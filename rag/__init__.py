"""
RAG Package - FASE 3
Sistema RAG per Q&A evidence-based su PCOS
"""

from rag.knowledge_base import PCOSKnowledgeBase
from rag.pcos_documents import get_all_documents, get_documents_by_category

__all__ = [
    'PCOSKnowledgeBase',
    'get_all_documents',
    'get_documents_by_category'
]
