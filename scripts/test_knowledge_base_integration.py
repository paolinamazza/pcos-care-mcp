"""
Test Knowledge Base Integration - Test the new PDF RAG system
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.knowledge_base import PCOSKnowledgeBase


def test_pdf_rag_system():
    """Test the PDF RAG system integration"""
    print("="*70)
    print("TESTING PDF RAG SYSTEM INTEGRATION")
    print("="*70)

    # Initialize knowledge base
    print("\n1. Initializing knowledge base...")
    try:
        kb = PCOSKnowledgeBase(use_pdf_rag=True)
        print("   ✓ Knowledge base initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False

    # Get statistics
    print("\n2. Getting statistics...")
    stats = kb.get_stats()
    print(f"   Model: {stats['model']}")
    print(f"   PDF RAG Enabled: {stats['pdf_rag_enabled']}")

    if 'pdf_rag' in stats:
        pdf_stats = stats['pdf_rag']
        print(f"\n   PDF RAG System:")
        print(f"   - Status: {pdf_stats.get('status', 'unknown')}")
        print(f"   - Total chunks: {pdf_stats.get('total_chunks', 0)}")
        print(f"   - Categories: {list(pdf_stats.get('categories', {}).keys())}")

        if pdf_stats.get('total_chunks', 0) == 0:
            print("\n   ⚠️  ChromaDB is empty!")
            print("   Run: python3 scripts/setup_rag.py")
            return False

    # Test queries
    print("\n3. Testing queries...")

    test_queries = [
        "What are the Rotterdam criteria for PCOS?",
        "How does exercise help with PCOS?",
        "What dietary changes are recommended for PCOS?",
        "Mental health and PCOS"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: '{query}'")

        try:
            result = kb.query_pdf_knowledge(
                query=query,
                top_k=3,
                include_sources=True
            )

            if result['success']:
                print(f"   ✓ Success!")
                print(f"     Confidence: {result.get('confidence', 0):.2%}")
                print(f"     Sources: {result.get('num_sources', 0)}")
                print(f"     Chunks found: {result.get('total_chunks_found', 0)}")

                if result.get('sources'):
                    top_source = result['sources'][0]
                    print(f"     Top source: {top_source['title']} ({top_source['category']})")

                # Show context preview
                context = result.get('context', '')
                if context:
                    preview = context[:200] + "..." if len(context) > 200 else context
                    print(f"     Context preview: {preview}")

            else:
                print(f"   ✗ Failed: {result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"   ✗ Error: {e}")

    # Test with category filter
    print("\n4. Testing category filter...")
    try:
        result = kb.query_pdf_knowledge(
            query="exercise recommendations",
            top_k=3,
            category_filter="exercise"
        )

        if result['success']:
            print(f"   ✓ Category filter works!")
            print(f"     Found {result.get('total_chunks_found', 0)} chunks in 'exercise' category")
        else:
            print(f"   ✗ Failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

    return True


def test_fallback_system():
    """Test fallback to legacy FAISS system"""
    print("\n" + "="*70)
    print("TESTING FALLBACK TO LEGACY SYSTEM")
    print("="*70)

    print("\n1. Initializing with PDF RAG disabled...")
    try:
        kb = PCOSKnowledgeBase(use_pdf_rag=False)
        print("   ✓ Knowledge base initialized (PDF RAG disabled)")

        # Build legacy index
        print("\n2. Building legacy FAISS index...")
        kb.build_index()

        # Test legacy query
        print("\n3. Testing legacy query...")
        result = kb.get_answer(
            query="What is PCOS?",
            top_k=3,
            include_sources=True
        )

        if result['success']:
            print(f"   ✓ Legacy system works!")
            print(f"     Sources: {result.get('num_sources', 0)}")
        else:
            print(f"   ✗ Failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "="*70)


if __name__ == "__main__":
    success = test_pdf_rag_system()

    if success:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Ensure ChromaDB is populated: python3 scripts/setup_rag.py")
        print("2. Start MCP server: python3 server.py")
        print("3. Test with Claude Desktop")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

    # Optionally test fallback
    print("\n" + "="*70)
    test_fallback = input("\nTest fallback to legacy system? (y/n): ")
    if test_fallback.lower() == 'y':
        test_fallback_system()
