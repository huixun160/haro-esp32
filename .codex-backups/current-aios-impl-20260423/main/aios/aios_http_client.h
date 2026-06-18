#pragma once

#include <memory>
#include <string>

#include "aios_crypto.h"
#include "settings.h"

class Http;

namespace aios {

class AiosHttpClient {
public:
    AiosHttpClient() = default;

    bool Initialize();
    bool RegisterIfNeeded();
    bool Auth();
    bool Sync();

    const AiosCredentials& credentials() const { return credentials_; }

private:
    std::unique_ptr<Http> SetupHttp();

    AiosCredentials credentials_;
    AiosCrypto crypto_;
    bool initialized_ = false;
};

}  // namespace aios
