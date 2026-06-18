#include "aios_runtime_metrics.h"

#include <utility>

#include "aios_event_types.h"
#include "system_info.h"

namespace aios {

static_assert(kEventSessionConnected[0] == 's');

void AiosRuntimeMetrics::SetWebsocketConnected(bool connected) {
    snapshot_.websocket_connected = connected;
}

void AiosRuntimeMetrics::SetSessionConnected(bool connected) {
    snapshot_.session_connected = connected;
}

void AiosRuntimeMetrics::SetAudioSendQueueDepth(int depth) {
    snapshot_.audio_send_queue_depth = depth;
}

void AiosRuntimeMetrics::SetAudioDecodeQueueDepth(int depth) {
    snapshot_.audio_decode_queue_depth = depth;
}

void AiosRuntimeMetrics::SetAudioPlaybackQueueDepth(int depth) {
    snapshot_.audio_playback_queue_depth = depth;
}

void AiosRuntimeMetrics::SetDeviceState(std::string device_state) {
    snapshot_.device_state = std::move(device_state);
}

const AiosRuntimeSnapshot& AiosRuntimeMetrics::snapshot() const {
    return snapshot_;
}

AiosRuntimeSnapshot AiosRuntimeMetrics::Snapshot() const {
    return snapshot_;
}

void AiosRuntimeMetrics::PublishSnapshot() {
    RefreshSnapshot();
}

void AiosRuntimeMetrics::RefreshSnapshot() {
    snapshot_.free_heap = SystemInfo::GetFreeHeapSize();
    snapshot_.min_free_heap = SystemInfo::GetMinimumFreeHeapSize();
}

}  // namespace aios
