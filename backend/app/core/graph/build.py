import json
from collections import defaultdict, deque
from collections.abc import AsyncGenerator
from functools import partial
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph

from app.core.graph.members import (
    GraphLeader,
    GraphMember,
    GraphTeam,
    LeaderNode,
    SequentialWorkerNode,
    SummariserNode,
    TeamState,
    WorkerNode,
)
from app.models import ChatMessage, Member, Team


def convert_hierarchical_team_to_dict(
    team: Team, members: list[Member]
) -> dict[str, GraphTeam]:
    """
    Converts a team and its members into a dictionary representation.

    Args:
        team (Team): The team model to be converted.
        members (list[Member]): A list of member models belonging to the team.

    Returns:
        dict: A dictionary containing the team's information, with member details.

    Raises:
        ValueError: If the root leader is not found in the team.

    Notes:
        This function assumes that each team has a single root leader.
    """
    teams: dict[str, GraphTeam] = {}

    in_counts: defaultdict[int, int] = defaultdict(int)
    out_counts: defaultdict[int, list[int]] = defaultdict(list[int])
    members_lookup: dict[int, Member] = {}

    for member in members:
        assert member.id is not None, "member.id is unexpectedly None"
        if member.source:
            in_counts[member.id] += 1
            out_counts[member.source].append(member.id)
        else:
            in_counts[member.id] = 0
        members_lookup[member.id] = member

    queue: deque[int] = deque()

    for member_id in in_counts:
        if in_counts[member_id] == 0:
            queue.append(member_id)

    while queue:
        member_id = queue.popleft()
        member = members_lookup[member_id]
        if member.type == "root" or member.type == "leader":
            leader_name = member.name
            # Create the team definitions
            teams[leader_name] = GraphTeam(
                name=team.name,
                model=member.model,
                members={},
                provider=member.provider,
                temperature=member.temperature,
            )
        # If member is not root team leader, add as a member
        if member.type != "root" and member.source:
            member_name = member.name
            leader = members_lookup[member.source]
            leader_name = leader.name
            if member.type == "worker":
                teams[leader_name].members[member_name] = GraphMember(
                    name=member_name,
                    backstory=member.backstory or "",
                    role=member.role,
                    tools=[skill.name for skill in member.skills],
                    provider=member.provider,
                    model=member.model,
                    temperature=member.temperature,
                )
            elif member.type == "leader":
                teams[leader_name].members[member_name] = GraphLeader(
                    name=member_name,
                    role=member.role,
                    provider=member.provider,
                    model=member.model,
                    temperature=member.temperature,
                )
        for nei_id in out_counts[member_id]:
            in_counts[nei_id] -= 1
            if in_counts[nei_id] == 0:
                queue.append(nei_id)

    return teams


def convert_sequential_team_to_dict(team: Team) -> dict[str, GraphMember]:
    team_dict: dict[str, GraphMember] = {}

    in_counts: defaultdict[int, int] = defaultdict(int)
    out_counts: defaultdict[int, list[int]] = defaultdict(list[int])
    members_lookup: dict[int, Member] = {}

    for member in team.members:
        assert member.id is not None, "member.id is unexpectedly None"
        if member.source:
            in_counts[member.id] += 1
            out_counts[member.source].append(member.id)
        else:
            in_counts[member.id] = 0
        members_lookup[member.id] = member

    queue: deque[int] = deque()

    for member_id in in_counts:
        if in_counts[member_id] == 0:
            queue.append(member_id)

    while queue:
        member_id = queue.popleft()
        memberModel = members_lookup[member_id]
        graph_member = GraphMember(
            name=memberModel.name,
            backstory=memberModel.backstory or "",
            role=memberModel.role,
            tools=[skill.name for skill in memberModel.skills],
            provider=memberModel.provider,
            model=memberModel.model,
            temperature=memberModel.temperature,
        )
        team_dict[graph_member.name] = graph_member
        for nei_id in out_counts[member_id]:
            in_counts[nei_id] -= 1
            if in_counts[nei_id] == 0:
                queue.append(nei_id)
    return team_dict


def format_teams(teams: dict[str, dict[str, Any]]) -> dict[str, GraphTeam]:
    """
    FOR TESTING PURPOSES ONLY!

    This function takes a dictionary of teams and formats their member lists to use instances of the `Member` or `Leader`
    classes.

    Args:
        teams (dict[str, any]): A dictionary where each key is a team name and the value is another dictionary containing
            the team's members

    Returns:
        dict[str, Team]: The input dictionary with its member lists formatted to use instances of `Member` or `Leader`
    """
    for team_name, team in teams.items():
        if not isinstance(team, dict):
            raise ValueError(f"Invalid team {team_name}. Teams must be dictionaries.")
        members: dict[str, dict[str, Any]] = team.get("members", {})
        for k, v in members.items():
            if v["type"] == "leader":
                teams[team_name]["members"][k] = GraphLeader(**v)
            else:
                teams[team_name]["members"][k] = GraphMember(**v)
    return {team_name: GraphTeam(**team) for team_name, team in teams.items()}


def router(state: TeamState) -> str:
    return state["next"]


def enter_chain(state: TeamState, team: GraphTeam) -> dict[str, Any]:
    """
    Initialise the sub-graph state.
    This makes it so that the states of each graph don't get intermixed.
    """
    task = state["task"]

    results = {
        "messages": task,
        "team_name": team.name,
        "team_members": team.members,
    }
    return results


def exit_chain(state: TeamState) -> dict[str, list[BaseMessage]]:
    """
    Pass the final response back to the top-level graph's state.
    """
    answer = state["messages"][-1]
    return {"messages": [answer]}


def create_hierarchical_graph(
    teams: dict[str, GraphTeam], leader_name: str
) -> CompiledGraph:
    """Create the team's graph.

    This function creates a graph representation of the given teams. The graph is represented as a dictionary where each key is a team name,
    and the value is another dictionary containing the team's members, their roles, and tools.

    Args:
        teams (dict[str, dict[str, str | dict[str, Member | Leader]]]): A dictionary where each key is a team leader's name and the value is
            another dictionary containing the team's members.
        leader_name (str): The name of the root leader in the team.

    Returns:
        dict: A dictionary representing the graph of teams.
    """
    build = StateGraph(TeamState)
    # Add the start and end node
    build.add_node(
        leader_name,
        RunnableLambda(
            LeaderNode(
                teams[leader_name].provider,
                teams[leader_name].model,
                teams[leader_name].temperature,
            ).delegate
        ),
    )
    build.add_node(
        "FinalAnswer",
        RunnableLambda(
            SummariserNode(
                teams[leader_name].provider,
                teams[leader_name].model,
                teams[leader_name].temperature,
            ).summarise
        ),
    )

    members = teams[leader_name].members
    for name, member in members.items():
        if isinstance(member, GraphMember):
            build.add_node(
                name,
                RunnableLambda(
                    WorkerNode(
                        member.provider,
                        member.model,
                        member.temperature,
                    ).work
                ),
            )
        elif isinstance(member, GraphLeader):
            subgraph = create_hierarchical_graph(teams, leader_name=name)
            enter = partial(enter_chain, team=teams[name])
            build.add_node(name, enter | subgraph | exit_chain)
        else:
            continue
        build.add_edge(name, leader_name)

    conditional_mapping = {v: v for v in members}
    conditional_mapping["FINISH"] = "FinalAnswer"
    build.add_conditional_edges(leader_name, router, conditional_mapping)

    build.set_entry_point(leader_name)
    build.set_finish_point("FinalAnswer")
    graph = build.compile()
    return graph


def create_sequential_graph(team: dict[str, GraphMember]) -> CompiledGraph:
    """
    Creates a sequential graph from a list of team members.

    The graph will have a node for each team member, with edges connecting the nodes in the order the members are provided.
    The first member's node will be set as the entry point, and the last member's node will be connected to the END node.

    Args:
        team (List[Member]): A list of team members.

    Returns:
        CompiledGraph: The compiled graph representing the sequential workflow.
    """
    members: list[GraphMember] = []
    graph = StateGraph(TeamState)
    for i, member in enumerate(team.values()):
        graph.add_node(
            member.name,
            RunnableLambda(
                SequentialWorkerNode(
                    member.provider, member.model, member.temperature
                ).work
            ),
        )
        if i > 0:
            graph.add_edge(members[i - 1].name, member.name)
        members.append(member)
    graph.add_edge(members[-1].name, END)
    graph.set_entry_point(members[0].name)
    return graph.compile()


async def generator(
    team: Team, members: list[Member], messages: list[ChatMessage]
) -> AsyncGenerator[Any, Any]:
    """Create the graph and stream responses as JSON."""
    formatted_messages = [
        HumanMessage(content=message.content)
        if message.type == "human"
        else AIMessage(content=message.content)
        for message in messages
    ]

    if team.workflow == "hierarchical":
        teams = convert_hierarchical_team_to_dict(team, members)
        team_leader = list(teams.keys())[0]
        root = create_hierarchical_graph(teams, leader_name=team_leader)
        state = {
            "messages": formatted_messages,
            "team_name": teams[team_leader].name,
            "team_members": teams[team_leader].members,
        }
    else:
        member_dict = convert_sequential_team_to_dict(team)
        root = create_sequential_graph(member_dict)
        state = {
            "messages": formatted_messages,
            "team_name": team.name,
            "team_members": member_dict,
            "next": list(member_dict.values())[0].name,
        }
    # TODO: Figure out how to use async_stream to stream responses from subgraphs
    async for output in root.astream(state):
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
#         "model": "ChatOpenAI",
#         "members": {
#             "ChineseFoodExpert": {
#                 "type": "worker",
#                 "name": "ChineseFoodExpert",
#                 "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. ISFP.",
#                 "role": "Provide chinese food suggestions in Singapore",
#                 "tools": [],
#                 "model": "ChatOpenAI",
#             },
#             "MalayFoodExpert": {
#                 "type": "worker",
#                 "name": "MalayFoodExpert",
#                 "backstory": "Studied culinary school in Singapore. Well-verse in hawker to fine-dining experiences. INTP.",
#                 "role": "Provide malay food suggestions in Singapore",
#                 "tools": [],
#                 "model": "ChatOpenAI",
#             },
#         },
#     },
#     "TravelExpertLeader": {
#         "name": "TravelKakis",
#         "model": "ChatOpenAI",
#         "members": {
#             "FoodExpertLeader": {
#                 "type": "leader",
#                 "name": "FoodExpertLeader",
#                 "role": "Gather inputs from your team and provide a diverse food suggestions in Singapore.",
#                 "tools": [],
#                 "model": "ChatOpenAI",
#             },
#             "HistoryExpert": {
#                 "type": "worker",
#                 "name": "HistoryExpert",
#                 "backstory": "Studied Singapore history. Well-verse in Singapore architecture. INTJ.",
#                 "role": "Provide places to sight-see with a history/architecture angle",
#                 "tools": ["search"],
#                 "model": "ChatOpenAI",
#             },
#         },
#     },
# }

# teams = format_teams(teams)
# team_leader = "TravelExpertLeader"

# root = create_graph(teams, team_leader)

# messages = [HumanMessage("What is the best food in Singapore")]

# initial_state = {
#     "messages": messages,
#     "team_name": teams[team_leader].name,
#     "team_members": teams[team_leader].members,
# }


# async def main():
#     async for s in root.astream(initial_state):
#         if "__end__" not in s:
#             print(s)
#             print("----")


# main()
# # import asyncio

# # asyncio.run(main())
