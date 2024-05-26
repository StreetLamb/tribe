import type { Message, ToolInput } from "./components/Teams/ChatTeam"

export const emailPattern = {
  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
  message: "Invalid email address",
}

interface CheckpointMessage {
  kwargs: {
    tool_calls?: ToolInput[]
    name: string
    type: string
    content: string
    next?: string
  }
}

/**
 * Convert langgraph's checkpoint data to messages
 * @param checkpoint Checkpoint
 */
export const convertCheckpointToMessages = (checkpoint: any): Message[] => {
  const messages: Message[] = []

  for (const message of checkpoint.channel_values
    .messages as CheckpointMessage[]) {
    if (message.kwargs.type === "tool") continue
    const { type, content, next, tool_calls, name } = message.kwargs
    messages.push({
      toolCalls: tool_calls || [],
      member: type === "human" ? "You." : name,
      type,
      content,
      next,
    } as Message)
  }

  return messages
}
