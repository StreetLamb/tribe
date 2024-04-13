from functools import partial
from typing import Dict, List
from app.models import ChatMessage
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.core.graph.members import Leader, LeaderNode, Member, SummariserNode, TeamState, WorkerNode
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda

model = ChatOpenAI(model="gpt-3.5-turbo")

# Create the Member/Leader class instance in members
def format_teams(teams: Dict[str, any]):
  """Update the team members to use Member/Leader"""
  for team in teams:
    members = teams[team]["members"]
    for k,v in members.items():
      print(v)
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



async def generator(teams: dict, team_leader: str, messages: List[ChatMessage]):
    """Create the graph and strem the response"""
    format_teams(teams)
    root = create_graph(teams, leader_name=team_leader)
    messages = [HumanMessage(message.content) if message.type == "human" else AIMessage(message.content) for message in messages]

    async for output in root.astream({
        "messages": messages,
        "team_name": teams[team_leader]["name"],
        "team_members": teams[team_leader]["members"]
    }):
        for key, value in output.items():
            if key != "__end__":
                response = {key :value}
                formatted_output = f"data: {response}\n\n"
                print(formatted_output)
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