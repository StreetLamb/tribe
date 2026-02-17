import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  Container,
  Fade,
  Flex,
  HStack,
  Icon,
  IconButton,
  Input,
  InputGroup,
  InputRightElement,
  Tag,
  TagCloseButton,
  TagLabel,
  Text,
  Tooltip,
  VStack,
  useDisclosure,
} from "@chakra-ui/react"
import { fetchEventSource } from "@microsoft/fetch-event-source"
import { getRouteApi, useNavigate, useParams } from "@tanstack/react-router"
import { useRef, useState } from "react"
import { FaCheck, FaTimes } from "react-icons/fa"
import { FaRegFileImage } from "react-icons/fa"
import { FiCopy, FiPaperclip } from "react-icons/fi"
import { GrFormNextLink } from "react-icons/gr"
import { IoCreateOutline } from "react-icons/io5"
import { VscSend } from "react-icons/vsc"
import { useMutation, useQuery, useQueryClient } from "react-query"
import { v4 } from "uuid"
import {
  type ApiError,
  type ChatResponse,
  type InterruptDecision,
  OpenAPI,
  type OpenAPIConfig,
  type TeamChat,
  type ThreadCreate,
  type ThreadUpdate,
  ThreadsService,
} from "../../client"
import type { ApiRequestOptions } from "../../client/core/ApiRequestOptions"
import {
  getHeaders,
  getQueryString,
  getRequestBody,
} from "../../client/core/request"
import type { ChatMessage } from "../../client/models/ChatMessage"
import useCustomToast from "../../hooks/useCustomToast"
import Markdown from "../Markdown/Markdown"

// possible message types: "ai" | "human" | "tool" | "error" | "interrupt"

const IMAGE_EXTENSIONS = [
  ".png",
  ".jpg",
  ".jpeg",
  ".gif",
  ".webp",
  ".bmp",
  ".svg",
  ".heic",
  ".heif",
]

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

type Attachment = { name: string; type: "image" | "file" }

type ChatUiMessage = ChatResponse & {
  attachments?: Attachment[]
}

interface MessageBoxProps {
  message: ChatUiMessage
  onResume: (decision: InterruptDecision, toolMessage: string | null) => void
}

const MessageBox = ({ message, onResume }: MessageBoxProps) => {
  const {
    type,
    name,
    next,
    content,
    tool_calls,
    tool_output,
    documents,
    attachments,
  } = message
  const [decision, setDecision] = useState<InterruptDecision | null>(null)
  const [toolMessage, setToolMessage] = useState<string | null>(null)
  const { isOpen: showClipboardIcon, onOpen, onClose } = useDisclosure()

  const onDecisionHandler = (decision: InterruptDecision) => {
    setDecision(decision)
    onResume(decision, toolMessage)
  }

  return (
    <VStack spacing={0} my={8} onMouseEnter={onOpen} onMouseLeave={onClose}>
      <Container fontWeight={"bold"} display={"flex"} alignItems="center">
        {name}
        {next && <Icon as={GrFormNextLink} mx={2} />}
        {next && next}
        <Tag ml={4}>{type.toUpperCase()}</Tag>
      </Container>
      <Container pt={2}>
        {content && <Markdown content={content} />}
        {!!attachments?.length && (
          <HStack spacing={2} mt={2} wrap="wrap">
            {attachments.map((attachment, index) => (
              <Tag
                key={`${attachment.name}-${index}`}
                size="sm"
                colorScheme="blue"
              >
                <Icon
                  as={
                    attachment.type === "image" ? FaRegFileImage : FiPaperclip
                  }
                  mr={1}
                />
                <TagLabel>{attachment.name}</TagLabel>
              </Tag>
            ))}
          </HStack>
        )}
        {tool_calls?.map((tool_call, index) => (
          <Box key={index} mb={4}>
            <Tag colorScheme="purple">{tool_call.name}</Tag>
            <Box mb={2}>
              {Object.keys(tool_call.args).map((attribute, index) => (
                <Text key={index}>
                  <b>{attribute}:</b>{" "}
                  <Markdown content={tool_call.args[attribute]} />
                </Text>
              ))}
            </Box>
          </Box>
        ))}
        {tool_output && (
          <Container maxH={"10rem"} overflow="auto">
            <Markdown content={JSON.parse(tool_output)} />
          </Container>
        )}
        {documents && (
          <Accordion mt={2} allowMultiple>
            {(
              JSON.parse(documents) as { score: number; content: string }[]
            ).map((document, index) => (
              <AccordionItem key={index}>
                <h2>
                  <AccordionButton>
                    <Box textAlign="left" w="full">
                      <HStack>
                        <Text flex={1} noOfLines={1}>
                          {document.content}
                        </Text>
                        <Tag ml="auto" mr={0}>
                          {document.score.toFixed(2)}
                        </Tag>
                      </HStack>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>{document.content}</AccordionPanel>
              </AccordionItem>
            ))}
          </Accordion>
        )}
        {type === "interrupt" && name === "human" && !decision && (
          <Flex alignItems={"center"} gap="1rem" mt={8}>
            <InputGroup size="md" width={"20rem"}>
              <Input
                pr="3rem"
                placeholder="Ваш ответ..."
                onChange={(e) => setToolMessage(e.target.value)}
              />
              <InputRightElement>
                <IconButton
                  icon={<VscSend />}
                  aria-label="human-reply"
                  isDisabled={!toolMessage?.trim().length}
                  onClick={() => onDecisionHandler("replied")}
                />
              </InputRightElement>
            </InputGroup>
          </Flex>
        )}
        {type === "interrupt" && name === "interrupt" && !decision && (
          <Flex alignItems={"center"} gap="1rem">
            <Tooltip>
              <Button
                autoFocus
                variant={"outline"}
                aria-label="approve"
                leftIcon={<FaCheck />}
                colorScheme="green"
                onClick={() => onDecisionHandler("approved")}
              >
                Одобрить
              </Button>
            </Tooltip>
            или
            <InputGroup size="md" width={"20rem"}>
              <Input
                pr="3rem"
                placeholder="Необязательные инструкции для отказа..."
                onChange={(e) => setToolMessage(e.target.value)}
              />
              <InputRightElement width="3rem">
                <Tooltip label="Отклонить">
                  <IconButton
                    variant={"outline"}
                    h="1.75rem"
                    aria-label="reject"
                    icon={<FaTimes />}
                    size="sm"
                    colorScheme="red"
                    onClick={() => onDecisionHandler("rejected")}
                  >
                    Reject
                  </IconButton>
                </Tooltip>
              </InputRightElement>
            </InputGroup>
          </Flex>
        )}
      </Container>
      {content && (
        <Container pt={2}>
          <Fade in={showClipboardIcon}>
            <IconButton
              aria-label="copy to clipboard"
              icon={<FiCopy />}
              variant="outline"
              size="xs"
              onClick={() => navigator.clipboard.writeText(content)}
            />
          </Fade>
        </Container>
      )}
    </VStack>
  )
}

const ChatTeam = () => {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { threadId }: { threadId?: string } = getRouteApi(
    "/_layout/teams/$teamId",
  ).useSearch()
  const { teamId } = useParams({ strict: false }) as { teamId: string }
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const showToast = useCustomToast()
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<ChatUiMessage[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  useQuery(
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
        showToast("Что-то пошло не так.", `${errDetail}`, "error")
        // if fail, then remove it from search params and delete existing messages
        navigate({ search: {} })
        setMessages([])
      },
      onSuccess: (data) => {
        // if thread changed, then show new thread's messages
        if (!threadId || threadId === currentThreadId) return
        setMessages([])
        setCurrentThreadId(threadId)
        for (const message of data.messages) {
          processMessage(message)
        }
      },
    },
  )

  const createThread = async (data: ThreadCreate) => {
    const thread = await ThreadsService.createThread({
      teamId: Number.parseInt(teamId),
      requestBody: data,
    })
    return thread.id
  }
  const createThreadMutation = useMutation(createThread, {
    onSuccess: (threadId) => {
      setCurrentThreadId(threadId)
      navigate({ search: { threadId } })
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Не удалось создать диалог", `${errDetail}`, "error")
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
      showToast("Не удалось обновить диалог.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries(["threads", teamId])
    },
  })

  const processMessage = (response: ChatResponse) => {
    setMessages((prevMessages) => {
      const updatedMessages = [...prevMessages]

      const messageIndex = updatedMessages.findIndex(
        (msg) => msg.id === response.id,
      )

      if (messageIndex !== -1) {
        const currentMessage = updatedMessages[messageIndex]
        updatedMessages[messageIndex] = {
          ...currentMessage,
          // only content is streamable in chunks
          content: currentMessage.content
            ? currentMessage.content + (response.content || "")
            : null,
          tool_output: response.tool_output,
        }
      } else {
        updatedMessages.push(response)
      }
      return updatedMessages
    })
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

    await fetchEventSource(url, {
      openWhenHidden: true,
      method: requestOptions.method,
      headers,
      body: JSON.stringify(body),
      onmessage(message) {
        const response: ChatResponse = JSON.parse(message.data)
        processMessage(response)
      },
    })
  }

  const getAttachments = (content: ChatMessage["content"]): Attachment[] => {
    if (typeof content === "string") return []

    const attachments: Attachment[] = []
    for (const part of content) {
      if (part.type === "image_url") {
        attachments.push({ name: "Изображение", type: "image" })
      }
      if (part.type === "file") {
        attachments.push({ name: part.file.filename || "Файл", type: "file" })
      }
    }

    return attachments
  }

  const getTextContent = (content: ChatMessage["content"]): string => {
    if (typeof content === "string") return content
    return content
      .filter((part) => part.type === "text")
      .map((part) => (part.type === "text" ? part.text : ""))
      .join("\n")
  }

  const toDataUrl = (file: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = () => reject(new Error("Failed to read file"))
      reader.readAsDataURL(file)
    })

  const isImageAttachment = (file: File, dataUrl: string) => {
    const fileName = file.name.toLowerCase()
    const hasImageExtension = IMAGE_EXTENSIONS.some((extension) =>
      fileName.endsWith(extension),
    )
    return (
      file.type.startsWith("image/") ||
      dataUrl.startsWith("data:image/") ||
      hasImageExtension
    )
  }

  const buildContent = async () => {
    const content: ChatMessage["content"] = []
    if (input.trim().length) {
      content.push({ type: "text", text: input })
    }
    for (const file of files) {
      const dataUrl = await toDataUrl(file)
      if (isImageAttachment(file, dataUrl)) {
        content.push({ type: "image_url", image_url: { url: dataUrl } })
      } else {
        content.push({
          type: "file",
          file: {
            filename: file.name,
            file_data: dataUrl,
          },
        })
      }
    }
    return content.length === 1 && content[0].type === "text"
      ? content[0].text
      : content
  }

  const chatTeam = async (data: TeamChat) => {
    // Create a new thread or update current thread with most recent user query
    const query = data.messages
    let currentThreadId: string | undefined | null = threadId
    if (!threadId) {
      currentThreadId = await createThreadMutation.mutateAsync({
        query: getTextContent(query[0].content),
      })
    } else {
      currentThreadId = await updateThreadMutation.mutateAsync({
        query: getTextContent(query[0].content),
      })
    }

    if (!currentThreadId)
      return showToast(
        "Something went wrong.",
        "Unable to obtain thread id",
        "error",
      )

    setMessages((prev) => [
      ...prev,
      {
        type: "human",
        id: v4(),
        content: getTextContent(data.messages[0].content) || null,
        name: "user",
        attachments: getAttachments(data.messages[0].content),
      },
    ])

    await stream(Number.parseInt(teamId), currentThreadId, data)
  }

  const mutation = useMutation(chatTeam, {
    onMutate: () => {
      setIsStreaming(true)
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Что-то пошло не так.", `${errDetail}`, "error")
    },
    onSuccess: () => {
      showToast("Поток завершен", "", "success")
    },
    onSettled: () => {
      setIsStreaming(false)
    },
  })

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const content = await buildContent()
    if (typeof content === "string" && !content.trim().length) return
    if (Array.isArray(content) && !content.length) return
    mutation.mutate({ messages: [{ type: "human", content }] })
    setInput("")
    setFiles([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const newChatHandler = () => {
    navigate({ search: {} })
    setMessages([])
    setFiles([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleFilesSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (!selectedFiles.length) return

    setFiles((prev) => [...prev, ...selectedFiles])
    e.target.value = ""
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, currentIndex) => currentIndex !== index))
  }

  /**
   * Submit the interrupt decision and optional tool message
   */
  const onResumeHandler = (
    decision: InterruptDecision,
    tool_message?: string | null,
  ) => {
    mutation.mutate({
      messages: [
        {
          type: "human",
          content: tool_message || decision,
        },
      ],
      interrupt: { decision, tool_message },
    })
  }

  return (
    <Box>
      <InputGroup as="form" onSubmit={onSubmit}>
        <Input
          type="text"
          placeholder="Задайте вопрос вашей команде"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <Button
          as="label"
          htmlFor="chat-files"
          mb={0}
          ml={2}
          size="sm"
          variant="outline"
          leftIcon={<FiPaperclip />}
        >
          Файлы
        </Button>
        <Input
          id="chat-files"
          ref={fileInputRef}
          type="file"
          multiple
          display="none"
          onChange={handleFilesSelect}
        />
        <InputRightElement>
          <IconButton
            type="submit"
            icon={<VscSend />}
            aria-label="send-question"
            isLoading={isStreaming}
            isDisabled={!input.trim().length && files.length === 0}
          />
        </InputRightElement>
      </InputGroup>
      {files.length > 0 && (
        <HStack spacing={2} mt={2} wrap="wrap">
          {files.map((file, index) => (
            <Tag key={`${file.name}-${index}`} size="sm" colorScheme="gray">
              <TagLabel>{file.name}</TagLabel>
              <TagCloseButton onClick={() => removeFile(index)} />
            </Tag>
          ))}
        </HStack>
      )}
      <Box p={2} overflow={"auto"} height="72vh" my={2}>
        {messages.map((message, index) => (
          <MessageBox
            key={index}
            message={message}
            onResume={onResumeHandler}
          />
        ))}
      </Box>
      <Button
        leftIcon={<IoCreateOutline />}
        position={"fixed"}
        right={0}
        bottom={0}
        margin={8}
        onClick={newChatHandler}
      >
        Новый чат
      </Button>
    </Box>
  )
}

export default ChatTeam
