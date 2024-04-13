from typing import Annotated, Dict, List, TypedDict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from app.core.graph.tools import all_tools
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from pydantic import BaseModel, Field
import operator

class Person(BaseModel):
  name: str = Field(description="The name of the person")
  role: str = Field(description="Role of the person")
  
class Member(Person):
  backstory: str = Field(description="Description of the person's experience, motives and concerns.")
  tools: List[str] = Field(description="The list of tools that the person can use.")
  @property
  def persona(self) -> str:
      return f"Name: {self.name}\nRole: {self.role}\nBackstory: {self.backstory}\n"

# Create a Leader class so we can pass leader as a team member for team within team
class Leader(Person):
  pass

def update_name(name: str, new_name: str):
  """Update name at the onset."""
  if not name:
    return new_name
  return name

def update_members(members: Dict[str, Member | Leader] | None, new_members: Dict[str, Member | Leader]):
  """Update members at the onset"""
  if not members:
    members = {}
  members.update(new_members) 
  return members

class TeamState(TypedDict):
  messages: Annotated[List[BaseMessage], operator.add]
  team_name: Annotated[str, update_name]
  team_members: Annotated[Dict[str, Member | Leader], update_members] 
  next: str
  task: List[BaseMessage] # This is the current task to be perform by a team member. Its a list because Worker's MessagesPlaceholder only accepts list of messages.
  
class BaseNode:
  def __init__(self, model: ChatOpenAI):
    self.model = model
    
  def tag_with_name(self, ai_message: AIMessage, name: str):
    """Tag a name to the AI message"""
    ai_message.name = name
    return ai_message
  
  
  

class WorkerNode(BaseNode):
  worker_prompt = ChatPromptTemplate.from_messages(
    [
      (
        "system", """You are a team member of {team_name} and you are one of the following team members: {team_members}.
        Your team members (and other teams) will collaborate with you with their own set of skills.
        You are chosen by one of your team member to perform this task. Try your best to perform it using your skills.
        Stay true to your perspective:
        {persona}"""
      ),
      MessagesPlaceholder(variable_name="task"),
      MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
  )
  
  def convert_output_to_ai_message(self, state: TeamState):
    """Convert agent executor output to ai message"""
    output = state["output"]
    return AIMessage(content=output)

  def create_agent(self, llm: ChatOpenAI, prompt: ChatPromptTemplate, tools: List[str]):
    """Create the agent executor"""
    tools = [all_tools[tool] for tool in tools]
    # Tools cannot be empty, add a placeholder
    if len(tools) < 1:
      tools = [all_tools["nothing"]]
    agent = create_openai_functions_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

  async def work(self, state: TeamState):
    name = state["next"]
    member = state["team_members"][name]
    tools = member.tools
    prompt = self.worker_prompt.partial(persona=member.persona)
    agent = self.create_agent(self.model, prompt, tools)
    work_chain = (
        agent
        | RunnableLambda(self.convert_output_to_ai_message)
        | RunnableLambda(self.tag_with_name).bind(name=member.name)
    )
    result = await work_chain.ainvoke(state)
    return {"messages": [result]}


class LeaderNode(BaseNode):
  leader_prompt = ChatPromptTemplate.from_messages([
      (
          "system", """You are the team leader of {team_name} and you have the following team members: {team_members}.
      Your team is given a task and you have to delegate the work among your team members based on their skills.
      Team member info:
      {team_members_info}"""
      ),
      MessagesPlaceholder(variable_name="messages"),
      (
          "system", "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}."
      )
  ])

  def get_team_members_info(self, team_members: List[Member]):
    """Create a string containing team members name and role."""
    result = ""
    for member in team_members.values():
      result += f"name: {member.name}\nrole: {member.role}\n\n"
    return result

  def get_tool_definition(self, options: List[str]):
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
              "description": "Provide the task to the team member."
            },
          },
          "required": ["next", "task"],
        }
      }
    }

  async def delegate(self, state: TeamState):
    team_members = ", ".join(state["team_members"])
    team_name = state["team_name"]
    team_members_info = self.get_team_members_info(state["team_members"])
    options = list(state["team_members"]) + ["FINISH"]

    delegate_chain = (
        self.leader_prompt.partial(team_name=team_name, team_members=team_members, team_members_info=team_members_info, options=str(options))
        | self.model.bind_tools([self.get_tool_definition(options)])
        | JsonOutputKeyToolsParser(key_name="route", first_tool_only=True)
    )
    result = await delegate_chain.ainvoke(state)
    # Convert task from string to List[HumanMessage] because Worker's MessagesPlaceholder only accepts list of messages.
    result["task"] = [HumanMessage(content=result.get("task", "None"), name=team_name)]
    return result


class SummariserNode(BaseNode):
  summariser_prompt = ChatPromptTemplate.from_messages([
      (
          "system", """You are a team member of {team_name} and you have the following team members: {team_members}.
          Your team was given a task and your team members have performed their roles and returned their responses to the team leader.
          Your role as a Summariser is to summarise the responses by your team members and give the final answer.
          Here is the team's task:
          {team_task}
          
          These are the responses from your team members:
          {team_responses}"""
      )
  ])

  def get_team_responses(self, messages: List[BaseMessage]):
    """Create a string containing the team's responses."""
    result = ""
    for message in messages:
      result += f"{message.name}: {message.content}\n"
    return result

  async def summarise(self, state: TeamState):
    team_members = ", ".join(state["team_members"])
    team_name = state["team_name"]
    team_responses = self.get_team_responses(state["messages"])
    team_task = state["messages"][0].content

    summarise_chain = (
        self.summariser_prompt.partial(team_name=team_name, team_members=team_members, team_task=team_task, team_responses=team_responses)
        | self.model
        | RunnableLambda(self.tag_with_name).bind(name="summariser")
    )
    result = await summarise_chain.ainvoke(state)
    return {"messages": [result]}