#pragma once

#include <cstddef>
#include <cstdint>
#include <deque>
#include <string>

namespace aios {

struct AiosJournalEvent {
    int64_t timestamp_ms = 0;
    std::string type;
    std::string detail;
};

class AiosEventJournal {
public:
    explicit AiosEventJournal(size_t capacity = 32);

    void Push(std::string type, std::string detail = {});
    void Clear();
    size_t size() const;
    bool empty() const;
    std::deque<AiosJournalEvent> Events() const;

private:
    size_t capacity_ = 0;
    std::deque<AiosJournalEvent> events_;
};

}  // namespace aios
