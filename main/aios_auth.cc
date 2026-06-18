#include "aios_auth.h"

#include "board.h"
#include "settings.h"
#include "system_info.h"
#include "assets/lang_config.h"

#include <cJSON.h>
#include <esp_log.h>
#include <esp_random.h>
#include <mbedtls/aes.h>
#include <mbedtls/base64.h>
#include <mbedtls/ctr_drbg.h>
#include <mbedtls/entropy.h>
#include <mbedtls/pk.h>

#include <cstring>
#include <cstdlib>
#include <ctime>
#include <string>
#include <sys/time.h>
#include <vector>

#define TAG "AiosAuth"

#if defined(CONFIG_AIOS_API_BASE_URL)
#define AIOS_RUNTIME_ENABLED 1
#else
#define AIOS_RUNTIME_ENABLED 0
#endif

#if defined(CONFIG_AIOS_PUBLIC_KEY_B64)
#define AIOS_PUBLIC_KEY_CONFIG CONFIG_AIOS_PUBLIC_KEY_B64
#elif defined(CONFIG_AIOS_PUBLIC_KEY_BASE64)
#define AIOS_PUBLIC_KEY_CONFIG CONFIG_AIOS_PUBLIC_KEY_BASE64
#else
#define AIOS_PUBLIC_KEY_CONFIG ""
#endif

#ifndef CONFIG_AIOS_ACCESS_KEY
#define CONFIG_AIOS_ACCESS_KEY ""
#endif
#ifndef CONFIG_AIOS_ACCESS_SECRET
#define CONFIG_AIOS_ACCESS_SECRET ""
#endif
#ifndef CONFIG_AIOS_BOT_ID
#define CONFIG_AIOS_BOT_ID ""
#endif
#ifndef CONFIG_AIOS_API_KEY
#define CONFIG_AIOS_API_KEY ""
#endif
#ifndef CONFIG_AIOS_DEVICE_SN
#define CONFIG_AIOS_DEVICE_SN ""
#endif
#ifndef CONFIG_AIOS_REGION
#define CONFIG_AIOS_REGION "cn"
#endif
#ifndef CONFIG_AIOS_LANGUAGE
#define CONFIG_AIOS_LANGUAGE "zh-CN"
#endif

namespace {

bool Base64Decode(const std::string& in, std::vector<uint8_t>& out) {
    size_t out_len = 0;
    int ret = mbedtls_base64_decode(nullptr, 0, &out_len,
                                    reinterpret_cast<const unsigned char*>(in.data()), in.size());
    if (ret != MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL || out_len == 0) {
        return false;
    }
    out.resize(out_len);
    ret = mbedtls_base64_decode(out.data(), out.size(), &out_len,
                                reinterpret_cast<const unsigned char*>(in.data()), in.size());
    if (ret != 0) {
        out.clear();
        return false;
    }
    out.resize(out_len);
    return true;
}

bool Base64Encode(const uint8_t* in, size_t in_len, std::string& out) {
    size_t out_len = 0;
    int ret = mbedtls_base64_encode(nullptr, 0, &out_len, in, in_len);
    if (ret != MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL || out_len == 0) {
        return false;
    }
    std::vector<uint8_t> buffer(out_len);
    ret = mbedtls_base64_encode(buffer.data(), buffer.size(), &out_len, in, in_len);
    if (ret != 0) {
        return false;
    }
    out.assign(reinterpret_cast<const char*>(buffer.data()), out_len);
    return true;
}

std::vector<uint8_t> Pkcs7Pad(const std::string& plain) {
    std::vector<uint8_t> data(plain.begin(), plain.end());
    size_t pad = 16 - (data.size() % 16);
    data.insert(data.end(), pad, static_cast<uint8_t>(pad));
    return data;
}

bool Pkcs7Unpad(std::vector<uint8_t>& data) {
    if (data.empty() || (data.size() % 16) != 0) {
        return false;
    }
    uint8_t pad = data.back();
    if (pad == 0 || pad > 16 || pad > data.size()) {
        return false;
    }
    for (size_t i = data.size() - pad; i < data.size(); ++i) {
        if (data[i] != pad) {
            return false;
        }
    }
    data.resize(data.size() - pad);
    return true;
}

bool AesEcbEncrypt(const std::vector<uint8_t>& key,
                   const std::string& plain_json,
                   std::string& encrypted_b64) {
    if (key.size() != 16) {
        return false;
    }
    std::vector<uint8_t> padded = Pkcs7Pad(plain_json);
    std::vector<uint8_t> encrypted(padded.size());

    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    int ret = mbedtls_aes_setkey_enc(&aes, key.data(), 128);
    if (ret != 0) {
        mbedtls_aes_free(&aes);
        return false;
    }
    for (size_t i = 0; i < padded.size(); i += 16) {
        ret = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, padded.data() + i, encrypted.data() + i);
        if (ret != 0) {
            mbedtls_aes_free(&aes);
            return false;
        }
    }
    mbedtls_aes_free(&aes);
    return Base64Encode(encrypted.data(), encrypted.size(), encrypted_b64);
}

bool AesEcbDecrypt(const std::vector<uint8_t>& key,
                   const std::string& encrypted_b64,
                   std::string& plain_json) {
    if (key.size() != 16) {
        return false;
    }
    std::vector<uint8_t> encrypted;
    if (!Base64Decode(encrypted_b64, encrypted) || encrypted.empty() || (encrypted.size() % 16) != 0) {
        return false;
    }

    std::vector<uint8_t> plain(encrypted.size());
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    int ret = mbedtls_aes_setkey_dec(&aes, key.data(), 128);
    if (ret != 0) {
        mbedtls_aes_free(&aes);
        return false;
    }
    for (size_t i = 0; i < encrypted.size(); i += 16) {
        ret = mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_DECRYPT, encrypted.data() + i, plain.data() + i);
        if (ret != 0) {
            mbedtls_aes_free(&aes);
            return false;
        }
    }
    mbedtls_aes_free(&aes);

    if (!Pkcs7Unpad(plain)) {
        return false;
    }
    plain_json.assign(plain.begin(), plain.end());
    return true;
}

bool RsaEncryptAesKeyPkcs1(const std::string& public_key_b64,
                           const std::vector<uint8_t>& aes_key,
                           std::string& encrypted_key_b64) {
    std::vector<uint8_t> der;
    if (!Base64Decode(public_key_b64, der)) {
        return false;
    }

    mbedtls_pk_context pk;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_pk_init(&pk);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    const char* pers = "aios_rsa";
    int ret = mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                                    reinterpret_cast<const unsigned char*>(pers), strlen(pers));
    if (ret != 0) {
        mbedtls_ctr_drbg_free(&ctr_drbg);
        mbedtls_entropy_free(&entropy);
        mbedtls_pk_free(&pk);
        return false;
    }

    ret = mbedtls_pk_parse_public_key(&pk, der.data(), der.size());
    if (ret != 0) {
        mbedtls_ctr_drbg_free(&ctr_drbg);
        mbedtls_entropy_free(&entropy);
        mbedtls_pk_free(&pk);
        return false;
    }

    std::vector<uint8_t> encrypted(mbedtls_pk_get_len(&pk));
    size_t olen = 0;
    ret = mbedtls_pk_encrypt(&pk,
                             aes_key.data(), aes_key.size(),
                             encrypted.data(), &olen, encrypted.size(),
                             mbedtls_ctr_drbg_random, &ctr_drbg);
    if (ret != 0) {
        mbedtls_ctr_drbg_free(&ctr_drbg);
        mbedtls_entropy_free(&entropy);
        mbedtls_pk_free(&pk);
        return false;
    }

    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    mbedtls_pk_free(&pk);
    return Base64Encode(encrypted.data(), olen, encrypted_key_b64);
}

std::string JsonToString(cJSON* root) {
    char* text = cJSON_PrintUnformatted(root);
    if (text == nullptr) {
        return "";
    }
    std::string out(text);
    cJSON_free(text);
    return out;
}

std::string GetJsonString(cJSON* root, const char* key) {
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (cJSON_IsString(item)) {
        return item->valuestring;
    }
    return "";
}

std::string GetJsonNumberAsString(cJSON* root, const char* key) {
    cJSON* item = cJSON_GetObjectItem(root, key);
    if (cJSON_IsNumber(item)) {
        return std::to_string(static_cast<long long>(item->valuedouble));
    }
    return "";
}

bool SyncSystemTimeFromHttpDate(Http* http) {
    if (http == nullptr) {
        return false;
    }

    std::string date_header = http->GetResponseHeader("Date");
    if (date_header.empty()) {
        return false;
    }

    struct tm tm_value = {};
    if (strptime(date_header.c_str(), "%a, %d %b %Y %H:%M:%S GMT", &tm_value) == nullptr) {
        return false;
    }

    const char* old_tz = getenv("TZ");
    std::string saved_tz = old_tz ? old_tz : "";
    setenv("TZ", "UTC0", 1);
    tzset();
    time_t parsed = mktime(&tm_value);
    if (saved_tz.empty()) {
        unsetenv("TZ");
    } else {
        setenv("TZ", saved_tz.c_str(), 1);
    }
    tzset();
    if (parsed <= 0) {
        return false;
    }

    time_t now = time(nullptr);
    if (now >= 1735689600 && llabs(static_cast<long long>(now) - static_cast<long long>(parsed)) < 5) {
        return true;
    }

    struct timeval tv = {};
    tv.tv_sec = parsed;
    tv.tv_usec = 0;
    if (settimeofday(&tv, nullptr) != 0) {
        return false;
    }

    ESP_LOGI(TAG, "System time synced from HTTP Date: %s", date_header.c_str());
    return true;
}

bool EncryptedPostJson(const std::string& url,
                       const std::string& public_key,
                       const std::string& api_key,
                       std::string payload_json,
                       cJSON** root_out,
                       std::string& error_message) {
    std::vector<uint8_t> aes_key(16);
    esp_fill_random(aes_key.data(), aes_key.size());

    std::string encrypted_key_b64;
    if (!RsaEncryptAesKeyPkcs1(public_key, aes_key, encrypted_key_b64)) {
        error_message = "RSA encrypt AES key failed";
        return false;
    }

    std::string encrypted_body_b64;
    if (!AesEcbEncrypt(aes_key, payload_json, encrypted_body_b64)) {
        error_message = "AES encrypt payload failed";
        return false;
    }

    auto network = Board::GetInstance().GetNetwork();
    auto http = network->CreateHttp(0);
    http->SetHeader("Authorization", "Bearer " + encrypted_key_b64);
    http->SetHeader("X-Encryption-Data", "{\"key\":\"" + encrypted_key_b64 + "\"}");
    http->SetHeader("Content-Type", "application/json");
    if (!api_key.empty()) {
        http->SetHeader("X-API-Key", api_key);
    }
    http->SetHeader("User-Agent", SystemInfo::GetUserAgent());
    http->SetHeader("Accept-Language", Lang::CODE);
    http->SetContent(std::move(encrypted_body_b64));

    if (!http->Open("POST", url)) {
        error_message = "open endpoint failed";
        return false;
    }
    int status = http->GetStatusCode();
    SyncSystemTimeFromHttpDate(http.get());
    std::string response = http->ReadAll();
    http->Close();
    if (status != 200) {
        error_message = "http status " + std::to_string(status) + ", body=" + response;
        return false;
    }

    cJSON* root = cJSON_Parse(response.c_str());
    if (root == nullptr) {
        std::string decrypted;
        if (!AesEcbDecrypt(aes_key, response, decrypted)) {
            error_message = "response is neither plain json nor encrypted json";
            return false;
        }
        root = cJSON_Parse(decrypted.c_str());
    }
    if (root == nullptr) {
        error_message = "parse response json failed";
        return false;
    }
    *root_out = root;
    return true;
}

bool EncryptedPostJsonWithToken(const std::string& url,
                                const std::string& public_key,
                                const std::string& bearer_token,
                                std::string payload_json,
                                cJSON** root_out,
                                std::string& error_message) {
    std::vector<uint8_t> aes_key(16);
    esp_fill_random(aes_key.data(), aes_key.size());

    std::string encrypted_key_b64;
    if (!RsaEncryptAesKeyPkcs1(public_key, aes_key, encrypted_key_b64)) {
        error_message = "RSA encrypt AES key failed";
        return false;
    }

    std::string encrypted_body_b64;
    if (!AesEcbEncrypt(aes_key, payload_json, encrypted_body_b64)) {
        error_message = "AES encrypt payload failed";
        return false;
    }

    auto network = Board::GetInstance().GetNetwork();
    auto http = network->CreateHttp(0);
    http->SetHeader("Authorization", "Bearer " + bearer_token);
    http->SetHeader("X-Encryption-Data", "{\"key\":\"" + encrypted_key_b64 + "\"}");
    http->SetHeader("Content-Type", "application/json");
    http->SetHeader("User-Agent", SystemInfo::GetUserAgent());
    http->SetHeader("Accept-Language", Lang::CODE);
    http->SetContent(std::move(encrypted_body_b64));

    if (!http->Open("POST", url)) {
        error_message = "open endpoint failed";
        return false;
    }
    int status = http->GetStatusCode();
    SyncSystemTimeFromHttpDate(http.get());
    std::string response = http->ReadAll();
    http->Close();
    if (status != 200) {
        error_message = "http status " + std::to_string(status) + ", body=" + response;
        return false;
    }

    cJSON* root = cJSON_Parse(response.c_str());
    if (root == nullptr) {
        std::string decrypted;
        if (!AesEcbDecrypt(aes_key, response, decrypted)) {
            error_message = "response is neither plain json nor encrypted json";
            return false;
        }
        root = cJSON_Parse(decrypted.c_str());
    }
    if (root == nullptr) {
        error_message = "parse response json failed";
        return false;
    }
    *root_out = root;
    return true;
}

}  // namespace

bool AiosAuthClient::FetchWebsocketConfig(AiosWebsocketConfig& config, std::string& error_message) {
#if !AIOS_RUNTIME_ENABLED
    error_message = "AIOS server mode is disabled";
    return false;
#else
    Settings aios_settings("aios", true);
    std::string access_key = aios_settings.GetString("access_key");
    std::string access_secret = aios_settings.GetString("access_secret");
    if (access_key.empty()) {
        access_key = CONFIG_AIOS_ACCESS_KEY;
    }
    if (access_secret.empty()) {
        access_secret = CONFIG_AIOS_ACCESS_SECRET;
    }
    std::string api_base = CONFIG_AIOS_API_BASE_URL;
    std::string public_key = AIOS_PUBLIC_KEY_CONFIG;
    std::string bot_override = CONFIG_AIOS_BOT_ID;
    std::string api_key = CONFIG_AIOS_API_KEY;
    std::string sn = aios_settings.GetString("sn");
    if (sn.empty()) {
        sn = CONFIG_AIOS_DEVICE_SN;
    }
    if (sn.empty()) {
        sn = SystemInfo::GetMacAddress();
    }

    if (api_base.empty() || public_key.empty()) {
        error_message = "AIOS api base or public key is empty";
        return false;
    }

    std::string auth_url = api_base + "/device/auth";
    std::string register_url = api_base + "/device/register";

    auto build_auth_payload = [&](const std::string& key, const std::string& secret) -> std::string {
        cJSON* payload = cJSON_CreateObject();
        cJSON_AddStringToObject(payload, "access_key", key.c_str());
        cJSON_AddStringToObject(payload, "access_secret", secret.c_str());
        cJSON_AddStringToObject(payload, "imei", "");
        cJSON_AddStringToObject(payload, "sn", sn.c_str());
        cJSON_AddStringToObject(payload, "region", CONFIG_AIOS_REGION);
        cJSON_AddStringToObject(payload, "language", CONFIG_AIOS_LANGUAGE);
        if (!api_key.empty()) {
            cJSON_AddStringToObject(payload, "api_key", api_key.c_str());
        }
        std::string out = JsonToString(payload);
        cJSON_Delete(payload);
        return out;
    };

    auto run_auth = [&](cJSON** root_out) -> bool {
        if (access_key.empty() || access_secret.empty()) {
            error_message = "access key/secret is empty";
            return false;
        }
        std::string payload_json = build_auth_payload(access_key, access_secret);
        if (payload_json.empty()) {
            error_message = "build auth payload json failed";
            return false;
        }
        ESP_LOGI(TAG, "Calling AIOS auth endpoint: %s", auth_url.c_str());
        return EncryptedPostJson(auth_url, public_key, api_key, std::move(payload_json), root_out, error_message);
    };

    cJSON* root = nullptr;
    bool auth_success = run_auth(&root);
    cJSON* code = root ? cJSON_GetObjectItem(root, "code") : nullptr;
    bool need_register = false;

    if (!auth_success) {
        if (error_message == "access key/secret is empty") {
            need_register = true;
        } else {
            return false;
        }
    } else if (!cJSON_IsNumber(code)) {
        std::string raw = JsonToString(root);
        cJSON_Delete(root);
        error_message = "auth response code invalid: " + raw;
        return false;
    } else if (code->valueint != 200) {
        need_register = true;
    }

    if (need_register) {
        // Auth failed (e.g. stale key), try register once and auth again.
        if (root) {
            cJSON_Delete(root);
            root = nullptr;
        }
        cJSON* register_payload = cJSON_CreateObject();
        cJSON_AddNumberToObject(register_payload, "device_product_id", CONFIG_AIOS_DEVICE_PRODUCT_ID);
        cJSON_AddNumberToObject(register_payload, "tenant_user_id", CONFIG_AIOS_TENANT_USER_ID);
        cJSON_AddStringToObject(register_payload, "sn", sn.c_str());
        if (!api_key.empty()) {
            cJSON_AddStringToObject(register_payload, "api_key", api_key.c_str());
        }
        std::string register_payload_json = JsonToString(register_payload);
        cJSON_Delete(register_payload);
        if (register_payload_json.empty()) {
            error_message = "build register payload json failed";
            return false;
        }
        ESP_LOGW(TAG, "AIOS auth rejected current key, trying register endpoint: %s", register_url.c_str());
        if (!EncryptedPostJson(register_url, public_key, api_key, std::move(register_payload_json), &root, error_message)) {
            return false;
        }

        cJSON* register_code = cJSON_GetObjectItem(root, "code");
        cJSON* register_data = cJSON_GetObjectItem(root, "data");
        cJSON* device = register_data ? cJSON_GetObjectItem(register_data, "device") : nullptr;
        if (!cJSON_IsNumber(register_code) || register_code->valueint != 200 || !cJSON_IsObject(device)) {
            std::string raw = JsonToString(root);
            cJSON_Delete(root);
            error_message = "register failed: " + raw;
            return false;
        }
        access_key = GetJsonString(device, "access_key");
        access_secret = GetJsonString(device, "access_secret");
        cJSON_Delete(root);
        root = nullptr;
        if (access_key.empty() || access_secret.empty()) {
            error_message = "register succeeded but access_key/access_secret missing";
            return false;
        }
        aios_settings.SetString("access_key", access_key);
        aios_settings.SetString("access_secret", access_secret);
        aios_settings.SetString("sn", sn);

        if (!run_auth(&root)) {
            return false;
        }
        code = cJSON_GetObjectItem(root, "code");
        if (!cJSON_IsNumber(code) || code->valueint != 200) {
            std::string raw = JsonToString(root);
            cJSON_Delete(root);
            error_message = "auth after register failed: " + raw;
            return false;
        }
    }

    cJSON* data = cJSON_GetObjectItem(root, "data");
    if (!cJSON_IsObject(data)) {
        std::string raw = JsonToString(root);
        cJSON_Delete(root);
        error_message = "auth response missing data: " + raw;
        return false;
    }

    cJSON* user = cJSON_GetObjectItem(data, "user");
    cJSON* ws = cJSON_GetObjectItem(data, "ws");
    cJSON* profile = cJSON_GetObjectItem(data, "profile_device");
    if (!cJSON_IsObject(user) || !cJSON_IsObject(ws) || !cJSON_IsObject(profile)) {
        cJSON_Delete(root);
        error_message = "auth response missing user/ws/profile_device";
        return false;
    }

    config.url = GetJsonString(ws, "url");
    config.token = GetJsonString(user, "token");
    config.device_id = GetJsonNumberAsString(user, "id");
    config.user_id = config.device_id;
    config.bot_id = bot_override.empty() ? GetJsonString(profile, "config_agentic_id") : bot_override;
    if (config.bot_id.empty()) {
        config.bot_id = aios_settings.GetString("bot_id");
    }
    cJSON_Delete(root);

    if (config.url.empty() || config.token.empty() || config.device_id.empty() || config.bot_id.empty()) {
        error_message = "auth response has empty ws url/token/device_id/bot_id";
        return false;
    }
    aios_settings.SetString("sn", sn);
    aios_settings.SetString("bot_id", config.bot_id);
    return true;
#endif
}

bool AiosAuthClient::SyncDevice(const std::string& token, std::string& error_message) {
#if !AIOS_RUNTIME_ENABLED
    error_message = "AIOS server mode is disabled";
    return false;
#else
    if (token.empty()) {
        error_message = "sync token is empty";
        return false;
    }

    std::string api_base = CONFIG_AIOS_API_BASE_URL;
    std::string public_key = AIOS_PUBLIC_KEY_CONFIG;
    if (api_base.empty() || public_key.empty()) {
        error_message = "AIOS api base or public key is empty";
        return false;
    }

    std::string sync_url = api_base + "/device/sync";
    cJSON* root = nullptr;
    ESP_LOGI(TAG, "Calling AIOS sync endpoint: %s", sync_url.c_str());
    if (!EncryptedPostJsonWithToken(sync_url, public_key, token, "{}", &root, error_message)) {
        return false;
    }

    cJSON* code = cJSON_GetObjectItem(root, "code");
    if (!cJSON_IsNumber(code) || code->valueint != 200) {
        std::string raw = JsonToString(root);
        cJSON_Delete(root);
        error_message = "sync failed: " + raw;
        return false;
    }

    ESP_LOGI(TAG, "AIOS sync succeeded");
    cJSON_Delete(root);
    return true;
#endif
}
