#include "volume_wake_word.h"
#include <cmath>
#include <esp_log.h>
#include "application.h"
#include "device_state_machine.h"

#define TAG "VolumeWakeWord"

// The user requested a "low decibel" wake up, meaning very sensitive.
// We lower the threshold from typical 40-50 down to 15.0.
#define VOLUME_THRESHOLD 15.0f

VolumeWakeWord::VolumeWakeWord() 
    : wake_word_("volume_trigger"), is_running_(false) {
}

VolumeWakeWord::~VolumeWakeWord() {
}

bool VolumeWakeWord::Initialize(AudioCodec* codec, srmodel_list_t* models_list) {
    ESP_LOGI(TAG, "VolumeWakeWord initialized with threshold %.1f", VOLUME_THRESHOLD);
    return true;
}

float VolumeWakeWord::CalculateVolume(const std::vector<int16_t>& data) {
    if (data.empty()) return 0.0f;
    
    int64_t sum_squares = 0;
    for (int16_t sample : data) {
        sum_squares += (int64_t)sample * sample;
    }
    float rms = std::sqrt(sum_squares / (float)data.size());
    return 20.0f * std::log10(rms + 1.0f);
}

void VolumeWakeWord::Feed(const std::vector<int16_t>& data) {
    if (!is_running_ || data.empty()) return;
    
    auto state = Application::GetInstance().GetDeviceState();
    if (state != kDeviceStateIdle && state != kDeviceStateSpeaking) {
        return;
    }
    
    float vol = CalculateVolume(data);
    
    if (vol > VOLUME_THRESHOLD) {
        ESP_LOGI(TAG, "Volume trigger! vol=%.1f > threshold=%.1f", vol, VOLUME_THRESHOLD);
        if (on_wake_word_detected_) {
            on_wake_word_detected_(wake_word_);
        }
    }
}

void VolumeWakeWord::OnWakeWordDetected(std::function<void(const std::string& wake_word)> callback) {
    on_wake_word_detected_ = callback;
}

void VolumeWakeWord::Start() {
    is_running_ = true;
}

void VolumeWakeWord::Stop() {
    is_running_ = false;
}

size_t VolumeWakeWord::GetFeedSize() {
    return 320; // Default feed size
}

void VolumeWakeWord::EncodeWakeWordData() {
    // No-op for volume wake word
}

bool VolumeWakeWord::GetWakeWordOpus(std::vector<uint8_t>& opus) {
    return false; // Not implemented
}

const std::string& VolumeWakeWord::GetLastDetectedWakeWord() const {
    return wake_word_;
}
