import {
  IconButton,
  useColorModeValue,
  useDisclosure,
  Text,
  Grid,
  GridItem,
  Tag,
} from "@chakra-ui/react"
import type { NodeProps } from "reactflow"
import { Position } from "reactflow"
import { EditMember } from "../../Members/EditMember"
import type { MemberOut } from "../../../client"
import { FiEdit2 } from "react-icons/fi"
import LimitConnectionHandle from "../Handles/LimitConnectionHandle"

export type FreelancerNodeData = {
  teamId: number
  member: MemberOut
}

export function FreelancerNode({ data }: NodeProps<FreelancerNodeData>) {
  const editMemberModal = useDisclosure()
  const bgColor = useColorModeValue("gray.50", "ui.darkSlate")

  return (
    <Grid
      w="15rem"
      templateColumns={"repeat(6,1fr)"}
      templateRows={"repeat(auto-fill, 0.5fr)"}
      p={1.5}
      boxShadow="base"
      borderRadius="lg"
      bgColor={bgColor}
      gap={1}
    >
      <GridItem colSpan={5}>
        <Text fontWeight={"bold"} noOfLines={1}>
          {data.member.name}
        </Text>
      </GridItem>
      <GridItem colStart={6} justifySelf={"end"}>
        <IconButton
          color="#009688"
          size="xs"
          fontSize={"xx-small"}
          aria-label="Edit Member"
          icon={<FiEdit2 />}
          onClick={editMemberModal.onOpen}
          variant="outline"
          colorScheme="blue"
        />
        <EditMember
          isOpen={editMemberModal.isOpen}
          onClose={editMemberModal.onClose}
          teamId={data.teamId}
          member={data.member}
        />
      </GridItem>
      <GridItem colSpan={6}>
        <Text fontSize="xx-small" noOfLines={2}>
          {data.member.role}
        </Text>
      </GridItem>
      <GridItem colSpan={6} maxW={"full"}>
        <Tag size="sm" colorScheme="blue" mt="0.2rem" mb={0}>
          <Text fontSize="xx-small" noOfLines={1}>
            {data.member.model}
          </Text>
        </Tag>
      </GridItem>
      <GridItem colSpan={6} maxW={"full"} noOfLines={1}>
        {[...data.member.skills, ...data.member.uploads].map((item, index) => (
          <Tag
            key={index}
            size="sm"
            fontSize="xx-small"
            colorScheme="purple"
            mr={0.5}
          >
            {item.name}
          </Tag>
        ))}
      </GridItem>
      {data.member.type !== "freelancer_root" && (
        <LimitConnectionHandle
          type="target"
          position={Position.Top}
          connectionLimit={1}
        />
      )}
      <LimitConnectionHandle
        type="source"
        position={Position.Bottom}
        connectionLimit={1}
      >
        {data.member.interrupt && (
          <Text
            fontSize="xx-small"
            fontWeight={"bold"}
            color="orange"
            position={"absolute"}
            left="3"
            top="1"
            width="10rem"
          >
            Approval Required
          </Text>
        )}
      </LimitConnectionHandle>
    </Grid>
  )
}
