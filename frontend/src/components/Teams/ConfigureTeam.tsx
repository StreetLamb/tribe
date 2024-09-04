import {
  Button,
  Heading,
  IconButton,
  Link,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
  useDisclosure,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "react-query"
import { type ApiError, ApiKeysService } from "../../client"
import { MdOutlineVpnKey } from "react-icons/md"
import AddApiKey from "./AddApiKey"
import { DeleteIcon } from "@chakra-ui/icons"
import useCustomToast from "../../hooks/useCustomToast"

interface ConfigureTeamProps {
  teamId: string
}

export const ConfigureTeam = ({ teamId }: ConfigureTeamProps) => {
  const queryClient = useQueryClient()
  const addApiKeyModal = useDisclosure()
  const showToast = useCustomToast()
  const {
    data: apikeys,
    isLoading,
    isError,
    error,
  } = useQuery("apikeys", () =>
    ApiKeysService.readApiKeys({ teamId: Number.parseInt(teamId) }),
  )

  const deleteApiKey = async (apiKeyId: number) => {
    await ApiKeysService.deleteApiKey({
      teamId: Number.parseInt(teamId),
      id: apiKeyId,
    })
  }

  const deleteApiKeyMutation = useMutation(deleteApiKey, {
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Unable to delete thread.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries("apikeys")
    },
    onSuccess: () => {
      showToast("Success!", "API key deleted successfully.", "success")
    },
  })

  const onDeleteHandler = (
    e: React.MouseEvent<HTMLButtonElement>,
    apiKeyId: number,
  ) => {
    e.stopPropagation()
    deleteApiKeyMutation.mutate(apiKeyId)
  }

  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast("Something went wrong.", `${errDetail}`, "error")
  }

  return (
    <VStack spacing={"1rem"} alignItems={"flex-start"}>
      <Heading size="lg">API keys</Heading>
      <Text>
        API keys are used for authentication when interacting with your teams
        through HTTP request. Learn how to make requests from the{" "}
        {
          <Link
            href="/redoc#tag/teams/operation/teams-public_stream"
            isExternal
            color="ui.main"
          >
            API docs
          </Link>
        }
        .
      </Text>

      <Button leftIcon={<MdOutlineVpnKey />} onClick={addApiKeyModal.onOpen}>
        Create API Key
      </Button>
      <AddApiKey
        teamId={teamId}
        isOpen={addApiKeyModal.isOpen}
        onClose={addApiKeyModal.onClose}
      />
      <Text>
        You can only access an API key when you first create it. If you lost
        one, you will need to create a new one. Your API keys are listed below.
      </Text>
      <TableContainer width="100%">
        <Table>
          <Thead>
            <Tr>
              <Th>Description</Th>
              <Th>API Key</Th>
              <Th>Created</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {!isLoading &&
              apikeys?.data.map((apikey) => (
                <Tr key={apikey.id}>
                  <Td maxW="20rem" overflow="hidden" textOverflow="ellipsis">
                    {apikey.description}
                  </Td>
                  <Td>{apikey.short_key}</Td>
                  <Td>{new Date(apikey.created_at).toLocaleString()}</Td>
                  <Td>
                    <IconButton
                      size={"sm"}
                      aria-label="Delete"
                      icon={<DeleteIcon />}
                      onClick={(e) => onDeleteHandler(e, apikey.id)}
                    />
                  </Td>
                </Tr>
              ))}
          </Tbody>
        </Table>
      </TableContainer>
    </VStack>
  )
}

export default ConfigureTeam
