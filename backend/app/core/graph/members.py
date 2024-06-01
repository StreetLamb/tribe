import operator
from collections.abc import Sequence
from typing import Annotated, Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableSerializable
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing_extensions import NotRequired, TypedDict

from app.core.graph.models import all_models
from app.core.graph.skills import all_skills


class GraphPerson(BaseModel):
    name: str = Field(description="The name of the person")
    role: str = Field(description="Role of the person")
    provider: str = Field(description="The provider for the llm model")
    model: str = Field(description="The llm model to use for this person")
    temperature: float = Field(description="The temperature of the llm model")


class GraphMember(GraphPerson):
    backstory: str = Field(
        description="Description of the person's experience, motives and concerns."
    )
    tools: list[str] = Field(description="The list of tools that the person can use.")
    interrupt: bool = Field(
        default=False,
        description="Whether to interrupt the person or not before skill use",
    )

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nBackstory: {self.backstory}\n"


# Create a Leader class so we can pass leader as a team member for team within team
class GraphLeader(GraphPerson):
    pass


class GraphTeam(BaseModel):
    name: str = Field(description="The name of the team")
    members: dict[str, GraphMember | GraphLeader] = Field(
        description="The members of the team"
    )
    provider: str = Field(description="The provider of the team leader's llm model")
    model: str = Field(description="The llm model to use for this team leader")
    temperature: float = Field(
        description="The temperature of the team leader's llm model"
    )


def update_name(name: str, new_name: str) -> str:
    """Update name at the onset."""
    if not name:
        return new_name
    return name


def update_members(
    members: dict[str, GraphMember | GraphLeader] | None,
    new_members: dict[str, GraphMember | GraphLeader],
) -> dict[str, GraphMember | GraphLeader]:
    """Update members at the onset"""
    if not members:
        members = {}
    members.update(new_members)
    return members


class TeamState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    team_name: Annotated[str, update_name]
    team_members: Annotated[dict[str, GraphMember | GraphLeader], update_members]
    next: str
    task: list[
        BaseMessage
    ]  # This is the current task to be perform by a team member. Its a list because Worker's MessagesPlaceholder only accepts list of messages.


# When returning teamstate, is it possible to exclude fields that you dont want to update
class ReturnTeamState(TypedDict):
    messages: list[BaseMessage]
    team_name: NotRequired[str]
    team_members: NotRequired[dict[str, GraphMember | GraphLeader]]
    next: NotRequired[str | None]  # Returning None is valid for sequential graphs only
    task: NotRequired[list[BaseMessage]]


class BaseNode:
    def __init__(self, provider: str, model: str, temperature: float):
        self.model = all_models[provider](model=model, temperature=temperature)  # type: ignore[call-arg]
        self.final_answer_model = all_models[provider](model=model, temperature=0)  # type: ignore[call-arg]

    def tag_with_name(self, ai_message: AIMessage, name: str) -> AIMessage:
        """Tag a name to the AI message"""
        ai_message.name = name
        return ai_message

    def get_team_members_name(
        self, team_members: dict[str, GraphMember | GraphLeader]
    ) -> str:
        """Get the names of all team members as a string"""
        return ",".join(list(team_members))


class WorkerNode(BaseNode):
    worker_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a team member of {team_name} and you are one of the following team members: {team_members_name}.\n"
                    "Your team members (and other teams) will collaborate with you with their own set of skills. "
                    "You are chosen by one of your team member to perform this task. Try your best to perform it using your skills. "
                    "Stay true to your persona and role:\n"
                    "{persona}"
                    "\nBEGIN!\n"
                ),
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="task"),
        ]
    )

    def convert_output_to_ai_message(self, agent_output: dict[str, str]) -> AIMessage:
        """Convert agent executor output to ai message"""
        output = agent_output["output"]
        return AIMessage(content=output)

    async def work(self, state: TeamState) -> ReturnTeamState:
        name = state["next"]
        member = state["team_members"][name]
        assert isinstance(member, GraphMember), "member is unexpectedly not a Member"
        team_members_name = self.get_team_members_name(state["team_members"])
        prompt = self.worker_prompt.partial(
            team_members_name=team_members_name,
            persona=member.persona,
        )
        # If member has no tools, then use a regular model instead of an agent
        if len(member.tools) >= 1:
            tools: Sequence[BaseTool] = [all_skills[tool].tool for tool in member.tools]
            chain = prompt | self.model.bind_tools(tools)
        else:
            chain: RunnableSerializable[dict[str, Any], BaseMessage] = (  # type: ignore[no-redef]
                prompt | self.model
            )
        work_chain: RunnableSerializable[dict[str, Any], Any] = chain | RunnableLambda(
            self.tag_with_name  # type: ignore[arg-type]
        ).bind(name=member.name)
        result = await work_chain.ainvoke(state)  # type: ignore[arg-type]
        return {"messages": [result]}


class SequentialWorkerNode(WorkerNode):
    """Perform Sequential Worker actions"""

    worker_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                (
                    "Perform the task given to you.\n"
                    "If you are unable to perform the task, that's OK, another member with different tools "
                    "will help where you left off. Do not attempt to communicate with other members. "
                    "Execute what you can to make progress. "
                    "Stay true to your persona and role:\n"
                    "{persona}"
                    "\nBEGIN!\n"
                ),
            ),
        ]
    )

    def get_next_member_in_sequence(
        self, members: dict[str, GraphMember | GraphLeader], current_name: str
    ) -> str | None:
        member_names = list(members.keys())
        next_index = member_names.index(current_name) + 1
        if next_index < len(members):
            return member_names[member_names.index(current_name) + 1]
        else:
            return None

    async def work(self, state: TeamState) -> ReturnTeamState:
        name = state["next"]
        member = state["team_members"][name]
        assert isinstance(member, GraphMember), "member is unexpectedly not a Member"
        team_members_name = self.get_team_members_name(state["team_members"])
        prompt = self.worker_prompt.partial(
            team_members_name=team_members_name,
            persona=member.persona,
        )
        # If member has no tools, then use a regular model instead of an agent
        if len(member.tools) >= 1:
            tools: Sequence[BaseTool] = [all_skills[tool].tool for tool in member.tools]
            chain = prompt | self.model.bind_tools(tools)
        else:
            chain: RunnableSerializable[dict[str, Any], BaseMessage] = (  # type: ignore[no-redef]
                prompt | self.model
            )
        work_chain: RunnableSerializable[dict[str, Any], Any] = chain | RunnableLambda(
            self.tag_with_name  # type: ignore[arg-type]
        ).bind(name=member.name)
        result: AIMessage = await work_chain.ainvoke(state)  # type: ignore[arg-type]
        # if agent is calling a tool, set the next member_name to be itself. This is so that when an agent triggers a
        # tool and the tool returns the response back, the next value will be the agent's name
        next: str | None
        if result.tool_calls:
            next = name
        else:
            next = self.get_next_member_in_sequence(state["team_members"], name)
        return {"messages": [result], "next": next}


class LeaderNode(BaseNode):
    leader_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                (
                    "You are the team leader of {team_name} and you have the following team members: {team_members_name}.\n"
                    "Your team is given a task and you have to delegate the work among your team members based on their skills.\n"
                    "Team member info:\n\n"
                    "{team_members_info}"
                ),
            ),
            (
                "system",
                "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}.",
            ),
        ]
    )

    def get_team_members_info(
        self, team_members: dict[str, GraphMember | GraphLeader]
    ) -> str:
        """Create a string containing team members name and role."""
        result = ""
        for member in team_members.values():
            result += f"name: {member.name}\nrole: {member.role}\n\n"
        return result

    def get_tool_definition(self, options: list[str]) -> dict[str, Any]:
        """Return the tool definition to choose next team member and provide the task."""
        return {
            "type": "function",
            "function": {
                "name": "route",
                "description": "Select the next role.",
                "parameters": {
                    "title": "routeSchema",
                    "type": "object",
                    "properties": {
                        "next": {
                            "title": "Next",
                            "anyOf": [
                                {"enum": options},
                            ],
                        },
                        "task": {
                            "title": "task",
                            "description": "Provide the task to the team member.",
                        },
                    },
                    "required": ["next", "task"],
                },
            },
        }

    async def delegate(self, state: TeamState) -> dict[str, Any]:
        team_members_name = self.get_team_members_name(state["team_members"])
        team_name = state["team_name"]
        team_members_info = self.get_team_members_info(state["team_members"])
        options = list(state["team_members"]) + ["FINISH"]
        tools = [self.get_tool_definition(options)]

        delegate_chain: RunnableSerializable[Any, Any] = (
            self.leader_prompt.partial(
                team_name=team_name,
                team_members_name=team_members_name,
                team_members_info=team_members_info,
                options=str(options),
            )
            | self.model.bind_tools(tools=tools)
            | JsonOutputKeyToolsParser(key_name="route", first_tool_only=True)
        )
        result: dict[str, Any] = await delegate_chain.ainvoke(state)
        if not result:
            return {
                "task": [HumanMessage(content="No further tasks.", name=team_name)],
                "next": "FINISH",
            }
        else:
            task_content = result.get("task", "No further tasks.")
            # Ensure the task content is a string
            if isinstance(task_content, list):
                task_content = "\n".join(task_content)
            elif not isinstance(task_content, str):
                task_content = str(task_content)

            result["task"] = [HumanMessage(content=task_content, name=team_name)]
            return result


class SummariserNode(BaseNode):
    summariser_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a team member of {team_name} and you have the following team members: {team_members_name}. "
                    "Your team was given a task and your team members have performed their roles and returned their responses to the team leader.\n\n"
                    "Here is the team's task:\n"
                    "'''\n"
                    "{team_task}\n"
                    "'''\n\n"
                    "These are the responses from your team members:\n"
                    "'''\n"
                    "{team_responses}\n"
                    "'''\n\n"
                    "Your role is to interpret all the responses and give the final answer to the team's task.\n"
                ),
            )
        ]
    )

    def get_team_responses(self, messages: list[BaseMessage]) -> str:
        """Create a string containing the team's responses."""
        result = ""
        for message in messages:
            result += f"{message.name}: {message.content}\n"
        return result

    async def summarise(self, state: TeamState) -> dict[str, list[BaseMessage]]:
        team_members_name = self.get_team_members_name(state["team_members"])
        team_name = state["team_name"]
        team_responses = self.get_team_responses(state["messages"])
        # TODO: optimise looking for task
        # The most recent human message is the team's most recent task
        team_task = ""
        for message in state["messages"][::-1]:
            if isinstance(message, HumanMessage) and isinstance(message.content, str):
                team_task = message.content
                break

        summarise_chain: RunnableSerializable[Any, Any] = (
            self.summariser_prompt.partial(
                team_name=team_name,
                team_members_name=team_members_name,
                team_task=team_task,
                team_responses=team_responses,
            )
            | self.final_answer_model
            | RunnableLambda(self.tag_with_name).bind(name=f"{team_name}_answer")  # type: ignore[arg-type]
        )
        result = await summarise_chain.ainvoke(state)
        return {"messages": [result]}
