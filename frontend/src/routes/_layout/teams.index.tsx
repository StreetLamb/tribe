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
  LinkBox,
  LinkOverlay,
  textDecoration,
} from "@chakra-ui/react"
import { Link, createFileRoute } from "@tanstack/react-router"
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
                    <Th>ID</Th>
                    <Th>Name</Th>
                    <Th>Description</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {teams.data.map((team) => (
                    <Tr key={team.id}>
                      <Td>{team.id}</Td>
                      <LinkBox as={Td} _hover={{ textDecoration: "underline" }}>
                        <LinkOverlay as={Link} to={team.id}>
                          {team.name}
                        </LinkOverlay>
                      </LinkBox>
                      <Td color={!team.description ? "gray.400" : "inherit"}>
                        {team.description || "N/A"}
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
