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
import { GrUserManager, GrUserWorker } from "react-icons/gr"

export type MemberNodeData = {
  teamId: number
  member: MemberOut
}

export function MemberNode({ data }: NodeProps<MemberNodeData>) {
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
        {data.member.type === "member" ? (
          <Icon as={GrUserWorker} boxSize={5} color="gray.400" />
        ) : (
          <Icon as={GrUserManager} boxSize={5} color="gray.400" />
        )}
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
      {data.member.type === "leader" && (
        <Handle type="source" position={Position.Bottom} />
      )}
    </Box>
  )
}
