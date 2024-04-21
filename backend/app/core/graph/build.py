from functools import partial
import json
from typing import Dict, List
from app.models import ChatMessage, Team
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.core.graph.members import Leader, LeaderNode, Member, SummariserNode, TeamState, WorkerNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda

model = ChatOpenAI(model="gpt-3.5-turbo")

def convert_team_to_dict(team: Team, members: list[Member]):
  """Convert team and members model to teams dict

  Args:
      team (Team): Team Model
      members (list[Member]): list of members model

  Raises:
      ValueError: Root leader not found

  Returns:
      dict: Dict containing the team and members
  """
  for member in members:
    if member.type == "root":
      # TODO: Find a better way to do this. Currently, Append team.id at end to ensure uniqueness
      root_leader = f'{member.name}-{team.id}'
      break

  if root_leader is None:
    raise ValueError("Root leader not found")

  teams = {
    root_leader: {
      "name": f'{team.name}-{team.id}',
      "members": {},
    }
  }

  for member in members:
    # TODO: Fix for leader
    if member.type == "worker":
      member_name = f'{member.name}-{team.id}'
      teams[root_leader]["members"][member_name] = {
        "type": member.type,
        "name": member_name,
        "backstory": member.backstory or "",
        "role": member.role,
        "tools": [],
      }
  
  return teams

# Create the Member/Leader class instance in members
def format_teams(teams: Dict[str, any]):
  """Update the team members to use Member/Leader"""
  for team in teams:
    members = teams[team]["members"]
    for k,v in members.items():
      teams[team]["members"][k] = Leader(**v) if v["type"] == "leader" else Member(**v)
  return teams

def router(state: TeamState):
    return state["next"]

def enter_chain(state: TeamState, team: Dict[str, str | List[Member | Leader]]):
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

def create_graph(teams: Dict[str, Dict[str, str | Dict[str, Member | Leader]]], leader_name: str):
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
  
  conditional_mapping = {v:v for v in members}
  conditional_mapping["FINISH"] = "summariser"
  build.add_conditional_edges(leader_name, router, conditional_mapping)

  build.set_entry_point(leader_name)
  build.set_finish_point("summariser")
  graph = build.compile()
  return graph



async def generator(team: Team, members: List[Member], messages: List[ChatMessage]):
    """Create the graph and stream responses as JSON."""
    teams = convert_team_to_dict(team, members)
    team_leader = list(teams.keys())[0]
    format_teams(teams)
    root = create_graph(teams, leader_name=team_leader)
    messages = [HumanMessage(message.content) if message.type == "human" else AIMessage(message.content) for message in messages]

    async for output in root.astream({
      "messages": messages,
      "team_name": teams[team_leader]["name"],
      "team_members": teams[team_leader]["members"]
    }):
      if "__end__" not in output:
        for key, value in output.items():
          if "task" in value:
            value["task"] = [message.dict() for message in  value["task"]]
          if "messages" in value:
            value["messages"] = [message.dict() for message in  value["messages"]]
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