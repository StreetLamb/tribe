import asyncio
import functools
from collections.abc import AsyncIterator, Iterator
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import TypeVar

import asyncpg
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    SerializerProtocol,
)
from typing_extensions import Self

from app.core.graph.checkpoint.postgres import JsonPlusSerializerCompat, search_where

T = TypeVar("T", bound=callable)


def not_implemented_sync_method(func: T) -> T:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        raise NotImplementedError(
            "The AsyncPostgresSaver does not support synchronous methods. "
            "Consider using the PostgresSaver instead.\n"
            "from langgraph.checkpoint.postgres import PostgresSaver\n"
            "See https://langchain-ai.github.io/langgraph/reference/checkpoints/#postgressaver "
            "for more information."
        )

    return wrapper


class AsyncPostgresSaver(BaseCheckpointSaver, AbstractAsyncContextManager):
    """An asynchronous checkpoint saver that stores checkpoints in a PostgreSQL database.

    Tip:
        Requires the [asyncpg](https://pypi.org/project/asyncpg/) package.
        Install it with `pip install asyncpg`.

    Args:
        conn (asyncpg.Connection): The asynchronous PostgreSQL database connection.
        serde (Optional[SerializerProtocol]): The serializer to use for serializing and deserializing checkpoints. Defaults to JsonPlusSerializerCompat.

    Examples:
        Usage within a StateGraph:
        ```pycon
        >>> import asyncio
        >>> import asyncpg
        >>>
        >>> from langgraph.checkpoint.postgres import AsyncPostgresSaver
        >>> from langgraph.graph import StateGraph
        >>>
        >>> builder = StateGraph(int)
        >>> builder.add_node("add_one", lambda x: x + 1)
        >>> builder.set_entry_point("add_one")
        >>> builder.set_finish_point("add_one")
        >>> memory = AsyncPostgresSaver.from_conn_string("postgresql://user:password@localhost/dbname")
        >>> graph = builder.compile(checkpointer=memory)
        >>> coro = graph.ainvoke(1, {"configurable": {"thread_id": "thread-1"}})
        >>> asyncio.run(coro)
        Output: 2
        ```

        Raw usage:
        ```pycon
        >>> import asyncio
        >>> import asyncpg
        >>> from langgraph.checkpoint.postgres import AsyncPostgresSaver
        >>>
        >>> async def main():
        >>>     conn = await asyncpg.connect("postgresql://user:password@localhost/dbname")
        ...     saver = AsyncPostgresSaver(conn)
        ...     config = {"configurable": {"thread_id": "1"}}
        ...     checkpoint = {"ts": "2023-05-03T10:00:00Z", "data": {"key": "value"}}
        ...     saved_config = await saver.aput(config, checkpoint)
        ...     print(saved_config)
        >>> asyncio.run(main())
        {"configurable": {"thread_id": "1", "thread_ts": "2023-05-03T10:00:00Z"}}
        ```
    """

    serde = JsonPlusSerializerCompat()

    conn: asyncpg.Connection
    lock: asyncio.Lock
    is_setup: bool

    def __init__(
        self,
        conn: asyncpg.Connection,
        *,
        serde: SerializerProtocol | None = None,
    ):
        super().__init__(serde=serde)
        self.conn = conn
        self.lock = asyncio.Lock()
        self.is_setup = False

    @classmethod
    async def from_conn_string(cls, conn_string: str) -> "AsyncPostgresSaver":
        """Create a new AsyncPostgresSaver instance from a connection string.

        Args:
            conn_string (str): The PostgreSQL connection string.

        Returns:
            AsyncPostgresSaver: A new AsyncPostgresSaver instance.
        """
        conn = await asyncpg.connect(conn_string)
        return AsyncPostgresSaver(conn=conn)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        if self.is_setup:
            await self.conn.close()
        return None

    @not_implemented_sync_method
    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Get a checkpoint tuple from the database.

        Note:
            This method is not implemented for the AsyncPostgresSaver. Use `aget` instead.
            Or consider using the [PostgresSaver](#postgressaver) checkpointer.
        """

    @not_implemented_sync_method
    def list(
        self,
        config: RunnableConfig,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        Note:
            This method is not implemented for the AsyncPostgresSaver. Use `alist` instead.
            Or consider using the [PostgresSaver](#postgressaver) checkpointer.
        """

    @not_implemented_sync_method
    def search(
        self,
        metadata_filter: CheckpointMetadata,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]:
        """Search for checkpoints by metadata.

        Note:
            This method is not implemented for the AsyncPostgresSaver. Use `asearch` instead.
            Or consider using the [PostgresSaver](#postgressaver) checkpointer.
        """

    @not_implemented_sync_method
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        """Save a checkpoint to the database."""

    async def setup(self) -> None:
        """Set up the checkpoint database asynchronously.

        This method creates the necessary tables in the PostgreSQL database if they don't
        already exist. It is called automatically when needed and should not be called
        directly by the user.
        """
        async with self.lock:
            if self.is_setup:
                return

            await self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    thread_id TEXT NOT NULL,
                    thread_ts TEXT NOT NULL,
                    parent_ts TEXT,
                    checkpoint BYTEA,
                    metadata BYTEA,
                    PRIMARY KEY (thread_id, thread_ts)
                );
                """
            )

            self.is_setup = True

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Get a checkpoint tuple from the database asynchronously.

        This method retrieves a checkpoint tuple from the PostgreSQL database based on the
        provided config. If the config contains a "thread_ts" key, the checkpoint with
        the matching thread ID and timestamp is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        await self.setup()
        if config["configurable"].get("thread_ts"):
            result = await self.conn.fetchrow(
                "SELECT checkpoint, parent_ts, metadata FROM checkpoints WHERE thread_id = $1 AND thread_ts = $2",
                str(config["configurable"]["thread_id"]),
                str(config["configurable"]["thread_ts"]),
            )
            if result:
                return CheckpointTuple(
                    config,
                    self.serde.loads(result["checkpoint"]),
                    self.serde.loads(result["metadata"]) if result["metadata"] else {},
                    (
                        {
                            "configurable": {
                                "thread_id": config["configurable"]["thread_id"],
                                "thread_ts": result["parent_ts"],
                            }
                        }
                        if result["parent_ts"]
                        else None
                    ),
                )
        else:
            result = await self.conn.fetchrow(
                "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = $1 ORDER BY thread_ts DESC LIMIT 1",
                str(config["configurable"]["thread_id"]),
            )
            if result:
                return CheckpointTuple(
                    {
                        "configurable": {
                            "thread_id": result["thread_id"],
                            "thread_ts": result["thread_ts"],
                        }
                    },
                    self.serde.loads(result["checkpoint"]),
                    self.serde.loads(result["metadata"]) if result["metadata"] else {},
                    (
                        {
                            "configurable": {
                                "thread_id": result["thread_id"],
                                "thread_ts": result["parent_ts"],
                            }
                        }
                        if result["parent_ts"]
                        else None
                    ),
                )

    async def alist(
        self,
        config: RunnableConfig,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints from the database asynchronously.

        This method retrieves a list of checkpoint tuples from the PostgreSQL database based
        on the provided config. The checkpoints are ordered by timestamp in descending order.

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified timestamp are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            AsyncIterator[CheckpointTuple]: An asynchronous iterator of checkpoint tuples.
        """
        await self.setup()
        query = (
            "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = $1 ORDER BY thread_ts DESC"
            if before is None
            else "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = $1 AND thread_ts < $2 ORDER BY thread_ts DESC"
        )
        if limit:
            query += f" LIMIT {limit}"
        params = (
            (str(config["configurable"]["thread_id"]),)
            if before is None
            else (
                str(config["configurable"]["thread_id"]),
                str(before["configurable"]["thread_ts"]),
            )
        )
        async with self.conn.transaction():
            async for record in self.conn.cursor(query, *params):
                yield CheckpointTuple(
                    {
                        "configurable": {
                            "thread_id": record["thread_id"],
                            "thread_ts": record["thread_ts"],
                        }
                    },
                    self.serde.loads(record["checkpoint"]),
                    self.serde.loads(record["metadata"]) if record["metadata"] else {},
                    (
                        {
                            "configurable": {
                                "thread_id": record["thread_id"],
                                "thread_ts": record["parent_ts"],
                            }
                        }
                        if record["parent_ts"]
                        else None
                    ),
                )

    async def asearch(
        self,
        metadata_filter: CheckpointMetadata,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """Search for checkpoints by metadata asynchronously.

        This method retrieves a list of checkpoint tuples from the PostgreSQL
        database based on the provided metadata filter. The metadata filter does
        not need to contain all keys defined in the CheckpointMetadata class.
        The checkpoints are ordered by timestamp in descending order.

        Args:
            metadata_filter (CheckpointMetadata): The metadata filter to use for searching the checkpoints.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified timestamp are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        await self.setup()

        # construct query
        SELECT = "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints "
        WHERE, params = search_where(metadata_filter, before)
        ORDER_BY = "ORDER BY thread_ts DESC "
        LIMIT = f"LIMIT {limit}" if limit else ""

        query = f"{SELECT}{WHERE}{ORDER_BY}{LIMIT}"

        # execute query
        async with self.conn.transaction():
            async for record in self.conn.cursor(query, *params):
                yield CheckpointTuple(
                    {
                        "configurable": {
                            "thread_id": record["thread_id"],
                            "thread_ts": record["thread_ts"],
                        }
                    },
                    self.serde.loads(record["checkpoint"]),
                    self.serde.loads(record["metadata"]) if record["metadata"] else {},
                    (
                        {
                            "configurable": {
                                "thread_id": record["thread_id"],
                                "thread_ts": record["parent_ts"],
                            }
                        }
                        if record["parent_ts"]
                        else None
                    ),
                )

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        """Save a checkpoint to the database asynchronously.

        This method saves a checkpoint to the PostgreSQL database. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.

        Returns:
            RunnableConfig: The updated config containing the saved checkpoint's timestamp.
        """
        await self.setup()
        await self.conn.execute(
            "INSERT INTO checkpoints (thread_id, thread_ts, parent_ts, checkpoint, metadata) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (thread_id, thread_ts) DO UPDATE SET checkpoint = EXCLUDED.checkpoint, metadata = EXCLUDED.metadata",
            str(config["configurable"]["thread_id"]),
            checkpoint["id"],
            config["configurable"].get("thread_ts"),
            self.serde.dumps(checkpoint),
            self.serde.dumps(metadata),
        )
        return {
            "configurable": {
                "thread_id": config["configurable"]["thread_id"],
                "thread_ts": checkpoint["id"],
            }
        }
