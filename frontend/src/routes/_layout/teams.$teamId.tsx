import {
  Flex,
  Spinner,
  Container,
  Heading,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Tabs,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
} from "@chakra-ui/react"
import { Link, createFileRoute } from "@tanstack/react-router"
import { useQuery } from "react-query"
import { TeamsService, type ApiError } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { ChevronRightIcon } from "@chakra-ui/icons"
import Flow from "../../components/ReactFlow/Flow"
import ChatTeam from "../../components/Teams/ChatTeam"
import ViewThreads from "../../components/Teams/ViewThreads"
import { useState } from "react"
import ConfigureTeam from "../../components/Teams/ConfigureTeam"

type SearchSchema = {
  threadId?: string
}

export const Route = createFileRoute("/_layout/teams/$teamId")({
  component: Team,
  validateSearch: (search: Record<string, unknown>): SearchSchema => {
    return {
      threadId:
        typeof search?.threadId === "string" ? search.threadId : undefined,
    }
  },
})

function Team() {
  const showToast = useCustomToast()
  const { teamId } = Route.useParams()
  const [tabIndex, setTabIndex] = useState(0)
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
          <Container maxW="full" maxHeight="full">
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
            <Tabs
              pt={2}
              variant="enclosed"
              index={tabIndex}
              onChange={setTabIndex}
            >
              <TabList>
                <Tab>Build</Tab>
                <Tab>Chat</Tab>
                <Tab>Threads</Tab>
                <Tab>Configure</Tab>
              </TabList>
              <TabPanels>
                <TabPanel height="80vh">
                  <Flow />
                </TabPanel>
                <TabPanel>
                  <ChatTeam />
                </TabPanel>
                <TabPanel>
                  <ViewThreads teamId={teamId} updateTabIndex={setTabIndex} />
                </TabPanel>
                <TabPanel>
                  <ConfigureTeam teamId={teamId} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Container>
        )
      )}
    </>
  )
}

export default Team
