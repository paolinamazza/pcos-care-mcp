"""
Unit Tests per RAG Knowledge Base System
Focus su documenti e struttura, con smoke tests per RAG functionality
"""

import pytest
from pathlib import Path


class TestPCOSKnowledgeBase:
    """Test suite per PCOSKnowledgeBase - smoke tests strutturali"""

    def test_dependencies_check(self):
        """Test: Verifica che DEPENDENCIES_AVAILABLE sia definito"""
        from rag import knowledge_base

        assert hasattr(knowledge_base, 'DEPENDENCIES_AVAILABLE')
        assert isinstance(knowledge_base.DEPENDENCIES_AVAILABLE, bool)

    def test_init_without_dependencies_fails(self):
        """Test: Inizializzazione senza dipendenze deve fallire"""
        from rag.knowledge_base import PCOSKnowledgeBase, DEPENDENCIES_AVAILABLE

        if not DEPENDENCIES_AVAILABLE:
            with pytest.raises(ImportError) as exc_info:
                PCOSKnowledgeBase()

            assert "RAG dependencies not installed" in str(exc_info.value)
        else:
            # Se le dipendenze sono installate, test passa
            pytest.skip("Dependencies available, skipping negative test")

    def test_class_structure(self):
        """Test: Verifica struttura della classe (senza istanziare)"""
        from rag.knowledge_base import PCOSKnowledgeBase

        # Verifica che la classe abbia i metodi principali
        assert hasattr(PCOSKnowledgeBase, '__init__')
        assert hasattr(PCOSKnowledgeBase, 'build_index')
        assert hasattr(PCOSKnowledgeBase, 'search')
        assert hasattr(PCOSKnowledgeBase, 'get_answer')
        assert hasattr(PCOSKnowledgeBase, 'get_stats')

    def test_cache_dir_structure(self):
        """Test: Verifica che cache dir sia configurata correttamente"""
        from rag.knowledge_base import PCOSKnowledgeBase, DEPENDENCIES_AVAILABLE

        if DEPENDENCIES_AVAILABLE:
            kb = PCOSKnowledgeBase()
            assert kb.cache_dir is not None
            assert isinstance(kb.cache_dir, Path)
        else:
            pytest.skip("Dependencies not available")

    def test_model_name_configuration(self):
        """Test: Verifica che model_name sia configurabile"""
        from rag.knowledge_base import PCOSKnowledgeBase, DEPENDENCIES_AVAILABLE

        if DEPENDENCIES_AVAILABLE:
            custom_model = "custom-model"
            kb = PCOSKnowledgeBase(model_name=custom_model)
            assert kb.model_name == custom_model
        else:
            pytest.skip("Dependencies not available")

    def test_initial_state(self):
        """Test: Verifica stato iniziale dopo init"""
        from rag.knowledge_base import PCOSKnowledgeBase, DEPENDENCIES_AVAILABLE

        if DEPENDENCIES_AVAILABLE:
            kb = PCOSKnowledgeBase()
            assert kb.model is None  # Lazy loading
            assert kb.index is None
            assert kb.documents == []
            assert kb.embeddings is None
        else:
            pytest.skip("Dependencies not available")

    def test_logging_configuration(self):
        """Test: Verifica che logging sia configurato"""
        from rag import knowledge_base

        assert hasattr(knowledge_base, 'logger')
        assert knowledge_base.logger is not None


class TestPCOSDocuments:
    """Test per PCOS documents module"""

    def test_get_all_documents_returns_list(self):
        """Test: get_all_documents ritorna una lista"""
        from rag.pcos_documents import get_all_documents

        docs = get_all_documents()

        assert isinstance(docs, list)
        assert len(docs) > 0

    def test_document_structure(self):
        """Test: Ogni documento ha la struttura corretta"""
        from rag.pcos_documents import get_all_documents

        docs = get_all_documents()

        for doc in docs:
            assert "id" in doc
            assert "title" in doc
            assert "content" in doc
            assert "category" in doc
            assert isinstance(doc["id"], str)
            assert isinstance(doc["title"], str)
            assert isinstance(doc["content"], str)
            assert len(doc["content"]) > 0

    def test_documents_cover_key_topics(self):
        """Test: Documenti coprono topic chiave di PCOS"""
        from rag.pcos_documents import get_all_documents

        docs = get_all_documents()
        categories = {doc["category"] for doc in docs}

        # Verifica che ci siano almeno questi topic
        expected_categories = {"basics", "symptoms", "nutrition", "lifestyle"}
        assert expected_categories.issubset(categories)

    def test_documents_have_minimum_content_quality(self):
        """Test: Documenti hanno qualità minima di contenuto"""
        from rag.pcos_documents import get_all_documents

        docs = get_all_documents()

        for doc in docs:
            # Contenuto deve essere sufficientemente lungo
            assert len(doc["content"]) >= 100, f"Document {doc['id']} too short"
            # Titolo deve essere significativo
            assert len(doc["title"]) >= 5, f"Document {doc['id']} title too short"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
