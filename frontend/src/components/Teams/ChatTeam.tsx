import {
  Box,
  Container,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputRightElement,
  VStack,
} from "@chakra-ui/react"
import { VscSend } from "react-icons/vsc"
import {
  type TeamChat,
  type ApiError,
  OpenAPI,
  type OpenAPIConfig,
  type ChatMessage,
} from "../../client"
import { useMutation } from "react-query"
import useCustomToast from "../../hooks/useCustomToast"
import { useParams } from "@tanstack/react-router"
import { useState } from "react"
import {
  getQueryString,
  getRequestBody,
  getHeaders,
} from "../../client/core/request"
import type { ApiRequestOptions } from "../../client/core/ApiRequestOptions"
import Markdown from "react-markdown"
import { GrFormNextLink } from "react-icons/gr"

interface Message extends ChatMessage {
  member: string
  next?: string
}

const getUrl = (config: OpenAPIConfig, options: ApiRequestOptions): string => {
  const encoder = config.ENCODE_PATH || encodeURI

  const path = options.url
    .replace("{api-version}", config.VERSION)
    .replace(/{(.*?)}/g, (substring: string, group: string) => {
      // biome-ignore lint/suspicious/noPrototypeBuiltins: <explanation>
      if (options.path?.hasOwnProperty(group)) {
        return encoder(String(options.path[group]))
      }
      return substring
    })

  const url = `${config.BASE}${path}`
  if (options.query) {
    return `${url}${getQueryString(options.query)}`
  }
  return url
}

const stream = async (id: number, data: TeamChat) => {
  const requestOptions = {
    method: "POST" as const,
    url: "/api/v1/teams/{id}/stream",
    path: {
      id,
    },
    body: data,
    mediaType: "application/json",
    errors: {
      422: "Validation Error",
    },
  }
  const url = getUrl(OpenAPI, requestOptions)
  const body = getRequestBody(requestOptions)
  const headers = await getHeaders(OpenAPI, requestOptions)
  const res = await fetch(url, {
    method: requestOptions.method,
    headers,
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new Error(res.statusText)
  }

  return res
}

const MessageBox = ({ message }: { message: Message }) => {
  const memberName = message.member.slice(0, message.member.lastIndexOf("-"))
  const nextMemberName =
    message.next?.lastIndexOf("-") !== -1
      ? message.next?.slice(0, message.next?.lastIndexOf("-"))
      : message.next
  return (
    <VStack spacing={0} my={8}>
      <Container fontWeight={"bold"} display={"flex"} alignItems="center">
        {memberName}
        {nextMemberName && <Icon as={GrFormNextLink} mx={2} />}
        {nextMemberName && nextMemberName}
      </Container>
      <Container>
        <Markdown>{message.content}</Markdown>
      </Container>
    </VStack>
  )
}

const ChatTeam = () => {
  const { teamId } = useParams({ strict: false }) as { teamId: string }
  const showToast = useCustomToast()
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)

  const chatTeam = async (data: TeamChat) => {
    setMessages([])
    const res = await stream(Number.parseInt(teamId), data)

    if (res.body) {
      const reader = res.body.getReader()
      let done = false
      while (!done) {
        const { done: streamDone, value } = await reader.read()
        done = streamDone
        if (!done) {
          const chunk = new TextDecoder().decode(value).slice(5)
          const parsed = JSON.parse(chunk)
          const newMessages: Message[] = []
          for (const name in parsed) {
            if ("messages" in parsed[name]) {
              for (const message of parsed[name].messages) {
                newMessages.push({
                  type: message.type,
                  content: message.content,
                  member: name,
                })
              }
            } else if ("task" in parsed[name]) {
              for (const task of parsed[name].task) {
                newMessages.push({
                  type: task.type,
                  content: task.content,
                  member: name,
                  next: parsed[name].next,
                })
              }
            }
          }
          setMessages((prev) => [...prev, ...newMessages])
        }
      }
    }
    setIsStreaming(false)
  }

  const mutation = useMutation(chatTeam, {
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSuccess: () => {
      showToast("Success!", "Streaming completed.", "success")
    },
  })

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsStreaming(true)
    mutation.mutate({ messages: [{ type: "human", content: input }] })
  }

  return (
    <Box>
      <InputGroup as="form" onSubmit={onSubmit}>
        <Input
          type="text"
          placeholder="Ask your team a question"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <InputRightElement>
          <IconButton
            type="submit"
            icon={<VscSend />}
            aria-label="send-question"
            isLoading={isStreaming}
          />
        </InputRightElement>
      </InputGroup>
      <Box p={2}>
        {messages.map((message, index) => (
          <MessageBox key={index} message={message} />
        ))}
      </Box>
    </Box>
  )
}

export default ChatTeam
