import {
  Box,
  Button,
  Container,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputRightElement,
  Tag,
  Tooltip,
  VStack,
  Wrap,
} from "@chakra-ui/react"
import { VscSend } from "react-icons/vsc"
import {
  type TeamChat,
  type ApiError,
  OpenAPI,
  type OpenAPIConfig,
  type ChatMessage,
  type ThreadUpdate,
  ThreadsService,
  type ThreadCreate,
} from "../../client"
import { useMutation, useQuery, useQueryClient } from "react-query"
import useCustomToast from "../../hooks/useCustomToast"
import { getRouteApi, useNavigate, useParams } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import {
  getQueryString,
  getRequestBody,
  getHeaders,
} from "../../client/core/request"
import type { ApiRequestOptions } from "../../client/core/ApiRequestOptions"
import Markdown from "react-markdown"
import { GrFormNextLink } from "react-icons/gr"
import { convertCheckpointToMessages } from "../../utils"
import { IoCreateOutline } from "react-icons/io5"

export interface ToolInput {
  name: string
  args: { [x: string]: any }
}

export interface Message extends ChatMessage {
  toolCalls?: ToolInput[]
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

const stream = async (id: number, threadId: string, data: TeamChat) => {
  const requestOptions = {
    method: "POST" as const,
    url: "/api/v1/teams/{id}/stream/{threadId}",
    path: {
      id,
      threadId,
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
  const { member, next, content, toolCalls } = message
  const hasTools = (toolCalls && toolCalls.length > 0) || false
  const memberComp =
    member === "user" ? (
      <Tag colorScheme="green" fontWeight={"bold"}>
        You
      </Tag>
    ) : member === "error" ? (
      <Tag colorScheme="red" fontWeight={"bold"}>
        Error
      </Tag>
    ) : (
      member
    )
  
  const isToolMessage = toolCalls && toolCalls.length > 0 || false
  return (
    <VStack spacing={0} my={8}>
      <Container fontWeight={"bold"} display={"flex"} alignItems="center">
        {memberComp}
        {next && <Icon as={GrFormNextLink} mx={2} />}
        {next && next}
        {hasTools && <Tag ml={4}>Tool</Tag>}
      </Container>
      <Container>
        <Wrap pt={2} gap={2}>
          {hasTools &&
            toolCalls?.map((toolCall, index) => (
              <Tooltip key={index} label={JSON.stringify(toolCall.args)}>
                <Tag>{toolCall.name}</Tag>
              </Tooltip>
            ))}
          {!isToolMessage && typeof content === "string" && <Markdown>{content}</Markdown>}
        </Wrap>
      </Container>
    </VStack>
  )
}

const ChatTeam = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { threadId } = getRouteApi("/_layout/teams/$teamId").useSearch()
  const { teamId } = useParams({ strict: false }) as { teamId: string }
  const showToast = useCustomToast()
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const threadData = useQuery(
    ["thread", threadId],
    () =>
      ThreadsService.readThread({
        teamId: Number.parseInt(teamId),
        id: threadId!,
      }),
    {
      // Only run the query if messages state is empty and threadId is not null or undefined.
      enabled: !!threadId,
      refetchOnWindowFocus: false,
      onError: (err: ApiError) => {
        const errDetail = err.body?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
        // if fail, then remove it from search params and delete existing messages
        navigate({ search: {} })
        setMessages([])
      },
    },
  )

  useEffect(() => {
    if (threadData.data?.last_checkpoint?.checkpoint) {
      const checkpoint = JSON.parse(
        threadData.data.last_checkpoint.checkpoint as unknown as string,
      )
      const messages = convertCheckpointToMessages(checkpoint)
      setMessages(messages)
    }
  }, [threadData.data])

  const createThread = async (data: ThreadCreate) => {
    const thread = await ThreadsService.createThread({
      teamId: Number.parseInt(teamId),
      requestBody: data,
    })
    return thread.id
  }
  const createThreadMutation = useMutation(createThread, {
    onSuccess: (threadId) => {
      navigate({ search: { threadId } })
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Unable to create thread", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries(["threads", teamId])
    },
  })

  const updateThread = async (data: ThreadUpdate) => {
    if (!threadId) return
    const thread = await ThreadsService.updateThread({
      teamId: Number.parseInt(teamId),
      id: threadId,
      requestBody: data,
    })
    return thread.id
  }
  const updateThreadMutation = useMutation(updateThread, {
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Unable to update thread.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries(["threads", teamId])
    },
  })

  const chatTeam = async (data: TeamChat) => {
    setMessages((prev) => [
      ...prev,
      {
        type: "human",
        content: data.messages[0].content,
        member: "user",
      },
    ])
    // Create a new thread or update current thread with most recent user query
    const query = data.messages
    let currentThreadId: string | undefined | null = threadId
    if (!threadId) {
      currentThreadId = await createThreadMutation.mutateAsync({
        query: query[0].content,
      })
    } else {
      currentThreadId = await updateThreadMutation.mutateAsync({
        query: query[0].content,
      })
    }

    if (!currentThreadId)
      return showToast(
        "Something went wrong.",
        "Unable to obtain thread id",
        "error",
      )

    const res = await stream(Number.parseInt(teamId), currentThreadId, data)

    if (res.body) {
      const reader = res.body.getReader()
      let done = false
      let buffer = "" // Buffer to accumulate chunks

      while (!done) {
        const { done: streamDone, value } = await reader.read()
        done = streamDone
        if (!done) {
          buffer += new TextDecoder().decode(value)
          let boundary = buffer.lastIndexOf("\n\n")
          while (boundary !== -1) {
            // Extract and parse the complete JSON string
            const chunk = buffer.slice(0, boundary).trim()
            buffer = buffer.slice(boundary + 2)
            if (chunk.startsWith("data: ")) {
              const jsonStr = chunk.slice(6) // Remove 'data: ' prefix
              try {
                const parsed = JSON.parse(jsonStr)
                const newMessages: Message[] = []

                if (!parsed) continue

                if ("error" in parsed) {
                  newMessages.push({
                    type: "ai",
                    content: parsed.error,
                    member: "error",
                  })
                }

                if ("task" in parsed) {
                  for (const task of parsed.task) {
                    if (task.name === "ignore") continue
                    newMessages.push({
                      type: task.type,
                      content: task.content,
                      member: task.name,
                      next: parsed.next,
                    })
                  }
                } else if ("messages" in parsed) {
                  for (const message of parsed.messages) {
                    if (message.name === "ignore") continue
                    newMessages.push({
                      type: message.type,
                      content: message.content,
                      member: message.name,
                      toolCalls: message.tool_calls,
                    })
                  }
                }

                setMessages((prev) => [...prev, ...newMessages])
              } catch (error) {
                console.error("Failed to parse messages:", error)
                return showToast(
                  "Something went wrong.",
                  "Error parsing messages.",
                  "error",
                )
              }
            }
            boundary = buffer.indexOf("\n\n")
          }
        }
      }
    }
  }

  const mutation = useMutation(chatTeam, {
    onMutate: () => {
      setIsStreaming(true)
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSuccess: () => {
      showToast("Streaming completed", "", "success")
    },
    onSettled: () => {
      setIsStreaming(false)
    },
  })

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({ messages: [{ type: "human", content: input }] })
    setInput("")
  }

  const newChatHandler = () => {
    navigate({ search: {} })
    setMessages([])
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
            isDisabled={!input.trim().length}
          />
        </InputRightElement>
      </InputGroup>
      <Box p={2} overflow={"auto"} height="72vh" my={2}>
        {messages.map((message, index) => (
          <MessageBox key={index} message={message} />
        ))}
      </Box>
      <Button leftIcon={<IoCreateOutline/>} position={"fixed"} right={0} bottom={0} margin={8} onClick={newChatHandler}>
        New Chat
      </Button>
    </Box>
  )
}

export default ChatTeam
