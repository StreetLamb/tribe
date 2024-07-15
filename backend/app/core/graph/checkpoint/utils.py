from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.base import CheckpointTuple
from psycopg import AsyncConnection

from app.core.config import settings
from app.core.graph.checkpoint.postgres import PostgresSaver
from app.models import GraphResponse


def convert_checkpoint_tuple_to_messages(
    checkpoint_tuple: CheckpointTuple,
) -> list[GraphResponse]:
    """
    Convert a checkpoint tuple to a list of GraphResponse messages.

    Args:
        checkpoint_tuple (CheckpointTuple): The checkpoint tuple to convert.

    Returns:
        list[GraphResponse]: A list of formatted messages.
    """
    checkpoint = checkpoint_tuple.checkpoint
    all_messages = checkpoint["channel_values"]["all_messages"]
    formatted_messages: list[GraphResponse] = []
    for message in all_messages:
        if (
            isinstance(message, AIMessage) or isinstance(message, HumanMessage)
        ) and message.content:
            formatted_messages.append(
                GraphResponse(
                    kind="on_chat_model_stream",
                    id=message.id,
                    name=message.name,
                    content=message.content,
                    parent_ids=[],
                )
            )
        elif isinstance(message, AIMessage) and message.tool_calls:
            for tool_call in message.tool_calls:
                formatted_messages.append(
                    GraphResponse(
                        kind="on_tool_start",
                        id=tool_call["id"],
                        name=tool_call["name"],
                        content=tool_call["args"],
                        parent_ids=[],
                    )
                )
        elif isinstance(message, ToolMessage):
            formatted_messages.append(
                GraphResponse(
                    kind="on_tool_end",
                    id=message.id,
                    name=message.name,
                    content=message.content,
                    parent_ids=[message.tool_call_id],
                )
            )
        else:
            continue
    return formatted_messages


async def get_checkpoint_tuples(thread_id: str):
    """
    Retrieve the latest checkpoint tuple for a given thread ID.

    Args:
        thread_id (str): The ID of the thread.

    Returns:
        CheckpointTuple: The latest checkpoint tuple.
    """
    async with await AsyncConnection.connect(settings.PG_DATABASE_URI) as conn:
        checkpointer = PostgresSaver(async_connection=conn)
        checkpoint_tuple = await checkpointer.aget_tuple(
            {"configurable": {"thread_id": thread_id}}
        )
        return checkpoint_tuple
