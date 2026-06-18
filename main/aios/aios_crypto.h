#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace aios {

class AiosCrypto {
public:
    AiosCrypto() = default;

    bool Initialize(const std::string& public_key_base64);
    bool EncryptRequestBody(const std::string& json, std::string& encrypted_key, std::string& encrypted_body);
    bool DecryptResponseBody(const std::string& encrypted_body, const std::string& aes_key, std::string& plain_json);

private:
    bool initialized_ = false;
    std::string public_key_base64_;
    std::vector<uint8_t> public_key_der_;
};

}  // namespace aios
