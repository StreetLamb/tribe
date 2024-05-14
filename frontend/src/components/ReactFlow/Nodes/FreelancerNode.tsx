import {
  Box,
  Container,
  Icon,
  IconButton,
  Stack,
  useDisclosure,
} from "@chakra-ui/react"
import type { NodeProps } from "reactflow"
import { Handle, Position } from "reactflow"
import { EditMember } from "../../Members/EditMember"
import type { MemberOut } from "../../../client"
import { FiEdit2 } from "react-icons/fi"
import { GrUserWorker } from "react-icons/gr"

export type FreelancerNodeData = {
  teamId: number
  member: MemberOut
}

export function FreelancerRootNode({ data }: NodeProps<FreelancerNodeData>) {
  const editMemberModal = useDisclosure()

  return (
    <Box
      width="15rem"
      p={2}
      boxShadow="base"
      borderRadius="lg"
      bgColor={"blackAlpha.50"}
    >
      <Stack direction="row" spacing={0} align="center">
        <Icon as={GrUserWorker} boxSize={5} color="gray.400" />
        <Stack spacing={0}>
          <Container fontWeight={"bold"}>{data.member.name}</Container>
          <Container fontSize={"x-small"} noOfLines={2}>
            {data.member.role}
          </Container>
        </Stack>
        <IconButton
          size="xs"
          aria-label="Edit Member"
          icon={<FiEdit2 />}
          onClick={editMemberModal.onOpen}
          variant="outline"
          colorScheme="blue"
        />
      </Stack>
      <EditMember
        isOpen={editMemberModal.isOpen}
        onClose={editMemberModal.onClose}
        teamId={data.teamId}
        member={data.member}
      />
      <Handle type="source" position={Position.Bottom} />
    </Box>
  )
}

export function FreelancerNode({ data }: NodeProps<FreelancerNodeData>) {
  const editMemberModal = useDisclosure()

  return (
    <Box
      width="15rem"
      p={2}
      boxShadow="base"
      borderRadius="lg"
      bgColor={"blackAlpha.50"}
    >
      <Stack direction="row" spacing={0} align="center">
        <Icon as={GrUserWorker} boxSize={5} color="gray.400" />
        <Stack spacing={0}>
          <Container fontWeight={"bold"}>{data.member.name}</Container>
          <Container fontSize={"x-small"} noOfLines={2}>
            {data.member.role}
          </Container>
        </Stack>
        <IconButton
          size="xs"
          aria-label="Edit Member"
          icon={<FiEdit2 />}
          onClick={editMemberModal.onOpen}
          variant="outline"
          colorScheme="blue"
        />
      </Stack>
      <EditMember
        isOpen={editMemberModal.isOpen}
        onClose={editMemberModal.onClose}
        teamId={data.teamId}
        member={data.member}
      />
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </Box>
  )
}
