#include "aios_event_journal.h"

#include <utility>

#include "system_info.h"

namespace aios {

AiosEventJournal::AiosEventJournal(size_t capacity) : capacity_(capacity) {}

void AiosEventJournal::Push(std::string type, std::string detail) {
    if (capacity_ == 0) {
        return;
    }
    if (events_.size() >= capacity_) {
        events_.pop_front();
    }
    events_.push_back({SystemInfo::GetUptimeMs(), std::move(type), std::move(detail)});
}

void AiosEventJournal::Clear() {
    events_.clear();
}

size_t AiosEventJournal::size() const {
    return events_.size();
}

bool AiosEventJournal::empty() const {
    return events_.empty();
}

std::deque<AiosJournalEvent> AiosEventJournal::Events() const {
    return events_;
}

}  // namespace aios
