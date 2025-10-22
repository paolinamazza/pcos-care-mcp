"""
RAG Knowledge Base System - FASE 3
Sistema per Q&A evidence-based su PCOS usando FAISS e sentence-transformers
"""

import os
import pickle
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning(
        "RAG dependencies not installed. "
        "Run: pip install sentence-transformers faiss-cpu numpy"
    )

from rag.pcos_documents import get_all_documents

logger = logging.getLogger("pcos-care-mcp.rag")


class PCOSKnowledgeBase:
    """
    Sistema RAG per Q&A su PCOS.

    Usa:
    - sentence-transformers per creare embeddings semantici
    - FAISS per ricerca vettoriale efficiente
    - Knowledge base con documenti evidence-based
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Inizializza knowledge base.

        Args:
            model_name: Nome del modello sentence-transformers
                       (default: all-MiniLM-L6-v2, piccolo e veloce)
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "RAG dependencies not installed. "
                "Run: pip install sentence-transformers faiss-cpu numpy"
            )

        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = []
        self.embeddings = None

        # Paths per cache
        self.cache_dir = Path(__file__).parent.parent / "data" / "rag_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.cache_dir / "faiss.index"
        self.embeddings_path = self.cache_dir / "embeddings.pkl"
        self.docs_path = self.cache_dir / "documents.pkl"

        logger.info(f"Initializing PCOS Knowledge Base with model: {model_name}")

    def _load_model(self):
        """Carica il modello sentence-transformers (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading sentence-transformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")

    def build_index(self, force_rebuild: bool = False):
        """
        Costruisce l'indice FAISS dai documenti.

        Args:
            force_rebuild: Se True, ricostruisce anche se esiste cache
        """
        # Check cache
        if not force_rebuild and self._load_from_cache():
            logger.info("Loaded knowledge base from cache")
            return

        logger.info("Building FAISS index from scratch...")

        # Load model
        self._load_model()

        # Load documents
        self.documents = get_all_documents()
        logger.info(f"Loaded {len(self.documents)} documents")

        # Create embeddings
        logger.info("Creating embeddings...")
        texts = [
            f"{doc['title']}\n{doc['content']}"
            for doc in self.documents
        ]

        self.embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        # Build FAISS index
        logger.info("Building FAISS index...")
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        self.index.add(self.embeddings)

        logger.info(f"FAISS index built with {self.index.ntotal} vectors")

        # Save to cache
        self._save_to_cache()

    def _save_to_cache(self):
        """Salva index e embeddings in cache"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))

            # Save embeddings
            with open(self.embeddings_path, 'wb') as f:
                pickle.dump(self.embeddings, f)

            # Save documents
            with open(self.docs_path, 'wb') as f:
                pickle.dump(self.documents, f)

            logger.info("Knowledge base saved to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _load_from_cache(self) -> bool:
        """
        Carica da cache se disponibile.

        Returns:
            True se caricato con successo, False altrimenti
        """
        try:
            if not (self.index_path.exists() and
                    self.embeddings_path.exists() and
                    self.docs_path.exists()):
                return False

            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))

            # Load embeddings
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)

            # Load documents
            with open(self.docs_path, 'rb') as f:
                self.documents = pickle.load(f)

            # Load model for querying
            self._load_model()

            return True

        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Cerca documenti rilevanti per una query.

        Args:
            query: Domanda dell'utente
            top_k: Numero di documenti da restituire
            score_threshold: Soglia di similarità (opzionale)

        Returns:
            Lista di documenti rilevanti con scores
        """
        if self.index is None:
            logger.warning("Index not built, building now...")
            self.build_index()

        # Create query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        # Search in FAISS
        distances, indices = self.index.search(query_embedding, top_k)

        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            # Convert L2 distance to similarity score (0-1, higher is better)
            # Using exponential decay: score = exp(-distance)
            similarity_score = np.exp(-distance / 10)  # Scaled for readability

            # Apply threshold if specified
            if score_threshold and similarity_score < score_threshold:
                continue

            doc = self.documents[idx]
            results.append({
                "document": doc,
                "score": float(similarity_score),
                "rank": i + 1,
                "distance": float(distance)
            })

        return results

    def get_answer(
        self,
        query: str,
        top_k: int = 3,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Genera una risposta completa per una query.

        Args:
            query: Domanda dell'utente
            top_k: Numero di documenti da considerare
            include_sources: Se includere le fonti

        Returns:
            Dizionario con risposta e metadati
        """
        # Search relevant documents
        results = self.search(query, top_k=top_k)

        if not results:
            return {
                "success": False,
                "message": "Non ho trovato informazioni rilevanti per la tua domanda.",
                "query": query
            }

        # Build answer from top results
        answer_parts = []
        sources = []

        for result in results:
            doc = result["document"]
            score = result["score"]

            # Only include high-confidence results in main answer
            if score > 0.5:  # Threshold for inclusion
                answer_parts.append(doc["content"].strip())

            # Always include in sources
            if include_sources:
                sources.append({
                    "title": doc["title"],
                    "category": doc["category"],
                    "source": doc.get("source", "PCOS Care Knowledge Base"),
                    "relevance_score": round(score, 2)
                })

        # Combine answer
        if not answer_parts:
            # Fallback to best match even if low score
            answer_parts = [results[0]["document"]["content"].strip()]

        answer_text = "\n\n".join(answer_parts)

        return {
            "success": True,
            "query": query,
            "answer": answer_text,
            "sources": sources,
            "num_sources": len(sources),
            "confidence": results[0]["score"] if results else 0
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Restituisce statistiche sulla knowledge base.

        Returns:
            Dizionario con statistiche
        """
        if self.index is None:
            return {
                "status": "not_initialized",
                "message": "Knowledge base not built yet"
            }

        categories = {}
        for doc in self.documents:
            cat = doc["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "status": "ready",
            "total_documents": len(self.documents),
            "categories": categories,
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else None,
            "model": self.model_name,
            "cache_available": self.index_path.exists()
        }
