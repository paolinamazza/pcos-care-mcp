"""
Embeddings Generator - Create vector embeddings for text chunks

Features:
- Sentence-Transformers model for embeddings
- Medical acronym expansion for better context
- Batch processing for efficiency
- Progress tracking with tqdm
"""

import logging
from typing import List, Dict, Optional
import numpy as np
from tqdm import tqdm

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

from rag.chunker import TextChunk


logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings for text chunks"""

    # Medical acronyms common in PCOS research
    MEDICAL_ACRONYMS = {
        "PCOS": "Polycystic Ovary Syndrome",
        "BMI": "Body Mass Index",
        "CVD": "Cardiovascular Disease",
        "IR": "Insulin Resistance",
        "T2D": "Type 2 Diabetes",
        "MetS": "Metabolic Syndrome",
        "SHBG": "Sex Hormone-Binding Globulin",
        "LH": "Luteinizing Hormone",
        "FSH": "Follicle-Stimulating Hormone",
        "AMH": "Anti-Müllerian Hormone",
        "HOMA-IR": "Homeostatic Model Assessment for Insulin Resistance",
        "OGTT": "Oral Glucose Tolerance Test",
        "HbA1c": "Glycated Hemoglobin",
        "HDL": "High-Density Lipoprotein",
        "LDL": "Low-Density Lipoprotein",
        "TG": "Triglycerides",
        "WHR": "Waist-to-Hip Ratio",
        "QOL": "Quality of Life",
        "PCOS-Q": "PCOS Questionnaire",
        "ART": "Assisted Reproductive Technology",
        "IVF": "In Vitro Fertilization",
    }

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 32,
        expand_acronyms: bool = True
    ):
        """
        Initialize embeddings generator

        Args:
            model_name: Sentence-transformers model name
            batch_size: Batch size for processing
            expand_acronyms: Whether to expand medical acronyms
        """
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.batch_size = batch_size
        self.expand_acronyms = expand_acronyms

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"Model loaded successfully (dim={self.model.get_sentence_embedding_dimension()})")

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text before embedding

        Args:
            text: Input text

        Returns:
            Preprocessed text
        """
        if not self.expand_acronyms:
            return text

        # Expand medical acronyms for better context
        processed = text

        for acronym, expansion in self.MEDICAL_ACRONYMS.items():
            # Replace acronym with "acronym (expansion)" pattern
            # But only if it's a standalone word
            import re
            pattern = r'\b' + re.escape(acronym) + r'\b'

            # Only replace first occurrence in each sentence to avoid repetition
            def replace_first(match):
                return f"{acronym} ({expansion})"

            processed = re.sub(pattern, replace_first, processed, count=1)

        return processed

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        preprocessed = self._preprocess_text(text)
        embedding = self.model.encode(preprocessed, convert_to_numpy=True)
        return embedding

    def generate_embeddings_batch(
        self,
        texts: List[str],
        show_progress: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches

        Args:
            texts: List of input texts
            show_progress: Show progress bar

        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")

        # Preprocess all texts
        preprocessed_texts = [self._preprocess_text(text) for text in texts]

        # Generate embeddings in batches
        all_embeddings = []

        if show_progress:
            pbar = tqdm(
                total=len(preprocessed_texts),
                desc="Generating embeddings",
                unit="chunk"
            )
        else:
            pbar = None

        for i in range(0, len(preprocessed_texts), self.batch_size):
            batch = preprocessed_texts[i:i + self.batch_size]

            # Generate embeddings for batch
            batch_embeddings = self.model.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False
            )

            all_embeddings.extend(batch_embeddings)

            if pbar:
                pbar.update(len(batch))

        if pbar:
            pbar.close()

        logger.info(f"Generated {len(all_embeddings)} embeddings")

        return all_embeddings

    def generate_chunk_embeddings(
        self,
        chunks: List[TextChunk],
        show_progress: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for text chunks

        Args:
            chunks: List of TextChunk objects
            show_progress: Show progress bar

        Returns:
            Dictionary mapping chunk_id to embedding vector
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")

        # Extract texts
        texts = [chunk.text for chunk in chunks]

        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts, show_progress=show_progress)

        # Create mapping
        chunk_embeddings = {
            chunk.chunk_id: embedding
            for chunk, embedding in zip(chunks, embeddings)
        }

        logger.info(f"Created embeddings for {len(chunk_embeddings)} chunks")

        return chunk_embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension

        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()

    def compute_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize embeddings
        norm1 = embedding1 / np.linalg.norm(embedding1)
        norm2 = embedding2 / np.linalg.norm(embedding2)

        # Compute cosine similarity
        similarity = np.dot(norm1, norm2)

        return float(similarity)

    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        chunk_embeddings: Dict[str, np.ndarray],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find most similar chunks to query

        Args:
            query_embedding: Query embedding
            chunk_embeddings: Dictionary of chunk embeddings
            top_k: Number of results to return

        Returns:
            List of (chunk_id, similarity_score) tuples
        """
        similarities = []

        for chunk_id, embedding in chunk_embeddings.items():
            similarity = self.compute_similarity(query_embedding, embedding)
            similarities.append((chunk_id, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]


def main():
    """Test the embeddings generator"""
    from rag.pdf_processor import PDFProcessor
    from rag.chunker import Chunker

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("="*60)
    print("EMBEDDINGS GENERATOR TEST")
    print("="*60)

    # Process PDFs
    print("\n1. Processing PDFs...")
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()

    if not documents:
        print("No documents found!")
        return

    # Chunk documents
    print("\n2. Chunking documents...")
    chunker = Chunker(chunk_size=700, overlap=50)
    chunks = chunker.chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # Generate embeddings (test with first 10 chunks)
    print("\n3. Generating embeddings (testing with first 10 chunks)...")
    test_chunks = chunks[:10]

    generator = EmbeddingsGenerator(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        batch_size=8
    )

    chunk_embeddings = generator.generate_chunk_embeddings(test_chunks)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Embedding Dimension: {generator.get_embedding_dimension()}")
    print(f"Generated Embeddings: {len(chunk_embeddings)}")
    print("\nSample Embeddings:")
    for i, (chunk_id, embedding) in enumerate(list(chunk_embeddings.items())[:3]):
        print(f"  Chunk {i+1} ({chunk_id}): shape={embedding.shape}, norm={np.linalg.norm(embedding):.4f}")

    # Test similarity search
    print("\n4. Testing similarity search...")
    query = "What are the diagnostic criteria for PCOS?"
    query_embedding = generator.generate_embedding(query)

    most_similar = generator.find_most_similar(
        query_embedding,
        chunk_embeddings,
        top_k=3
    )

    print(f"\nQuery: '{query}'")
    print("\nMost Similar Chunks:")
    for i, (chunk_id, score) in enumerate(most_similar):
        # Find the chunk
        chunk = next(c for c in test_chunks if c.chunk_id == chunk_id)
        print(f"\n{i+1}. Similarity: {score:.4f}")
        print(f"   Source: {chunk.source} ({chunk.category})")
        print(f"   Text: {chunk.text[:150]}...")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
