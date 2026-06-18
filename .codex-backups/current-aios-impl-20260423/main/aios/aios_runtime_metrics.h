#pragma once

#include <cstddef>
#include <string>

namespace aios {

struct AiosRuntimeSnapshot {
    size_t free_heap = 0;
    size_t min_free_heap = 0;
    bool websocket_connected = false;
    bool session_connected = false;
    int audio_send_queue_depth = 0;
    int audio_decode_queue_depth = 0;
    int audio_playback_queue_depth = 0;
    std::string device_state;
};

class AiosRuntimeMetrics {
public:
    AiosRuntimeMetrics() = default;

    void SetWebsocketConnected(bool connected);
    void SetSessionConnected(bool connected);
    void SetAudioSendQueueDepth(int depth);
    void SetAudioDecodeQueueDepth(int depth);
    void SetAudioPlaybackQueueDepth(int depth);
    void SetDeviceState(std::string device_state);

    const AiosRuntimeSnapshot& snapshot() const;
    AiosRuntimeSnapshot Snapshot() const;
    void PublishSnapshot();

private:
    void RefreshSnapshot();

    AiosRuntimeSnapshot snapshot_;
};

}  // namespace aios
