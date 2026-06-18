#include "aios_http_client.h"

#include "board.h"
#include "system_info.h"
#include "assets/lang_config.h"

#include <esp_log.h>

#define TAG "AiosHttpClient"

namespace aios {

bool AiosHttpClient::Initialize() {
    Settings settings("aios", false);
    credentials_ = settings.GetAiosCredentials();
    if (credentials_.device_user_id.empty()) {
        credentials_.device_user_id = Board::GetInstance().GetUuid();
    }

    initialized_ = crypto_.Initialize(CONFIG_AIOS_PUBLIC_KEY_BASE64);
    if (!initialized_) {
        ESP_LOGE(TAG, "Failed to initialize AIOS crypto");
        return false;
    }

    return true;
}

bool AiosHttpClient::RegisterIfNeeded() {
    if (!initialized_) {
        return false;
    }

    if (credentials_.device_user_id.empty()) {
        credentials_.device_user_id = Board::GetInstance().GetUuid();
    }

    return true;
}

std::unique_ptr<Http> AiosHttpClient::SetupHttp() {
    auto& board = Board::GetInstance();
    auto network = board.GetNetwork();
    if (network == nullptr) {
        ESP_LOGE(TAG, "Board network interface is not available");
        return nullptr;
    }

    auto http = network->CreateHttp(0);
    if (http == nullptr) {
        ESP_LOGE(TAG, "Failed to allocate AIOS HTTP client");
        return nullptr;
    }

    auto user_agent = SystemInfo::GetUserAgent();

    http->SetHeader("Device-Id", SystemInfo::GetMacAddress().c_str());
    http->SetHeader("Client-Id", board.GetUuid().c_str());
    http->SetHeader("X-Device-Id", credentials_.device_user_id.c_str());
    http->SetHeader("X-AIOS-Version", CONFIG_AIOS_WS_PROTOCOL_VERSION);
    if (!credentials_.token.empty()) {
        std::string authorization = credentials_.token;
        if (authorization.find(' ') == std::string::npos) {
            authorization = "Bearer " + authorization;
        }
        http->SetHeader("Authorization", authorization.c_str());
    }
    http->SetHeader("User-Agent", user_agent);
    http->SetHeader("Accept-Language", Lang::CODE);
    http->SetHeader("Content-Type", "application/json");

    return http;
}

bool AiosHttpClient::Auth() {
    if (!initialized_) {
        return false;
    }

    auto http = SetupHttp();
    return http != nullptr;
}

bool AiosHttpClient::Sync() {
    if (!initialized_) {
        return false;
    }

    auto http = SetupHttp();
    return http != nullptr;
}

}  // namespace aios
