#include "aios_crypto.h"

#include <esp_log.h>
#include <mbedtls/base64.h>

#define TAG "AiosCrypto"

namespace aios {

bool AiosCrypto::Initialize(const std::string& public_key_base64) {
    public_key_base64_ = public_key_base64;
    public_key_der_.clear();

    if (public_key_base64_.empty()) {
        ESP_LOGE(TAG, "AIOS public key is empty");
        initialized_ = false;
        return false;
    }

    size_t decoded_len = 0;
    int ret = mbedtls_base64_decode(nullptr, 0, &decoded_len,
                                    reinterpret_cast<const unsigned char*>(public_key_base64_.data()),
                                    public_key_base64_.size());
    if (ret != MBEDTLS_ERR_BASE64_BUFFER_TOO_SMALL && ret != 0) {
        ESP_LOGE(TAG, "Failed to validate AIOS public key: %d", ret);
        initialized_ = false;
        return false;
    }

    public_key_der_.resize(decoded_len);
    ret = mbedtls_base64_decode(public_key_der_.data(), public_key_der_.size(), &decoded_len,
                                reinterpret_cast<const unsigned char*>(public_key_base64_.data()),
                                public_key_base64_.size());
    if (ret != 0) {
        ESP_LOGE(TAG, "Failed to decode AIOS public key: %d", ret);
        public_key_der_.clear();
        initialized_ = false;
        return false;
    }

    public_key_der_.resize(decoded_len);

    initialized_ = true;
    return true;
}

bool AiosCrypto::EncryptRequestBody(const std::string& json, std::string& encrypted_key, std::string& encrypted_body) {
    if (!initialized_) {
        return false;
    }

    encrypted_key.clear();
    encrypted_body = json;
    return true;
}

bool AiosCrypto::DecryptResponseBody(const std::string& encrypted_body, const std::string& aes_key, std::string& plain_json) {
    (void)aes_key;
    if (!initialized_) {
        return false;
    }

    plain_json = encrypted_body;
    return true;
}

}  // namespace aios
