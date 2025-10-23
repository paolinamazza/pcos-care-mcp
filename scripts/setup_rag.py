"""
Setup RAG system - Process PDFs and create embeddings

Complete pipeline:
1. Extract text from PDFs
2. Create intelligent chunks
3. Generate embeddings
4. Store in ChromaDB
5. Save metadata
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pdf_processor import PDFProcessor
from rag.chunker import Chunker
from rag.embeddings import EmbeddingsGenerator
from rag.vector_store import VectorStore


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docs/processed/rag_setup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_stats(title: str, stats: dict):
    """Print formatted statistics"""
    print(f"\n{title}:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    - {sub_key}: {sub_value}")
        elif isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        elif isinstance(value, int) and value > 1000:
            print(f"  {key}: {value:,}")
        else:
            print(f"  {key}: {value}")


def main():
    """Run complete RAG setup pipeline"""
    start_time = time.time()

    print_header("🚀 PCOS RAG SETUP - STARTING")

    try:
        # ====================================================================
        # STEP 1: Process PDFs
        # ====================================================================
        print_header("📄 STEP 1/5: Processing PDF Documents")

        processor = PDFProcessor(pdf_dir="docs/raw_pdfs")
        documents = processor.process_all_pdfs()

        if not documents:
            logger.error("No documents were successfully processed!")
            return 1

        pdf_stats = processor.get_statistics(documents)
        print_stats("PDF Processing Results", {
            "Documents Processed": pdf_stats["total_documents"],
            "Total Pages": pdf_stats["total_pages"],
            "Total Characters": pdf_stats["total_chars"],
            "Avg Pages/Doc": pdf_stats["avg_pages_per_doc"],
            "Categories": len(pdf_stats["categories"])
        })

        # ====================================================================
        # STEP 2: Chunk Documents
        # ====================================================================
        print_header("✂️  STEP 2/5: Creating Text Chunks")

        chunker = Chunker(
            chunk_size=700,
            overlap=50,
            min_chunk_size=100
        )

        chunks = chunker.chunk_documents(documents)

        if not chunks:
            logger.error("No chunks were created!")
            return 1

        chunk_stats = chunker.get_statistics(chunks)
        print_stats("Chunking Results", {
            "Total Chunks": chunk_stats["total_chunks"],
            "Total Tokens": chunk_stats["total_tokens"],
            "Avg Tokens/Chunk": chunk_stats["avg_tokens_per_chunk"],
            "Min Tokens": chunk_stats["min_tokens"],
            "Max Tokens": chunk_stats["max_tokens"],
            "Categories": len(chunk_stats["categories"])
        })

        # ====================================================================
        # STEP 3: Generate Embeddings
        # ====================================================================
        print_header("🧠 STEP 3/5: Generating Embeddings")

        generator = EmbeddingsGenerator(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            batch_size=32,
            expand_acronyms=True
        )

        embeddings = generator.generate_chunk_embeddings(
            chunks,
            show_progress=True
        )

        print_stats("Embedding Results", {
            "Embeddings Generated": len(embeddings),
            "Embedding Dimension": generator.get_embedding_dimension(),
            "Model": generator.model_name
        })

        # ====================================================================
        # STEP 4: Store in ChromaDB
        # ====================================================================
        print_header("💾 STEP 4/5: Storing in ChromaDB")

        vector_store = VectorStore(
            persist_directory="docs/processed/embeddings/chroma_db",
            collection_name="pcos_knowledge_v2"
        )

        # Clear existing data (optional - comment out to append)
        print("Clearing existing collection...")
        vector_store.clear()

        # Add chunks to store
        vector_store.add_chunks(chunks, embeddings, batch_size=100)

        store_stats = vector_store.get_statistics()
        print_stats("Vector Store Results", {
            "Total Chunks Stored": store_stats["total_chunks"],
            "Categories": len(store_stats["categories"]),
            "Persist Directory": store_stats["persist_directory"]
        })

        # ====================================================================
        # STEP 5: Save Metadata
        # ====================================================================
        print_header("📝 STEP 5/5: Saving Metadata")

        metadata_path = "docs/processed/chunks/metadata.json"
        vector_store.save_metadata(metadata_path, chunks)

        print(f"✓ Metadata saved to: {metadata_path}")

        # ====================================================================
        # FINAL SUMMARY
        # ====================================================================
        elapsed_time = time.time() - start_time

        print_header("✅ RAG SETUP COMPLETE")

        print("\n📊 FINAL SUMMARY:")
        print(f"  Documents Processed: {pdf_stats['total_documents']}")
        print(f"  Pages Processed: {pdf_stats['total_pages']}")
        print(f"  Chunks Created: {chunk_stats['total_chunks']}")
        print(f"  Embeddings Generated: {len(embeddings)}")
        print(f"  Time Elapsed: {elapsed_time:.1f} seconds")

        print("\n📂 OUTPUT FILES:")
        print(f"  ChromaDB: docs/processed/embeddings/chroma_db/")
        print(f"  Metadata: {metadata_path}")
        print(f"  Logs: docs/processed/rag_setup.log")

        print("\n🎯 NEXT STEPS:")
        print("  1. Test the system with: python3 rag/vector_store.py")
        print("  2. Integrate with MCP server (FASE 6)")
        print("  3. Query example:")
        print("     from rag.vector_store import VectorStore")
        print("     store = VectorStore()")
        print("     results = store.query_by_text('Rotterdam criteria', top_k=5)")

        print("\n" + "="*70 + "\n")

        return 0

    except Exception as e:
        logger.error(f"RAG setup failed: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
