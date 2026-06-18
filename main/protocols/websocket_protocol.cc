#include "websocket_protocol.h"
#include "aios_auth.h"
#include "board.h"
#include "system_info.h"
#include "application.h"
#include "settings.h"

#include <cstring>
#include <initializer_list>
#include <ctime>
#include <cJSON.h>
#include <esp_log.h>
#include <arpa/inet.h>
#include "assets/lang_config.h"
#include <inttypes.h>

#define TAG "WS"

WebsocketProtocol::WebsocketProtocol() {
    event_group_handle_ = xEventGroupCreate();
}

WebsocketProtocol::~WebsocketProtocol() {
    vEventGroupDelete(event_group_handle_);
}

bool WebsocketProtocol::Start() {
    // Only connect to server when audio channel is needed
    return true;
}

bool WebsocketProtocol::SendAudio(std::unique_ptr<AudioStreamPacket> packet) {
    if (websocket_ == nullptr || !websocket_->IsConnected()) {
        return false;
    }

    if (aios_mode_) {
        bool ok = websocket_->Send(packet->payload.data(), packet->payload.size(), true);
        if (ok) {
            aios_audio_packet_count_++;
            aios_audio_bytes_sent_ += packet->payload.size();
            if (aios_audio_packet_count_ == 1 || (aios_audio_packet_count_ % 50) == 0) {
                ESP_LOGI(TAG, "AIOS audio sent: packets=%" PRIu32 ", bytes=%u, last_frame=%u",
                         aios_audio_packet_count_,
                         static_cast<unsigned>(aios_audio_bytes_sent_),
                         static_cast<unsigned>(packet->payload.size()));
            }
        }
        return ok;
    } else if (version_ == 2) {
        std::string serialized;
        serialized.resize(sizeof(BinaryProtocol2) + packet->payload.size());
        auto bp2 = (BinaryProtocol2*)serialized.data();
        bp2->version = htons(version_);
        bp2->type = 0;
        bp2->reserved = 0;
        bp2->timestamp = htonl(packet->timestamp);
        bp2->payload_size = htonl(packet->payload.size());
        memcpy(bp2->payload, packet->payload.data(), packet->payload.size());

        return websocket_->Send(serialized.data(), serialized.size(), true);
    } else if (version_ == 3) {
        std::string serialized;
        serialized.resize(sizeof(BinaryProtocol3) + packet->payload.size());
        auto bp3 = (BinaryProtocol3*)serialized.data();
        bp3->type = 0;
        bp3->reserved = 0;
        bp3->payload_size = htons(packet->payload.size());
        memcpy(bp3->payload, packet->payload.data(), packet->payload.size());

        return websocket_->Send(serialized.data(), serialized.size(), true);
    } else {
        return websocket_->Send(packet->payload.data(), packet->payload.size(), true);
    }
}

void WebsocketProtocol::SendWakeWordDetected(const std::string& wake_word) {
    (void)wake_word;
    if (aios_mode_) {
        // AIOS v3 uses up_stream.start/stop for turn control.
        return;
    }
    Protocol::SendWakeWordDetected(wake_word);
}

void WebsocketProtocol::SendStartListening(ListeningMode mode) {
    (void)mode;
    if (aios_mode_) {
        aios_audio_packet_count_ = 0;
        aios_audio_bytes_sent_ = 0;
        aios_audio_stream_started_ = true;
        ESP_LOGI(TAG, "AIOS mode=vad, skip up_stream.start");
        return;
    }
    Protocol::SendStartListening(mode);
}

void WebsocketProtocol::SendStopListening() {
    if (aios_mode_) {
        if (aios_audio_stream_started_) {
            ESP_LOGI(TAG, "AIOS audio summary: packets=%" PRIu32 ", bytes=%u",
                     aios_audio_packet_count_, static_cast<unsigned>(aios_audio_bytes_sent_));
            ESP_LOGI(TAG, "AIOS mode=vad, skip up_stream.stop");
            aios_audio_stream_started_ = false;
            aios_stream_id_.clear();
        }
        return;
    }
    Protocol::SendStopListening();
}

void WebsocketProtocol::SendAbortSpeaking(AbortReason reason) {
    (void)reason;
    if (aios_mode_) {
        auto message = BuildAiosConversationCancel();
        if (!message.empty()) {
            ESP_LOGI(TAG, "AIOS send: conversation.cancel");
            SendText(message);
        }
        return;
    }
    Protocol::SendAbortSpeaking(reason);
}

bool WebsocketProtocol::SendText(const std::string& text) {
    if (websocket_ == nullptr || !websocket_->IsConnected()) {
        return false;
    }

    if (!websocket_->Send(text)) {
        ESP_LOGE(TAG, "Failed to send text: %s", text.c_str());
        SetError(Lang::Strings::SERVER_ERROR);
        return false;
    }

    return true;
}

bool WebsocketProtocol::IsAudioChannelOpened() const {
    return websocket_ != nullptr && websocket_->IsConnected() && !error_occurred_ && !IsTimeout();
}

void WebsocketProtocol::CloseAudioChannel(bool send_goodbye) {
    (void)send_goodbye;  // Websocket doesn't need to send goodbye message
    if (websocket_ == nullptr) {
        return;
    }
    closing_audio_channel_.store(true);
    websocket_->Close();
    websocket_.reset();
    closing_audio_channel_.store(false);
}

bool WebsocketProtocol::OpenAudioChannel() {
    Settings settings("websocket", false);
    std::string url = settings.GetString("url");
    std::string token = settings.GetString("token");
    auto get_first_non_empty = [&settings](std::initializer_list<const char*> keys, const std::string& default_value = "") -> std::string {
        for (const char* key : keys) {
            auto value = settings.GetString(key);
            if (!value.empty()) {
                return value;
            }
        }
        return default_value;
    };
    auto aios_device_id = get_first_non_empty({"x-device-id", "x_device_id", "device_id", "aios-device-user-id", "user_id"});
    auto aios_user_id = get_first_non_empty({"x-user-id", "x_user_id", "user_id", "aios-device-user-id"});
    auto aios_bot_id = get_first_non_empty({"x-bot-id", "x_bot_id", "bot_id", "config_agentic_id"});
#ifdef CONFIG_AIOS_BOT_ID
    if (aios_bot_id.empty() && strlen(CONFIG_AIOS_BOT_ID) > 0) {
        aios_bot_id = CONFIG_AIOS_BOT_ID;
    }
#endif
    auto aios_version = get_first_non_empty({"x-aios-version", "x_aios_version", "aios_version"}, "3.0");
    auto aios_down_format = get_first_non_empty({"aios-down-format", "aios_down_format"}, "pcm");
    bool force_aios_mode = settings.GetBool("aios_mode", false) || settings.GetBool("use_aios_headers", false);
    aios_mode_ = force_aios_mode || !aios_bot_id.empty();
    aios_downstream_pcm_ = (aios_down_format != "opus");
    int default_downstream_sample_rate = 16000;
    auto codec = Board::GetInstance().GetAudioCodec();
    if (codec != nullptr && codec->output_sample_rate() > 0) {
        default_downstream_sample_rate = codec->output_sample_rate();
    }
    aios_downstream_sample_rate_ = settings.GetInt("aios-down-sample-rate", default_downstream_sample_rate);
    if (aios_downstream_sample_rate_ <= 0) {
        aios_downstream_sample_rate_ = 16000;
    }

    int version = settings.GetInt("version");
    if (version != 0) {
        version_ = version;
    }

    error_occurred_ = false;
    session_id_.clear();
    aios_sync_completed_ = false;
    aios_audio_stream_started_ = false;
    aios_stream_id_.clear();
    aios_audio_packet_count_ = 0;
    aios_audio_bytes_sent_ = 0;
    xEventGroupClearBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);

    auto network = Board::GetInstance().GetNetwork();
    websocket_ = network->CreateWebSocket(1);
    if (websocket_ == nullptr) {
        ESP_LOGE(TAG, "Failed to create websocket");
        return false;
    }

    if (!token.empty()) {
        // If token not has a space, add "Bearer " prefix
        if (token.find(" ") == std::string::npos) {
            token = "Bearer " + token;
        }
        websocket_->SetHeader("Authorization", token.c_str());
    }
    if (aios_mode_) {
        if (aios_device_id.empty()) {
            aios_device_id = SystemInfo::GetMacAddress();
        }
        ESP_LOGI(TAG, "AIOS downstream audio format=%s sample_rate=%d",
                 aios_downstream_pcm_ ? "pcm" : "opus", aios_downstream_sample_rate_);
        websocket_->SetHeader("X-Device-Id", aios_device_id.c_str());
        websocket_->SetHeader("X-AIOS-Version", aios_version.c_str());
        if (!aios_user_id.empty()) {
            websocket_->SetHeader("X-User-ID", aios_user_id.c_str());
        }
        if (!aios_bot_id.empty()) {
            websocket_->SetHeader("X-Bot-ID", aios_bot_id.c_str());
        } else {
            ESP_LOGW(TAG, "AIOS mode enabled but X-Bot-ID is empty");
        }
    }

    // Keep legacy headers for backward compatibility with non-AIOS websocket servers.
    websocket_->SetHeader("Protocol-Version", std::to_string(version_).c_str());
    websocket_->SetHeader("Device-Id", SystemInfo::GetMacAddress().c_str());
    websocket_->SetHeader("Client-Id", Board::GetInstance().GetUuid().c_str());

    websocket_->OnData([this](const char* data, size_t len, bool binary) {
        if (binary) {
            if (on_incoming_audio_ != nullptr) {
                if (aios_mode_) {
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = aios_downstream_sample_rate_,
                        .frame_duration = 60,
                        .timestamp = 0,
                        .format = aios_downstream_pcm_ ? AudioStreamPacket::PayloadFormat::PCM_S16LE
                                                       : AudioStreamPacket::PayloadFormat::OPUS,
                        .payload = std::vector<uint8_t>((uint8_t*)data, (uint8_t*)data + len)
                    }));
                    return;
                }
                if (version_ == 2) {
                    BinaryProtocol2* bp2 = (BinaryProtocol2*)data;
                    bp2->version = ntohs(bp2->version);
                    bp2->type = ntohs(bp2->type);
                    bp2->timestamp = ntohl(bp2->timestamp);
                    bp2->payload_size = ntohl(bp2->payload_size);
                    auto payload = (uint8_t*)bp2->payload;
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = bp2->timestamp,
                        .payload = std::vector<uint8_t>(payload, payload + bp2->payload_size)
                    }));
                } else if (version_ == 3) {
                    BinaryProtocol3* bp3 = (BinaryProtocol3*)data;
                    bp3->type = bp3->type;
                    bp3->payload_size = ntohs(bp3->payload_size);
                    auto payload = (uint8_t*)bp3->payload;
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = 0,
                        .payload = std::vector<uint8_t>(payload, payload + bp3->payload_size)
                    }));
                } else {
                    on_incoming_audio_(std::make_unique<AudioStreamPacket>(AudioStreamPacket{
                        .sample_rate = server_sample_rate_,
                        .frame_duration = server_frame_duration_,
                        .timestamp = 0,
                        .payload = std::vector<uint8_t>((uint8_t*)data, (uint8_t*)data + len)
                    }));
                }
            }
        } else {
            // Parse JSON data
            auto root = cJSON_Parse(data);
            if (root == nullptr) {
                ESP_LOGE(TAG, "Failed to parse JSON message: %.*s", (int)len, data);
            } else {
                auto type = cJSON_GetObjectItem(root, "type");
                auto event_type = cJSON_GetObjectItem(root, "event_type");
                if (cJSON_IsString(type)) {
                    if (strcmp(type->valuestring, "hello") == 0) {
                        ParseServerHello(root);
                    } else if (on_incoming_json_ != nullptr) {
                        on_incoming_json_(root);
                    }
                } else if (cJSON_IsString(event_type)) {
                    if (strcmp(event_type->valuestring, "session.connected") == 0) {
                        xEventGroupSetBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);
                    }
                    if (on_incoming_json_ != nullptr) {
                        on_incoming_json_(root);
                    }
                } else {
                    ESP_LOGE(TAG, "Missing message type/event_type, data: %s", data);
                }
                cJSON_Delete(root);
            }
        }
        last_incoming_time_ = std::chrono::steady_clock::now();
    });

    websocket_->OnDisconnected([this]() {
        ESP_LOGI(TAG, "Websocket disconnected");
        if (closing_audio_channel_.load()) {
            ESP_LOGI(TAG, "Ignore websocket disconnected callback while closing audio channel");
            return;
        }
        if (on_audio_channel_closed_ != nullptr) {
            on_audio_channel_closed_();
        }
    });

    ESP_LOGI(TAG, "Connecting to websocket server: %s with version: %d", url.c_str(), version_);
    if (!websocket_->Connect(url.c_str())) {
        ESP_LOGE(TAG, "Failed to connect to websocket server, code=%d", websocket_->GetLastError());
        SetError(Lang::Strings::SERVER_NOT_CONNECTED);
        return false;
    }

    if (!aios_mode_) {
        // Legacy websocket servers require a hello exchange.
        auto message = GetHelloMessage();
        if (!SendText(message)) {
            return false;
        }
    }

    // Wait for either legacy server hello or AIOS session.connected event.
    EventBits_t bits = xEventGroupWaitBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT, pdTRUE, pdFALSE, pdMS_TO_TICKS(10000));
    if (!(bits & WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT)) {
        ESP_LOGE(TAG, "Failed to receive websocket ready event");
        SetError(Lang::Strings::SERVER_TIMEOUT);
        return false;
    }

    if (aios_mode_) {
        Settings settings("websocket", false);
        std::string raw_token = settings.GetString("token");
        if (!raw_token.empty() && raw_token.rfind("Bearer ", 0) == 0) {
            raw_token = raw_token.substr(strlen("Bearer "));
        }
        if (!raw_token.empty()) {
            AiosAuthClient aios_auth;
            std::string sync_error;
            if (!aios_auth.SyncDevice(raw_token, sync_error)) {
                ESP_LOGW(TAG, "AIOS device sync failed: %s", sync_error.c_str());
            } else {
                aios_sync_completed_ = true;
            }
        } else {
            ESP_LOGW(TAG, "AIOS sync skipped because token is empty");
        }

        auto profile_message = BuildAiosProfileReport();
        if (!profile_message.empty()) {
            ESP_LOGI(TAG, "AIOS send: device.profile.report %s", profile_message.c_str());
            SendText(profile_message);
        }
    }

    if (on_audio_channel_opened_ != nullptr) {
        on_audio_channel_opened_();
    }

    return true;
}

std::string WebsocketProtocol::BuildAiosProfileReport() {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "event_type", "device.profile.report");
    cJSON_AddNumberToObject(root, "timestamp", static_cast<double>(time(nullptr)));

    cJSON* data = cJSON_CreateObject();
    cJSON* identity = cJSON_CreateObject();
    cJSON_AddStringToObject(identity, "product_id", BOARD_NAME);
    cJSON_AddStringToObject(identity, "soft_ver", "3.0");
    cJSON_AddItemToObject(data, "identity", identity);

    cJSON* audio = cJSON_CreateObject();
    cJSON* up = cJSON_CreateObject();
    cJSON_AddStringToObject(up, "format", "opus");
    cJSON_AddNumberToObject(up, "sample_rate", 16000);
    cJSON_AddStringToObject(up, "audio_encode", "binary");
    cJSON* down = cJSON_CreateObject();
    cJSON_AddStringToObject(down, "format", aios_downstream_pcm_ ? "pcm" : "opus");
    cJSON_AddNumberToObject(down, "sample_rate", aios_downstream_sample_rate_);
    cJSON_AddStringToObject(down, "audio_encode", "binary");
    cJSON_AddItemToObject(audio, "up", up);
    cJSON_AddItemToObject(audio, "down", down);
    cJSON_AddItemToObject(data, "audio", audio);

    cJSON* language = cJSON_CreateObject();
    cJSON_AddStringToObject(language, "src", Lang::CODE);
    cJSON_AddStringToObject(language, "tgt", Lang::CODE);
    cJSON_AddItemToObject(data, "language", language);
    cJSON_AddStringToObject(data, "mode", "vad");

    cJSON_AddItemToObject(root, "data", data);
    char* text = cJSON_PrintUnformatted(root);
    std::string out = text ? text : "";
    if (text) {
        cJSON_free(text);
    }
    cJSON_Delete(root);
    return out;
}

std::string WebsocketProtocol::BuildAiosUpStreamStart() {
    int64_t ts = static_cast<int64_t>(time(nullptr));
    if (aios_stream_id_.empty()) {
        aios_stream_id_ = GenerateAiosStreamId();
    }

    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "event_type", "up_stream.start");
    cJSON_AddNumberToObject(root, "timestamp", static_cast<double>(ts));
    cJSON* data = cJSON_CreateObject();
    cJSON_AddStringToObject(data, "type", "audio");
    cJSON_AddStringToObject(data, "stream_id", aios_stream_id_.c_str());
    cJSON* metadata = cJSON_CreateObject();
    cJSON_AddStringToObject(metadata, "format", "opus");
    cJSON_AddNumberToObject(metadata, "sample_rate", 16000);
    cJSON_AddStringToObject(metadata, "audio_encode", "binary");
    cJSON_AddNumberToObject(metadata, "channels", 1);
    cJSON_AddItemToObject(data, "metadata", metadata);
    cJSON_AddItemToObject(root, "data", data);
    char* text = cJSON_PrintUnformatted(root);
    std::string out = text ? text : "";
    if (text) {
        cJSON_free(text);
    }
    cJSON_Delete(root);
    return out;
}

std::string WebsocketProtocol::GenerateAiosStreamId() {
    time_t now = time(nullptr);
    if (now <= last_aios_stream_id_second_) {
        now = last_aios_stream_id_second_ + 1;
    }
    last_aios_stream_id_second_ = now;

    struct tm time_info = {};
    localtime_r(&now, &time_info);

    char buffer[32] = {0};
    strftime(buffer, sizeof(buffer), "%Y%m%d%H%M%S", &time_info);
    return std::string(buffer);
}

std::string WebsocketProtocol::BuildAiosUpStreamStop() {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "event_type", "up_stream.stop");
    cJSON_AddNumberToObject(root, "timestamp", static_cast<double>(time(nullptr)));
    cJSON* data = cJSON_CreateObject();
    if (!aios_stream_id_.empty()) {
        cJSON_AddStringToObject(data, "stream_id", aios_stream_id_.c_str());
    }
    cJSON_AddItemToObject(root, "data", data);
    char* text = cJSON_PrintUnformatted(root);
    std::string out = text ? text : "";
    if (text) {
        cJSON_free(text);
    }
    cJSON_Delete(root);
    return out;
}

std::string WebsocketProtocol::BuildAiosConversationCancel() {
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "event_type", "conversation.cancel");
    cJSON_AddNumberToObject(root, "timestamp", static_cast<double>(time(nullptr)));
    char* text = cJSON_PrintUnformatted(root);
    std::string out = text ? text : "";
    if (text) {
        cJSON_free(text);
    }
    cJSON_Delete(root);
    return out;
}

std::string WebsocketProtocol::GetHelloMessage() {
    // keys: message type, version, audio_params (format, sample_rate, channels)
    cJSON* root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "type", "hello");
    cJSON_AddNumberToObject(root, "version", version_);
    cJSON* features = cJSON_CreateObject();
#if CONFIG_USE_SERVER_AEC
    cJSON_AddBoolToObject(features, "aec", true);
#endif
    cJSON_AddBoolToObject(features, "mcp", true);
    cJSON_AddItemToObject(root, "features", features);
    cJSON_AddStringToObject(root, "transport", "websocket");
    cJSON* audio_params = cJSON_CreateObject();
    cJSON_AddStringToObject(audio_params, "format", "opus");
    cJSON_AddNumberToObject(audio_params, "sample_rate", 16000);
    cJSON_AddNumberToObject(audio_params, "channels", 1);
    cJSON_AddNumberToObject(audio_params, "frame_duration", OPUS_FRAME_DURATION_MS);
    cJSON_AddItemToObject(root, "audio_params", audio_params);
    auto json_str = cJSON_PrintUnformatted(root);
    std::string message(json_str);
    cJSON_free(json_str);
    cJSON_Delete(root);
    return message;
}

void WebsocketProtocol::ParseServerHello(const cJSON* root) {
    auto transport = cJSON_GetObjectItem(root, "transport");
    if (!cJSON_IsString(transport) || strcmp(transport->valuestring, "websocket") != 0) {
        ESP_LOGE(TAG, "Unsupported transport in server hello");
        return;
    }

    auto session_id = cJSON_GetObjectItem(root, "session_id");
    if (cJSON_IsString(session_id)) {
        session_id_ = session_id->valuestring;
        ESP_LOGI(TAG, "Session ID: %s", session_id_.c_str());
    }

    auto audio_params = cJSON_GetObjectItem(root, "audio_params");
    if (cJSON_IsObject(audio_params)) {
        auto sample_rate = cJSON_GetObjectItem(audio_params, "sample_rate");
        if (cJSON_IsNumber(sample_rate)) {
            server_sample_rate_ = sample_rate->valueint;
        }
        auto frame_duration = cJSON_GetObjectItem(audio_params, "frame_duration");
        if (cJSON_IsNumber(frame_duration)) {
            server_frame_duration_ = frame_duration->valueint;
        }
    }

    xEventGroupSetBits(event_group_handle_, WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT);
}
