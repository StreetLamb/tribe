import type { NodeTypes } from "reactflow"
import { MemberNode } from "./MemberNode"
import { RootNode } from "./RootNode"

export const nodeTypes = {
  member: MemberNode,
  leader: MemberNode,
  root: RootNode,
  // Add any of your custom nodes here!
} satisfies NodeTypes
