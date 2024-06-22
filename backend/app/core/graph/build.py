import asyncio
import json
from collections import defaultdict, deque
from collections.abc import AsyncGenerator, Mapping
from functools import partial
from typing import Any

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import (
    ToolNode,
)

from app.core.config import settings
from app.core.graph.checkpoint.aiopostgres import AsyncPostgresSaver
from app.core.graph.members import (
    GraphLeader,
    GraphMember,
    GraphSkill,
    GraphTeam,
    GraphUpload,
    LeaderNode,
    SequentialWorkerNode,
    SummariserNode,
    TeamState,
    WorkerNode,
)
from app.models import ChatMessage, InterruptDecision, Member, Team


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
                name=leader_name,
                model=member.model,
                role=member.role,
                backstory=member.backstory or "",
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
                tools = [
                    GraphSkill(
                        name=skill.name,
                        managed=skill.managed,
                        definition=skill.tool_definition,
                    )
                    for skill in member.skills
                ]
                # TODO: Add description
                tools += [
                    GraphUpload(
                        name=upload.name,
                        description="",
                        owner_id=upload.owner_id,
                        upload_id=upload.id,
                    )
                    for upload in member.uploads
                ]
                teams[leader_name].members[member_name] = GraphMember(
                    name=member_name,
                    backstory=member.backstory or "",
                    role=member.role,
                    tools=tools,
                    provider=member.provider,
                    model=member.model,
                    temperature=member.temperature,
                    interrupt=member.interrupt,
                )
            elif member.type == "leader":
                teams[leader_name].members[member_name] = GraphLeader(
                    name=member_name,
                    backstory=member.backstory or "",
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


def convert_sequential_team_to_dict(team: Team) -> Mapping[str, GraphMember]:
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
        tools = [
            GraphSkill(
                name=skill.name,
                managed=skill.managed,
                definition=skill.tool_definition,
            )
            for skill in member.skills
        ]
        # TODO: Add description
        tools += [
            GraphUpload(
                name=upload.name,
                description="",
                owner_id=upload.owner_id,
                upload_id=upload.id,
            )
            for upload in member.uploads
        ]
        graph_member = GraphMember(
            name=memberModel.name,
            backstory=memberModel.backstory or "",
            role=memberModel.role,
            tools=tools,
            provider=memberModel.provider,
            model=memberModel.model,
            temperature=memberModel.temperature,
            interrupt=memberModel.interrupt,
        )
        team_dict[graph_member.name] = graph_member
        for nei_id in out_counts[member_id]:
            in_counts[nei_id] -= 1
            if in_counts[nei_id] == 0:
                queue.append(nei_id)
    return team_dict


def router(state: TeamState) -> str:
    return state["next"]


def enter_chain(state: TeamState, team: GraphTeam) -> dict[str, Any]:
    """
    Initialise the sub-graph state.
    This makes it so that the states of each graph don't get intermixed.
    """
    task = state["task"]
    results = {
        "main_task": task,
        "team": team,
        "team_members": team.members,
    }
    return results


def exit_chain(state: TeamState) -> dict[str, list[AnyMessage]]:
    """
    Pass the final response back to the top-level graph's state.
    """
    answer = state["messages"][-1]
    return {"messages": [answer]}


def should_continue(state: TeamState) -> str:
    """Determine if graph should go to tool node or not. For tool calling agents."""
    messages: list[AnyMessage] = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return "continue"
    # Otherwise if there is, we continue
    else:
        return "call_tools"


def create_tools_condition(
    current_member_name: str, next_member_name: str
) -> dict[str, str]:
    """Creates the mapping for conditional edges
    The tool node must be in format: '{current_member_name}_tools'

    Args:
        current_member_name (str): The name of the member that is calling the tool
        next_member_name (str): The name of the next member after the current member processes the tool response. Can be END.
    """
    return {
        # If `tools`, then we call the tool node.
        "call_tools": f"{current_member_name}_tools",
        # Else continue to the next node
        "continue": next_member_name,
    }


def create_hierarchical_graph(
    teams: dict[str, GraphTeam],
    leader_name: str,
    memory: BaseCheckpointSaver | None = None,
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
    # Create a list to store member names that require human intervention before tool calling
    interrupt_member_names = []
    # Add the start and end node
    build.add_node(
        leader_name,
        RunnableLambda(
            LeaderNode(
                teams[leader_name].provider,
                teams[leader_name].model,
                teams[leader_name].temperature,
            ).delegate  # type: ignore[arg-type]
        ),
    )
    build.add_node(
        "FinalAnswer",
        RunnableLambda(
            SummariserNode(
                teams[leader_name].provider,
                teams[leader_name].model,
                teams[leader_name].temperature,
            ).summarise  # type: ignore[arg-type]
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
                    ).work  # type: ignore[arg-type]
                ),
            )
            # if member can call tools, then add tool node
            if len(member.tools) >= 1:
                build.add_node(
                    f"{name}_tools",
                    ToolNode([tool.tool for tool in member.tools]),
                )
                # After tools node is called, agent node is called next.
                build.add_edge(f"{name}_tools", name)
                # Check if member requires human intervention before tool calling
                if member.interrupt:
                    interrupt_member_names.append(f"{name}_tools")
        elif isinstance(member, GraphLeader):
            # subgraphs do not require memory
            subgraph = create_hierarchical_graph(teams, leader_name=name, memory=None)
            enter = partial(enter_chain, team=teams[name])
            build.add_node(
                name,
                enter | subgraph | exit_chain,
            )
        else:
            continue
        # If member has tools, we create conditional edge to either tool node or back to leader.
        if isinstance(member, GraphMember) and len(member.tools) >= 1:
            build.add_conditional_edges(
                name, should_continue, create_tools_condition(name, leader_name)
            )
            # Check if member requires human intervention before tool calling
            if member.interrupt:
                interrupt_member_names.append(f"{member.name}_tools")
        else:
            build.add_edge(name, leader_name)
    conditional_mapping = {v: v for v in members}
    conditional_mapping["FINISH"] = "FinalAnswer"
    build.add_conditional_edges(leader_name, router, conditional_mapping)

    build.set_entry_point(leader_name)
    build.set_finish_point("FinalAnswer")
    graph = build.compile(checkpointer=memory, interrupt_before=interrupt_member_names)
    return graph


def create_sequential_graph(
    team: Mapping[str, GraphMember], memory: BaseCheckpointSaver
) -> CompiledGraph:
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
    # Create a list to store member names that require human intervention before tool calling
    interrupt_member_names = []
    for i, member in enumerate(team.values()):
        graph.add_node(
            member.name,
            RunnableLambda(
                SequentialWorkerNode(
                    member.provider, member.model, member.temperature
                ).work  # type: ignore[arg-type]
            ),
        )
        # if member can call tools, then add tool node
        if len(member.tools) >= 1:
            graph.add_node(
                f"{member.name}_tools",
                ToolNode([tool.tool for tool in member.tools]),
            )
            # After tools node is called, agent node is called next.
            graph.add_edge(f"{member.name}_tools", member.name)
            # Check if member requires human intervention before tool calling
            if member.interrupt:
                interrupt_member_names.append(f"{member.name}_tools")
        if i > 0:
            # if previous member has tools, then the edge should conditionally call tool node
            if len(members[i - 1].tools) >= 1:
                graph.add_conditional_edges(
                    members[i - 1].name,
                    should_continue,
                    create_tools_condition(members[i - 1].name, member.name),
                )
            else:
                graph.add_edge(members[i - 1].name, member.name)
        members.append(member)
    # Add the conditional edges for the final node if it uses tools
    if len(members[-1].tools) >= 1:
        graph.add_conditional_edges(
            members[-1].name,
            should_continue,
            create_tools_condition(members[-1].name, END),
        )
    else:
        graph.add_edge(members[-1].name, END)
    graph.set_entry_point(members[0].name)
    return graph.compile(checkpointer=memory, interrupt_before=interrupt_member_names)


def convert_messages_and_tasks_to_dict(data: Any) -> Any:
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if key == "messages" or key == "task":
                if isinstance(value, list):
                    new_data[key] = [message.dict() for message in value]
                else:
                    new_data[key] = value
            else:
                new_data[key] = convert_messages_and_tasks_to_dict(value)
        return new_data
    elif isinstance(data, list):
        return [convert_messages_and_tasks_to_dict(item) for item in data]
    else:
        return data


async def generator(
    team: Team,
    members: list[Member],
    messages: list[ChatMessage],
    thread_id: str,
    interrupt_decision: InterruptDecision | None = None,
) -> AsyncGenerator[Any, Any]:
    """Create the graph and stream responses as JSON."""
    formatted_messages = [
        # Current only one message is passed - the user's query.
        HumanMessage(content=message.content, name="user")
        if message.type == "human"
        else AIMessage(content=message.content)
        for message in messages
    ]

    try:
        memory = await AsyncPostgresSaver.from_conn_string(settings.PG_DATABASE_URI)

        if team.workflow == "hierarchical":
            teams = convert_hierarchical_team_to_dict(team, members)
            team_leader = list(teams.keys())[0]
            root = create_hierarchical_graph(
                teams, leader_name=team_leader, memory=memory
            )
            state: dict[str, Any] | None = {
                "messages": formatted_messages,
                "team": teams[team_leader],
                "main_task": formatted_messages,
            }
        else:
            member_dict = convert_sequential_team_to_dict(team)
            root = create_sequential_graph(member_dict, memory)
            first_member = list(member_dict.values())[0]
            state = {
                "messages": formatted_messages,
                "team": GraphTeam(
                    name=first_member.name,
                    role=first_member.role,
                    backstory=first_member.backstory,
                    members=member_dict,  # type: ignore[arg-type]
                    provider=first_member.provider,
                    model=first_member.model,
                    temperature=first_member.temperature,
                ),
                "next": first_member.name,
            }

        config: RunnableConfig = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 25,
        }
        # Handle interrupt logic by orriding state
        if interrupt_decision == InterruptDecision.APPROVED:
            state = None
        elif interrupt_decision == InterruptDecision.REJECTED:
            current_values = await root.aget_state(config)
            tool_calls = current_values.values["messages"][-1].tool_calls
            state = {
                "messages": [
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content="API call denied by user. Continue assisting.",
                    )
                    for tool_call in tool_calls
                ]
            }

        async for output in root.astream_events(
            state,
            version="v1",
            include_names=["work", "delegate", "summarise"],
            config=config,
        ):
            if output["event"] == "on_chain_end":
                output_data = output["data"]["output"]
                transformed_output_data = convert_messages_and_tasks_to_dict(
                    output_data
                )
                formatted_output = f"data: {json.dumps(transformed_output_data)}\n\n"
                if formatted_output != "data: null\n\n":
                    yield formatted_output
        snapshot = await root.aget_state(config)
        if snapshot.next:
            # Interrupt occured
            yield f"data: {json.dumps({'interrupt': True})}\n\n"
    except Exception as e:
        error_message = {
            "error": str(e),
            "details": "An error occurred during streaming.",
        }
        yield f"data: {json.dumps(error_message)}\n\n"
        await asyncio.sleep(0.1)  # Add a small delay to ensure the message is sent
        raise e
