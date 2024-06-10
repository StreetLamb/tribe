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
    if (name === "ignore") continue
    messages.push({
      toolCalls: tool_calls || [],
      member: name,
      type,
      content,
      next,
    } as Message)
  }

  // If last message is a tool call, then next message should be to interrupt message
  if (messages.length > 0) {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.toolCalls && lastMessage.toolCalls.length > 0) {
      messages.push({
        type: "ai",
        content: "Proceed?",
        member: "Interrupt",
        interrupt: true
      })
    }
  }

  return messages
}
