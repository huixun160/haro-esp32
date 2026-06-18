#ifndef _WEBSOCKET_PROTOCOL_H_
#define _WEBSOCKET_PROTOCOL_H_


#include "protocol.h"

#include <web_socket.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <atomic>

#define WEBSOCKET_PROTOCOL_SERVER_HELLO_EVENT (1 << 0)

class WebsocketProtocol : public Protocol {
public:
    WebsocketProtocol();
    ~WebsocketProtocol();

    bool Start() override;
    bool SendAudio(std::unique_ptr<AudioStreamPacket> packet) override;
    void SendWakeWordDetected(const std::string& wake_word) override;
    void SendStartListening(ListeningMode mode) override;
    void SendStopListening() override;
    void SendAbortSpeaking(AbortReason reason) override;
    bool IsAiosMode() const override { return aios_mode_; }
    bool OpenAudioChannel() override;
    void CloseAudioChannel(bool send_goodbye = true) override;
    bool IsAudioChannelOpened() const override;

private:
    EventGroupHandle_t event_group_handle_;
    std::unique_ptr<WebSocket> websocket_;
    int version_ = 1;
    bool aios_mode_ = false;
    bool aios_audio_stream_started_ = false;
    bool aios_sync_completed_ = false;
    bool aios_downstream_pcm_ = true;
    int aios_downstream_sample_rate_ = 16000;
    std::atomic<bool> closing_audio_channel_{false};
    std::string aios_stream_id_;
    time_t last_aios_stream_id_second_ = 0;
    uint32_t aios_audio_packet_count_ = 0;
    size_t aios_audio_bytes_sent_ = 0;

    void ParseServerHello(const cJSON* root);
    std::string BuildAiosProfileReport();
    std::string BuildAiosUpStreamStart();
    std::string BuildAiosUpStreamStop();
    std::string BuildAiosConversationCancel();
    std::string GenerateAiosStreamId();
    bool SendText(const std::string& text) override;
    std::string GetHelloMessage();
};

#endif
