import {
  Flex,
  Spinner,
  Container,
  Heading,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from "@chakra-ui/react"
import { Link, createFileRoute } from "@tanstack/react-router"
import { useQuery } from "react-query"
import { TeamsService, type ApiError } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { ChevronRightIcon } from "@chakra-ui/icons"

export const Route = createFileRoute("/_layout/teams/$teamId")({
  component: Team,
})

function Team() {
  const showToast = useCustomToast()
  const { teamId } = Route.useParams()
  const {
    data: team,
    isLoading,
    isError,
    error,
  } = useQuery(`team/${teamId}`, () =>
    TeamsService.readTeam({ id: Number.parseInt(teamId) }),
  )

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
        team && (
          <Container maxW="full">
            <Breadcrumb
              pt={12}
              separator={<ChevronRightIcon color="gray.500" />}
            >
              <BreadcrumbItem>
                <BreadcrumbLink as={Link} to="/teams">
                  Teams
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbItem isCurrentPage>
                <BreadcrumbLink as={Link} to="">
                  {team.name}
                </BreadcrumbLink>
              </BreadcrumbItem>
            </Breadcrumb>
            <Heading
              size="lg"
              textAlign={{ base: "center", md: "left" }}
              pt={2}
            >
              {team.name}
            </Heading>
          </Container>
        )
      )}
    </>
  )
}

export default Team
