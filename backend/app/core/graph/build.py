import json
from collections import defaultdict, deque
from functools import partial

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

from app.core.graph.members import (
    Leader,
    LeaderNode,
    Member,
    SummariserNode,
    TeamState,
    WorkerNode,
)
from app.models import ChatMessage, Team
from app.models import Member as MemberModel

model = ChatOpenAI(model="gpt-3.5-turbo")


def convert_team_to_dict(team: Team, members: list[MemberModel]):
    """Convert team and members model to teams dict

    Args:
        team (Team): Team Model
        members (list[Member]): list of members model

    Raises:
        ValueError: Root leader not found

    Returns:
        dict: Dict containing the team and members
    """

    teams = {}

    in_counts = defaultdict(int)
    out_counts = defaultdict(list[int])
    members_lookup: dict[int, MemberModel] = {}

    for member in members:
        if member.source:
            in_counts[member.id] += 1
            out_counts[member.source].append(member.id)
        else:
            in_counts[member.id] = 0
        members_lookup[member.id] = member

    queue = deque()

    for member_id in in_counts:
        if in_counts[member_id] == 0:
            queue.append(member_id)

    while queue:
        member_id = queue.popleft()
        member = members_lookup[member_id]
        if member.type == "root" or member.type == "leader":
            leader_name = member.name
            # Create the team definitions
            teams[leader_name] = {
                "name": team.name,
                "members": {},
            }
        # If member is not root team leader, add as a member
        if member.type != "root":
            member_name = member.name
            leader = members_lookup[member.source]
            leader_name = leader.name
            teams[leader_name]["members"][member_name] = {
                "type": member.type,
                "name": member_name,
                "backstory": member.backstory or "",
                "role": member.role,
                "tools": [skill.name for skill in member.skills],
            }

        for nei_id in out_counts[member_id]:
            in_counts[nei_id] -= 1
            if in_counts[nei_id] == 0:
                queue.append(nei_id)

    return teams


# Create the Member/Leader class instance in members
def format_teams(teams: dict[str, any]):
    """Update the team members to use Member/Leader"""
    for team in teams:
        members = teams[team]["members"]
        for k, v in members.items():
            teams[team]["members"][k] = (
                Leader(**v) if v["type"] == "leader" else Member(**v)
            )
    return teams


def router(state: TeamState):
    return state["next"]


def enter_chain(state: TeamState, team: dict[str, str | list[Member | Leader]]):
    """
    Initialise the sub-graph state.
    This makes it so that the states of each graph don't get intermixed.
    """
    task = state["task"]
    team_name = team["name"]
    team_members = team["members"]

    results = {
        "messages": task,
        "team_name": team_name,
        "team_members": team_members,
    }
    return results


def exit_chain(state: TeamState):
    """
    Pass the final response back to the top-level graph's state.
    """
    answer = state["messages"][-1]
    return {"messages": [answer]}


def create_graph(
    teams: dict[str, dict[str, str | dict[str, Member | Leader]]], leader_name: str
):
    """
    Create the team's graph.
    """
    build = StateGraph(TeamState)
    # Add the start and end node
    build.add_node(leader_name, RunnableLambda(LeaderNode(model).delegate))
    build.add_node("summariser", RunnableLambda(SummariserNode(model).summarise))

    members = teams[leader_name]["members"]
    for name, member in members.items():
        if isinstance(member, Member):
            build.add_node(name, RunnableLambda(WorkerNode(model).work))
        elif isinstance(member, Leader):
            subgraph = create_graph(teams, leader_name=name)
            enter = partial(enter_chain, team=teams[name])
            build.add_node(name, enter | subgraph | exit_chain)
        else:
            continue
        build.add_edge(name, leader_name)

    conditional_mapping = {v: v for v in members}
    conditional_mapping["FINISH"] = "summariser"
    build.add_conditional_edges(leader_name, router, conditional_mapping)

    build.set_entry_point(leader_name)
    build.set_finish_point("summariser")
    graph = build.compile()
    return graph


async def generator(team: Team, members: list[Member], messages: list[ChatMessage]):
    """Create the graph and stream responses as JSON."""
    teams = convert_team_to_dict(team, members)
    team_leader = list(teams.keys())[0]
    format_teams(teams)
    root = create_graph(teams, leader_name=team_leader)
    messages = [
        HumanMessage(message.content)
        if message.type == "human"
        else AIMessage(message.content)
        for message in messages
    ]

    # TODO: Figure out how to use async_stream to stream responses from subgraphs
    async for output in root.astream(
        {
            "messages": messages,
            "team_name": teams[team_leader]["name"],
            "team_members": teams[team_leader]["members"],
        }
    ):
        if "__end__" not in output:
            for _key, value in output.items():
                if "task" in value:
                    value["task"] = [message.dict() for message in value["task"]]
                if "messages" in value:
                    value["messages"] = [
                        message.dict() for message in value["messages"]
                    ]
                formatted_output = f"data: {json.dumps(output)}\n\n"
                yield formatted_output


# teams = {
#     "FoodExpertLeader": {
#         "name": "FoodExperts",
#         "members": {
#             "ChineseFoodExpert": {
#                 "type": "worker",
#                 "name": "ChineseFoodExpert",
#                 "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. ISFP.",
#                 "role": "Provide chinese food suggestions in Singapore",
#                 "tools": []
#             },
#             "MalayFoodExpert": {
#                 "type": "worker",
#                 "name": "MalayFoodExpert",
#                 "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. INTP.",
#                 "role": "Provide malay food suggestions in Singapore",
#                 "tools": []
#             },
#         }
#     },
#     "TravelExpertLeader": {
#         "name": "TravelKakis",
#         "members": {
#             "FoodExpertLeader": {
#                 "type": "leader",
#                 "name": "FoodExpertLeader",
#                 "role": "Gather inputs from your team and provide a diverse food suggestions in Singapore.",
#                 "tools": []
#             },
#             "HistoryExpert": {
#                 "type": "worker",
#                 "name": "HistoryExpert",
#                 "backstory": "Studied Singapore history. Well-verse in Singapore architecture. INTJ.",
#                 "role": "Provide places to sight-see with a history/architecture angle",
#                 "tools": ["search"]
#             }
#         }
#     }
# }

# format_teams(teams)

# team_leader = "TravelExpertLeader"

# root = create_graph(teams, team_leader)

# messages = [
#     HumanMessage(f"What is the best food in Singapore")
# ]

# initial_state = {
#     "messages": messages,
#     "team_name": teams[team_leader]["name"],
#     "team_members": teams[team_leader]["members"],
# }

# async def main():
#     async for s in root.astream(initial_state):
#         if "__end__" not in s:
#           print(s)
#           print("----")

# import asyncio

# asyncio.run(main())
