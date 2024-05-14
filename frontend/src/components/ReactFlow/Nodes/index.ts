import type { NodeTypes } from "reactflow"
import { MemberNode } from "./MemberNode"
import { RootNode } from "./RootNode"
import { FreelancerNode, FreelancerRootNode } from "./FreelancerNode"

export const nodeTypes = {
  worker: MemberNode,
  leader: MemberNode,
  freelancer: FreelancerNode,
  freelancer_root: FreelancerRootNode,
  root: RootNode,
  // Add any of your custom nodes here!
} satisfies NodeTypes
