#!/usr/bin/env python3
from pathlib import Path
import sys


def main() -> int:
    source = Path("main/application.cc").read_text(encoding="utf-8")
    marker = 'strcmp(event_type->valuestring, "turn.interrupt") == 0'
    start = source.find(marker)
    if start == -1:
        print("FAIL: turn.interrupt handler not found")
        return 1

    end_marker = '} else if (strcmp(event_type->valuestring, "conversation.completed") == 0) {'
    end = source.find(end_marker, start)
    if end == -1:
        print("FAIL: could not isolate turn.interrupt handler")
        return 1

    handler = source[start:end]

    failures = []
    if "SetDeviceState(kDeviceStateListening)" in handler:
        failures.append("turn.interrupt must not force state back to listening")
    if "EnableVoiceProcessing(true)" in handler:
        failures.append("turn.interrupt must not reopen upstream voice processing")
    if "audio_service_.ResetDecoder();" not in handler:
        failures.append("turn.interrupt must still stop current TTS playback by resetting decoder")
    if "tts_stream_finished_ = true;" not in handler:
        failures.append("turn.interrupt should mark current local TTS stream finished for later drain/completion")

    if failures:
        print("FAIL:")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("PASS: turn.interrupt handler keeps playback-stop semantics without reopening listening")
    return 0


if __name__ == "__main__":
    sys.exit(main())
