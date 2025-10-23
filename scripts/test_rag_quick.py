"""
Quick RAG test - Process 3 PDFs to verify the system works
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.pdf_processor import PDFProcessor
from rag.chunker import Chunker
from rag.embeddings import EmbeddingsGenerator
from rag.vector_store import VectorStore


def main():
    """Quick test with 3 PDFs"""
    logging.basicConfig(level=logging.WARNING)

    print("="*60)
    print("QUICK RAG TEST (3 PDFs)")
    print("="*60)

    # Process first 3 PDFs
    print("\n1. Processing PDFs...")
    processor = PDFProcessor()
    all_pdfs = list(processor.pdf_dir.rglob('*.pdf'))[:3]
    documents = []

    for pdf in all_pdfs:
        doc = processor.process_pdf(pdf)
        if doc:
            documents.append(doc)
            print(f"   ✓ {doc.source} ({doc.category}): {len(doc.text)} chars")

    print(f"\n   Total: {len(documents)} documents processed")

    # Chunk
    print("\n2. Chunking...")
    chunker = Chunker(chunk_size=700, overlap=50)
    chunks = chunker.chunk_documents(documents)
    print(f"   ✓ Created {len(chunks)} chunks")

    # Generate embeddings
    print("\n3. Generating embeddings...")
    generator = EmbeddingsGenerator(batch_size=16)
    embeddings = generator.generate_chunk_embeddings(chunks, show_progress=False)
    print(f"   ✓ Generated {len(embeddings)} embeddings (dim={generator.get_embedding_dimension()})")

    # Store in ChromaDB
    print("\n4. Storing in ChromaDB...")
    store = VectorStore(
        persist_directory="docs/processed/embeddings/test_chroma_db",
        collection_name="test_pcos_quick"
    )
    store.clear()
    store.add_chunks(chunks, embeddings)
    print(f"   ✓ Stored {store.collection.count()} chunks")

    # Test query
    print("\n5. Testing query...")
    query = "What are the Rotterdam criteria for PCOS?"
    results = store.query_by_text(query, top_k=3)

    print(f"\n   Query: '{query}'")
    print(f"   Found {results['total']} results:\n")

    for i, chunk in enumerate(results['chunks'][:3]):
        print(f"   {i+1}. {chunk['metadata']['source']} ({chunk['metadata']['category']})")
        print(f"      Distance: {chunk['distance']:.4f}")
        print(f"      Preview: {chunk['text'][:80]}...\n")

    print("="*60)
    print("✅ QUICK TEST COMPLETE - System is working!")
    print("="*60)
    print("\nNext: Run full setup with all PDFs:")
    print("  python3 scripts/setup_rag.py")
    print()


if __name__ == "__main__":
    main()
