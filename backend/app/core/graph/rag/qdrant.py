import pymupdf4llm  # type: ignore[import-untyped]
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.http import models as rest

from app.core.config import settings


class QdrantStore:
    """
    A class to handle uploading and searching documents in a Qdrant vector store.
    """

    embeddings = FastEmbedEmbeddings()
    collection_name = settings.QDRANT_COLLECTION
    url = settings.QDRANT_URL

    def create(
        self,
        file_path: str,
        upload_id: int,
        user_id: int,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> None:
        """
        Uploads a PDF document to the Qdrant vector store after converting it to markdown and splitting into chunks.

        Args:
            upload_name (str): The name of the upload (PDF file path).
            user_id (int): The ID of the user uploading the document.
            chunk_size (int, optional): The size of each text chunk. Defaults to 500.
            chunk_overlap (int, optional): The overlap size between chunks. Defaults to 50.
        """
        md_text = pymupdf4llm.to_markdown(file_path)
        text_spliter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        docs = text_spliter.create_documents(
            [md_text],
            [{"user_id": user_id, "upload_id": upload_id}],
        )
        Qdrant.from_documents(
            documents=docs,
            embedding=self.embeddings,
            url=self.url,
            prefer_grpc=True,
            collection_name=self.collection_name,
            api_key=settings.QDRANT__SERVICE__API_KEY,
        )

    def _get_collection(self) -> Qdrant:
        """Get instance of an existing Qdrant collection."""
        return Qdrant.from_existing_collection(
            embedding=self.embeddings,
            url=self.url,
            prefer_grpc=True,
            collection_name=self.collection_name,
            api_key=settings.QDRANT__SERVICE__API_KEY,
        )

    def delete(self, upload_id: int, user_id: int) -> bool | None:
        """Delete points from collection where upload_id and user_id in metadata matches."""
        qdrant = self._get_collection()
        return qdrant.delete(
            ids=rest.Filter(  # type: ignore[arg-type]
                must=[
                    rest.FieldCondition(
                        key="metadata.user_id",
                        match=rest.MatchValue(value=user_id),
                    ),
                    rest.FieldCondition(
                        key="metadata.upload_id",
                        match=rest.MatchValue(value=upload_id),
                    ),
                ]
            )
        )

    def retriever(self, user_id: int, upload_id: int) -> VectorStoreRetriever:
        """
        Creates a VectorStoreRetriever that retrieves results containing the specified user_id and upload_id in the metadata.

        Args:
            user_id (int): Filters the retriever results to only include those belonging to this user.
            upload_id (int): Filters the retriever results to only include those from this upload ID.

        Returns:
            VectorStoreRetriever: A VectorStoreRetriever instance.
        """
        qdrant = self._get_collection()
        retriever = qdrant.as_retriever(
            search_kwargs={"filter": {"user_id": user_id, "upload_id": upload_id}}
        )
        return retriever

    def search(self, user_id: int, upload_ids: list[int], query: str) -> list[Document]:
        """
        Performs a similarity search in the Qdrant vector store for a given query, filtered by user ID and upload names.

        Args:
            user_id (str): The ID of the user performing the search.
            upload_names (list[str]): A list of upload names to filter the search.
            query (str): The search query.

        Returns:
            List[Document]: A list of documents matching the search criteria.
        """
        qdrant = self._get_collection()
        found_docs = qdrant.similarity_search(
            query,
            filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="metadata.user_id",
                        match=rest.MatchValue(value=user_id),
                    ),
                    rest.FieldCondition(
                        key="metadata.upload_id",
                        match=rest.MatchAny(any=upload_ids),
                    ),
                ]
            ),
        )
        return found_docs
