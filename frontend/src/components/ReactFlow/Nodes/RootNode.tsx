import {
  Box,
  Icon,
  IconButton,
  Stack,
  useColorModeValue,
  useDisclosure,
  Text,
} from "@chakra-ui/react"
import type { NodeProps } from "reactflow"
import { Handle, Position } from "reactflow"
import { EditMember } from "../../Members/EditMember"
import type { MemberOut } from "../../../client"
import { FiEdit2 } from "react-icons/fi"
import { GrUserManager } from "react-icons/gr"

export type RootNodeData = {
  teamId: number
  member: MemberOut
}

export function RootNode({ data }: NodeProps<RootNodeData>) {
  const editMemberModal = useDisclosure()
  const bgColor = useColorModeValue("gray.50", "ui.darkSlate")

  return (
    <Box w="15rem" p={2} boxShadow="base" borderRadius="lg" bgColor={bgColor}>
      <Stack direction="row" spacing={2} align="center" w="full">
        <Icon as={GrUserManager} boxSize={5} color="gray.400" />
        <Stack spacing={0} w="70%">
          <Text fontWeight="bold" noOfLines={1}>
            {data.member.name}
          </Text>
          <Text fontSize="x-small" noOfLines={2}>
            {data.member.role}
          </Text>
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
