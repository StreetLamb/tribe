import {
  Flex,
  Spinner,
  Container,
  Heading,
  TableContainer,
  Table,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
  useColorModeValue,
  Box,
} from "@chakra-ui/react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useQuery } from "react-query"
import { TeamsService, type ApiError } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import useCustomToast from "../../hooks/useCustomToast"

export const Route = createFileRoute("/_layout/teams/")({
  component: Teams,
})

function Teams() {
  const showToast = useCustomToast()
  // TODO: Use theme instead of hard coding this everywhere
  const rowTint = useColorModeValue("blackAlpha.50", "whiteAlpha.50")
  const navigate = useNavigate()
  const {
    data: teams,
    isLoading,
    isError,
    error,
  } = useQuery("teams", () => TeamsService.readTeams({}))

  if (isError) {
    const errDetail = (error as ApiError).body?.detail
    showToast("Something went wrong.", `${errDetail}`, "error")
  }

  const handleRowClick = (teamId: string) => {
    navigate({ to: "/teams/$teamId", params: { teamId } })
  }

  return (
    <>
      {isLoading ? (
        // TODO: Add skeleton
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        teams && (
          <Container maxW="full">
            <Heading
              size="lg"
              textAlign={{ base: "center", md: "left" }}
              pt={12}
            >
              Teams Management
            </Heading>
            <Navbar type={"Team"} />
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>Description</Th>
                    <Th>Workflow</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {teams.data.map((team) => (
                    <Tr
                      key={team.id}
                      _hover={{ backgroundColor: rowTint }}
                      cursor={"pointer"}
                      onClick={() => handleRowClick(team.id.toString())}
                    >
                      <Td maxW="20rem">
                        <Box
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                        >
                          {team.name}
                        </Box>
                      </Td>
                      <Td
                        maxW="20rem"
                        color={!team.description ? "gray.400" : "inherit"}
                      >
                        <Box
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                        >
                          {team.description || "N/A"}
                        </Box>
                      </Td>
                      <Td color={!team.workflow ? "gray.400" : "inherit"}>
                        {team.workflow || "N/A"}
                      </Td>
                      <Td>
                        <ActionsMenu type={"Team"} value={team} />
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </TableContainer>
          </Container>
        )
      )}
    </>
  )
}

export default Teams
