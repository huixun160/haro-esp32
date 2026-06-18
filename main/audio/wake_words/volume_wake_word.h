#ifndef _VOLUME_WAKE_WORD_H_
#define _VOLUME_WAKE_WORD_H_

#include "wake_word.h"
#include <string>

class VolumeWakeWord : public WakeWord {
public:
    VolumeWakeWord();
    ~VolumeWakeWord() override;
    
    bool Initialize(AudioCodec* codec, srmodel_list_t* models_list) override;
    void Feed(const std::vector<int16_t>& data) override;
    void OnWakeWordDetected(std::function<void(const std::string& wake_word)> callback) override;
    void Start() override;
    void Stop() override;
    size_t GetFeedSize() override;
    void EncodeWakeWordData() override;
    bool GetWakeWordOpus(std::vector<uint8_t>& opus) override;
    const std::string& GetLastDetectedWakeWord() const override;

private:
    float CalculateVolume(const std::vector<int16_t>& data);
    std::function<void(const std::string&)> on_wake_word_detected_;
    std::string wake_word_;
    bool is_running_;
};

#endif
