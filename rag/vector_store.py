"""
Vector Store - ChromaDB integration for RAG system

Features:
- Store and retrieve text chunks with embeddings
- Metadata filtering by category
- Efficient similarity search
- Persistent storage
"""

import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import numpy as np

try:
    import chromadb
    # Try importing Settings for older versions, but it's not needed for v1.x
    try:
        from chromadb.config import Settings
    except ImportError:
        Settings = None
except ImportError:
    chromadb = None
    Settings = None

from rag.chunker import TextChunk


logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for RAG system"""

    def __init__(
        self,
        persist_directory: str = "docs/processed/embeddings/chroma_db",
        collection_name: str = "pcos_knowledge_v2"
    ):
        """
        Initialize vector store

        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
        """
        if chromadb is None:
            raise ImportError(
                "chromadb not installed. "
                "Install with: pip install chromadb"
            )

        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name

        # Create directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initializing ChromaDB at: {persist_directory}")

        # Initialize ChromaDB client with persistent storage
        # Use different API based on ChromaDB version
        try:
            # Try v1.x API (PersistentClient)
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            logger.info("Using ChromaDB v1.x+ API (PersistentClient)")
        except AttributeError:
            # Fallback to v0.x API (Client with Settings)
            if Settings is None:
                raise ImportError("ChromaDB Settings not available")
            self.client = chromadb.Client(Settings(
                persist_directory=str(self.persist_directory),
                anonymized_telemetry=False
            ))
            logger.info("Using ChromaDB v0.x API (Client with Settings)")

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "PCOS knowledge base from research PDFs"}
            )
            logger.info(f"Created new collection: {collection_name}")

    def add_chunks(
        self,
        chunks: List[TextChunk],
        embeddings: Dict[str, np.ndarray],
        batch_size: int = 100
    ) -> None:
        """
        Add chunks with embeddings to the vector store

        Args:
            chunks: List of TextChunk objects
            embeddings: Dictionary mapping chunk_id to embedding
            batch_size: Batch size for adding to ChromaDB
        """
        logger.info(f"Adding {len(chunks)} chunks to vector store")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for chunk in chunks:
            if chunk.chunk_id not in embeddings:
                logger.warning(f"No embedding found for chunk {chunk.chunk_id}, skipping")
                continue

            ids.append(chunk.chunk_id)
            documents.append(chunk.text)

            # Metadata
            metadata = {
                "source": chunk.source,
                "category": chunk.category,
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "total_chunks": chunk.total_chunks,
                "file_path": chunk.file_path
            }
            metadatas.append(metadata)

            # Embedding
            embeddings_list.append(embeddings[chunk.chunk_id].tolist())

        # Add to ChromaDB in batches
        total_added = 0

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_emb = embeddings_list[i:i + batch_size]

            self.collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=batch_emb
            )

            total_added += len(batch_ids)
            logger.info(f"Added {total_added}/{len(ids)} chunks")

        logger.info(f"Successfully added {total_added} chunks to vector store")

    def query(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store for similar chunks

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            category_filter: Optional category to filter by

        Returns:
            Dictionary with results
        """
        # Prepare where filter
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter
        )

        # Format results
        formatted_results = {
            "chunks": [],
            "total": len(results["ids"][0]) if results["ids"] else 0
        }

        if not results["ids"] or not results["ids"][0]:
            return formatted_results

        # Extract results
        for i in range(len(results["ids"][0])):
            chunk_data = {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            }
            formatted_results["chunks"].append(chunk_data)

        return formatted_results

    def query_by_text(
        self,
        query_text: str,
        top_k: int = 5,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query using text (ChromaDB will generate embedding)

        Args:
            query_text: Query text
            top_k: Number of results to return
            category_filter: Optional category to filter by

        Returns:
            Dictionary with results
        """
        # Prepare where filter
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter
        )

        # Format results
        formatted_results = {
            "chunks": [],
            "total": len(results["ids"][0]) if results["ids"] else 0
        }

        if not results["ids"] or not results["ids"][0]:
            return formatted_results

        # Extract results
        for i in range(len(results["ids"][0])):
            chunk_data = {
                "chunk_id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            }
            formatted_results["chunks"].append(chunk_data)

        return formatted_results

    def get_by_id(self, chunk_id: str) -> Optional[Dict]:
        """
        Get chunk by ID

        Args:
            chunk_id: Chunk ID

        Returns:
            Chunk data or None if not found
        """
        try:
            results = self.collection.get(
                ids=[chunk_id],
                include=["documents", "metadatas", "embeddings"]
            )

            if not results["ids"]:
                return None

            return {
                "chunk_id": results["ids"][0],
                "text": results["documents"][0],
                "metadata": results["metadatas"][0],
                "embedding": results["embeddings"][0] if "embeddings" in results else None
            }
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {e}")
            return None

    def get_all_categories(self) -> List[str]:
        """
        Get all unique categories in the store

        Returns:
            List of category names
        """
        # Get all documents
        all_docs = self.collection.get(include=["metadatas"])

        if not all_docs["metadatas"]:
            return []

        # Extract unique categories
        categories = set(meta["category"] for meta in all_docs["metadatas"])

        return sorted(list(categories))

    def get_statistics(self) -> Dict:
        """
        Get statistics about the vector store

        Returns:
            Dictionary with statistics
        """
        count = self.collection.count()

        if count == 0:
            return {
                "total_chunks": 0,
                "categories": {}
            }

        # Get all documents to compute stats
        all_docs = self.collection.get(include=["metadatas"])

        # Category statistics
        category_stats = {}
        for meta in all_docs["metadatas"]:
            category = meta["category"]
            if category not in category_stats:
                category_stats[category] = {"count": 0, "sources": set()}

            category_stats[category]["count"] += 1
            category_stats[category]["sources"].add(meta["source"])

        # Convert sets to counts
        for category in category_stats:
            category_stats[category]["num_sources"] = len(category_stats[category]["sources"])
            del category_stats[category]["sources"]

        return {
            "total_chunks": count,
            "categories": category_stats,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory)
        }

    def clear(self) -> None:
        """Clear all data from the collection"""
        logger.warning(f"Clearing collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "PCOS knowledge base from research PDFs"}
        )
        logger.info("Collection cleared")

    def save_metadata(self, output_path: str, chunks: List[TextChunk]) -> None:
        """
        Save chunk metadata to JSON file

        Args:
            output_path: Path to save metadata
            chunks: List of chunks
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        metadata = {
            "total_chunks": len(chunks),
            "chunks": [chunk.to_dict() for chunk in chunks]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved metadata to {output_path}")


def main():
    """Test the vector store"""
    from rag.pdf_processor import PDFProcessor
    from rag.chunker import Chunker
    from rag.embeddings import EmbeddingsGenerator

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("="*60)
    print("VECTOR STORE TEST")
    print("="*60)

    # Process PDFs
    print("\n1. Processing PDFs...")
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()[:2]  # Test with first 2 docs

    # Chunk documents
    print("\n2. Chunking documents...")
    chunker = Chunker()
    chunks = chunker.chunk_documents(documents)

    # Generate embeddings
    print("\n3. Generating embeddings...")
    generator = EmbeddingsGenerator()
    embeddings = generator.generate_chunk_embeddings(chunks)

    # Create vector store
    print("\n4. Creating vector store...")
    store = VectorStore(
        persist_directory="docs/processed/embeddings/test_chroma_db",
        collection_name="test_pcos"
    )

    # Clear existing data
    store.clear()

    # Add chunks
    print("\n5. Adding chunks to store...")
    store.add_chunks(chunks, embeddings)

    # Get statistics
    stats = store.get_statistics()
    print("\n" + "="*60)
    print("STORE STATISTICS")
    print("="*60)
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Categories: {list(stats['categories'].keys())}")
    for cat, cat_stats in stats['categories'].items():
        print(f"  {cat}: {cat_stats['count']} chunks from {cat_stats['num_sources']} sources")

    # Test query
    print("\n6. Testing query...")
    query = "What are the Rotterdam criteria for PCOS?"
    results = store.query_by_text(query, top_k=3)

    print(f"\nQuery: '{query}'")
    print(f"Found {results['total']} results:\n")

    for i, chunk in enumerate(results['chunks']):
        print(f"{i+1}. Source: {chunk['metadata']['source']} (page ~{chunk['metadata']['page']})")
        print(f"   Category: {chunk['metadata']['category']}")
        print(f"   Distance: {chunk['distance']:.4f}")
        print(f"   Text: {chunk['text'][:150]}...")
        print()

    print("="*60)


if __name__ == "__main__":
    main()
