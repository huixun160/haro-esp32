#ifndef AIOS_AUTH_H_
#define AIOS_AUTH_H_

#include <string>

struct AiosWebsocketConfig {
    std::string url;
    std::string token;
    std::string device_id;
    std::string user_id;
    std::string bot_id;
    std::string version = "3.0";
};

class AiosAuthClient {
public:
    bool FetchWebsocketConfig(AiosWebsocketConfig& config, std::string& error_message);
    bool SyncDevice(const std::string& token, std::string& error_message);
};

#endif  // AIOS_AUTH_H_
