#pragma once

namespace aios {

inline constexpr char kEventSessionConnected[] = "session.connected";
inline constexpr char kEventConversationStarted[] = "conversation.started";
inline constexpr char kEventConversationCompleted[] = "conversation.completed";
inline constexpr char kEventTurnInterrupt[] = "turn.interrupt";
inline constexpr char kEventDeviceProfileReport[] = "device.profile.report";
inline constexpr char kEventDeviceStateUpdate[] = "device.state.update";
inline constexpr char kEventUpStreamStart[] = "up_stream.start";
inline constexpr char kEventUpStreamStop[] = "up_stream.stop";
inline constexpr char kEventToolExecuteRequest[] = "tool.execute.request";
inline constexpr char kEventToolExecuteCompleted[] = "tool.execute.completed";
inline constexpr char kEventToolExecuteFailed[] = "tool.execute.failed";

}  // namespace aios
