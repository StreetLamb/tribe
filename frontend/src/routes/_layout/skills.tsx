import { createFileRoute } from "@tanstack/react-router"
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
  Box,
} from "@chakra-ui/react"
import { useQuery } from "react-query"
import { SkillsService, type ApiError } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import useCustomToast from "../../hooks/useCustomToast"

export const Route = createFileRoute("/_layout/skills")({
  component: Skills,
})

function Skills() {
  const showToast = useCustomToast()
  const {
    data: skills,
    isLoading,
    isError,
    error,
  } = useQuery("skills", () => SkillsService.readSkills({}))

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
        skills && (
          <Container maxW="full">
            <Heading
              size="lg"
              textAlign={{ base: "center", md: "left" }}
              pt={12}
            >
              Skills Management
            </Heading>
            <Navbar type={"Skill"} />
            <TableContainer>
              <Table size={{ base: "sm", md: "md" }}>
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>Description</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {skills.data.map((skill) => (
                    <Tr key={skill.id}>
                      <Td maxW="20rem">
                        <Box
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                        >
                          {skill.name}
                        </Box>
                      </Td>
                      <Td maxW="20rem">
                        <Box
                          overflow="hidden"
                          textOverflow="ellipsis"
                          whiteSpace="nowrap"
                        >
                          {skill.description}
                        </Box>
                      </Td>
                      <Td>
                        {!skill.managed ? (
                          <ActionsMenu type={"Skill"} value={skill} />
                        ) : (
                          "Managed"
                        )}
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

export default Skills
