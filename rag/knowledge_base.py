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

# Import new PDF-based RAG system
try:
    from rag.vector_store import VectorStore
    from rag.embeddings import EmbeddingsGenerator
    PDF_RAG_AVAILABLE = True
except ImportError:
    PDF_RAG_AVAILABLE = False
    logging.warning("PDF RAG system not available (missing dependencies)")

logger = logging.getLogger("pcos-care-mcp.rag")


class PCOSKnowledgeBase:
    """
    Sistema RAG per Q&A su PCOS.

    Usa:
    - sentence-transformers per creare embeddings semantici
    - FAISS per ricerca vettoriale efficiente
    - Knowledge base con documenti evidence-based
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_pdf_rag: bool = True):
        """
        Inizializza knowledge base.

        Args:
            model_name: Nome del modello sentence-transformers
                       (default: all-MiniLM-L6-v2, piccolo e veloce)
            use_pdf_rag: Se True, usa il nuovo sistema basato su PDF reali (default: True)
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = []
        self.embeddings = None
        self.use_pdf_rag = use_pdf_rag and PDF_RAG_AVAILABLE

        # Check if we have at least one working system
        if not DEPENDENCIES_AVAILABLE and not PDF_RAG_AVAILABLE:
            raise ImportError(
                "No RAG system available. Install dependencies:\n"
                "  For PDF RAG: pip install sentence-transformers chromadb pypdf\n"
                "  For legacy FAISS: pip install sentence-transformers faiss-cpu numpy"
            )

        # Warn if legacy system requested but not available
        if not use_pdf_rag and not DEPENDENCIES_AVAILABLE:
            logger.warning(
                "Legacy FAISS system requested but dependencies not available. "
                "Install: pip install sentence-transformers faiss-cpu numpy"
            )

        # Paths per cache (legacy FAISS system)
        self.cache_dir = Path(__file__).parent.parent / "data" / "rag_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.cache_dir / "faiss.index"
        self.embeddings_path = self.cache_dir / "embeddings.pkl"
        self.docs_path = self.cache_dir / "documents.pkl"

        # Initialize PDF-based RAG system if available
        self.vector_store = None
        self.embeddings_generator = None

        if self.use_pdf_rag:
            try:
                logger.info("Initializing PDF-based RAG system...")
                self.vector_store = VectorStore()
                self.embeddings_generator = EmbeddingsGenerator(model_name=model_name)

                # Check if ChromaDB has data
                stats = self.vector_store.get_statistics()
                if stats['total_chunks'] == 0:
                    logger.warning(
                        "ChromaDB is empty. Run 'python3 scripts/setup_rag.py' to build the knowledge base."
                    )
                else:
                    logger.info(
                        f"PDF RAG system ready: {stats['total_chunks']} chunks from "
                        f"{len(stats['categories'])} categories"
                    )
            except Exception as e:
                logger.error(f"Failed to initialize PDF RAG system: {e}")
                self.use_pdf_rag = False
                logger.info("Falling back to legacy FAISS system")

        logger.info(
            f"Initializing PCOS Knowledge Base with model: {model_name} "
            f"(PDF RAG: {'enabled' if self.use_pdf_rag else 'disabled'})"
        )

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

    def query_pdf_knowledge(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query the PDF-based RAG system (new system with real PDFs).

        Args:
            query: User question
            top_k: Number of chunks to retrieve
            category_filter: Optional category filter (e.g., 'guidelines', 'nutrition')
            include_sources: Whether to include source citations

        Returns:
            Dictionary with answer and metadata
        """
        if not self.use_pdf_rag or self.vector_store is None:
            return {
                "success": False,
                "message": (
                    "PDF RAG system not available. "
                    "Either ChromaDB is empty or dependencies are missing. "
                    "Run 'python3 scripts/setup_rag.py' to build the knowledge base."
                ),
                "query": query,
                "fallback_available": True
            }

        try:
            # Query vector store
            results = self.vector_store.query_by_text(
                query_text=query,
                top_k=top_k,
                category_filter=category_filter
            )

            if not results['chunks']:
                return {
                    "success": False,
                    "message": "No relevant information found in the knowledge base.",
                    "query": query,
                    "fallback_available": True
                }

            # Build context from chunks
            context_parts = []
            sources = []
            seen_sources = set()

            for chunk_data in results['chunks']:
                text = chunk_data['text']
                metadata = chunk_data['metadata']
                distance = chunk_data.get('distance', 1.0)

                # Add to context (only high-quality chunks)
                # ChromaDB uses L2 distance - lower is better
                if distance < 1.5:  # Threshold for quality
                    context_parts.append(text.strip())

                # Add to sources (avoid duplicates)
                source_key = f"{metadata['source']}_{metadata['category']}"
                if include_sources and source_key not in seen_sources:
                    seen_sources.add(source_key)

                    # Convert distance to similarity score (0-1, higher is better)
                    similarity = max(0, 1 - (distance / 2))  # Normalize distance

                    sources.append({
                        "title": metadata['source'],
                        "category": metadata['category'],
                        "page": metadata.get('page', 'N/A'),
                        "relevance_score": round(similarity, 2),
                        "chunk_preview": text[:150] + "..." if len(text) > 150 else text
                    })

            # Combine context
            if not context_parts:
                # Fallback to best match even if low quality
                context_parts = [results['chunks'][0]['text']]

            context = "\n\n".join(context_parts[:3])  # Limit to top 3 for conciseness

            # Calculate overall confidence
            if results['chunks']:
                best_distance = results['chunks'][0].get('distance', 1.0)
                confidence = max(0, 1 - (best_distance / 2))
            else:
                confidence = 0

            return {
                "success": True,
                "query": query,
                "context": context,
                "sources": sources[:5],  # Limit sources
                "num_sources": len(sources),
                "confidence": round(confidence, 2),
                "category_filter": category_filter,
                "total_chunks_found": results['total'],
                "system": "pdf_rag"
            }

        except Exception as e:
            logger.error(f"Error querying PDF knowledge base: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error querying knowledge base: {str(e)}",
                "query": query,
                "fallback_available": True
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Restituisce statistiche sulla knowledge base.

        Returns:
            Dizionario con statistiche
        """
        stats = {
            "model": self.model_name,
            "pdf_rag_enabled": self.use_pdf_rag
        }

        # PDF RAG stats
        if self.use_pdf_rag and self.vector_store is not None:
            try:
                pdf_stats = self.vector_store.get_statistics()
                stats["pdf_rag"] = {
                    "status": "ready" if pdf_stats['total_chunks'] > 0 else "empty",
                    "total_chunks": pdf_stats['total_chunks'],
                    "categories": pdf_stats['categories'],
                    "persist_directory": pdf_stats['persist_directory']
                }
            except Exception as e:
                stats["pdf_rag"] = {"status": "error", "message": str(e)}

        # Legacy FAISS stats
        if self.index is None:
            stats["legacy_faiss"] = {
                "status": "not_initialized",
                "message": "Knowledge base not built yet"
            }
        else:
            categories = {}
            for doc in self.documents:
                cat = doc["category"]
                categories[cat] = categories.get(cat, 0) + 1

            stats["legacy_faiss"] = {
                "status": "ready",
                "total_documents": len(self.documents),
                "categories": categories,
                "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else None,
                "cache_available": self.index_path.exists()
            }

        return stats
