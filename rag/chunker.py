"""
Chunker - Intelligent text chunking for RAG system

Features:
- Semantic chunking (respect paragraph boundaries)
- Configurable chunk size and overlap
- Never split sentences mid-way
- Preserve metadata for each chunk
"""

import logging
import re
from typing import List, Dict
from dataclasses import dataclass, asdict
import hashlib

from rag.pdf_processor import PDFDocument


logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a text chunk with metadata"""
    text: str
    chunk_id: str
    source: str
    category: str
    page: int  # Approximate page number
    chunk_index: int  # Index within document
    total_chunks: int  # Total chunks in document
    file_path: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class Chunker:
    """Intelligent text chunker for documents"""

    def __init__(
        self,
        chunk_size: int = 700,
        overlap: int = 50,
        min_chunk_size: int = 100
    ):
        """
        Initialize chunker

        Args:
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap size in tokens (approximate)
            min_chunk_size: Minimum chunk size to avoid tiny chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

        logger.info(
            f"Chunker initialized - chunk_size: {chunk_size}, "
            f"overlap: {overlap}, min_chunk_size: {min_chunk_size}"
        )

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token on average
        return len(text) // 4

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Sentence boundaries (period, exclamation, question mark)
        # But not for common abbreviations
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+'

        sentences = re.split(sentence_pattern, text)

        # Clean sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs

        Args:
            text: Input text

        Returns:
            List of paragraphs
        """
        # Split on double newlines or multiple whitespace
        paragraphs = re.split(r'\n\s*\n', text)

        # Clean paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _create_chunks_from_sentences(
        self,
        sentences: List[str],
        target_size: int
    ) -> List[str]:
        """
        Create chunks from sentences, respecting target size

        Args:
            sentences: List of sentences
            target_size: Target chunk size in tokens

        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = self._estimate_tokens(sentence)

            # If adding this sentence exceeds target, start new chunk
            if current_size + sentence_size > target_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))

                # Start new chunk with overlap
                # Keep last few sentences for context
                overlap_sentences = []
                overlap_size = 0

                for sent in reversed(current_chunk):
                    sent_size = self._estimate_tokens(sent)
                    if overlap_size + sent_size <= self.overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_size += sent_size
                    else:
                        break

                current_chunk = overlap_sentences
                current_size = overlap_size

            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_size

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _generate_chunk_id(self, text: str, source: str, index: int) -> str:
        """
        Generate unique chunk ID

        Args:
            text: Chunk text
            source: Source filename
            index: Chunk index

        Returns:
            Unique chunk ID
        """
        # Use hash of source + index for stable IDs
        content = f"{source}_{index}_{text[:100]}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:12]

    def chunk_document(self, document: PDFDocument) -> List[TextChunk]:
        """
        Chunk a single document

        Args:
            document: PDFDocument to chunk

        Returns:
            List of TextChunk objects
        """
        logger.info(f"Chunking document: {document.source}")

        # Split into paragraphs first (semantic boundaries)
        paragraphs = self._split_into_paragraphs(document.text)
        logger.debug(f"Split into {len(paragraphs)} paragraphs")

        # Process each paragraph
        all_text_chunks = []

        for paragraph in paragraphs:
            # Split paragraph into sentences
            sentences = self._split_into_sentences(paragraph)

            # Create chunks from sentences
            paragraph_chunks = self._create_chunks_from_sentences(
                sentences,
                self.chunk_size
            )

            all_text_chunks.extend(paragraph_chunks)

        # Filter out tiny chunks
        all_text_chunks = [
            chunk for chunk in all_text_chunks
            if self._estimate_tokens(chunk) >= self.min_chunk_size
        ]

        logger.info(f"Created {len(all_text_chunks)} chunks from {document.source}")

        # Create TextChunk objects with metadata
        chunks = []

        for idx, chunk_text in enumerate(all_text_chunks):
            # Estimate page number (rough approximation)
            # Assume chunks are evenly distributed across pages
            progress = idx / len(all_text_chunks)
            estimated_page = max(1, int(progress * document.num_pages))

            chunk = TextChunk(
                text=chunk_text,
                chunk_id=self._generate_chunk_id(chunk_text, document.source, idx),
                source=document.source,
                category=document.category,
                page=estimated_page,
                chunk_index=idx,
                total_chunks=len(all_text_chunks),
                file_path=document.file_path
            )

            chunks.append(chunk)

        return chunks

    def chunk_documents(self, documents: List[PDFDocument]) -> List[TextChunk]:
        """
        Chunk multiple documents

        Args:
            documents: List of PDFDocument objects

        Returns:
            List of all TextChunk objects
        """
        logger.info(f"Chunking {len(documents)} documents")

        all_chunks = []

        for doc in documents:
            try:
                chunks = self.chunk_document(doc)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to chunk {doc.source}: {e}")
                continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Chunking Complete:")
        logger.info(f"  Total Chunks: {len(all_chunks)}")
        logger.info(f"  Avg Chunks/Doc: {len(all_chunks) / len(documents):.1f}")
        logger.info(f"{'='*60}\n")

        return all_chunks

    def get_statistics(self, chunks: List[TextChunk]) -> Dict:
        """
        Get chunking statistics

        Args:
            chunks: List of text chunks

        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_tokens_per_chunk": 0,
                "categories": {}
            }

        category_stats = {}
        total_tokens = 0

        for chunk in chunks:
            tokens = self._estimate_tokens(chunk.text)
            total_tokens += tokens

            if chunk.category not in category_stats:
                category_stats[chunk.category] = {
                    "count": 0,
                    "tokens": 0
                }

            category_stats[chunk.category]["count"] += 1
            category_stats[chunk.category]["tokens"] += tokens

        return {
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "avg_tokens_per_chunk": total_tokens / len(chunks),
            "min_tokens": min(self._estimate_tokens(c.text) for c in chunks),
            "max_tokens": max(self._estimate_tokens(c.text) for c in chunks),
            "categories": category_stats
        }


def main():
    """Test the chunker"""
    from rag.pdf_processor import PDFProcessor

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Process PDFs
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()

    if not documents:
        print("No documents to chunk!")
        return

    # Chunk documents
    chunker = Chunker(chunk_size=700, overlap=50)
    chunks = chunker.chunk_documents(documents)

    # Statistics
    stats = chunker.get_statistics(chunks)

    print("\n" + "="*60)
    print("CHUNKING STATISTICS")
    print("="*60)
    print(f"Total Chunks: {stats['total_chunks']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Avg Tokens/Chunk: {stats['avg_tokens_per_chunk']:.1f}")
    print(f"Min Tokens: {stats['min_tokens']}")
    print(f"Max Tokens: {stats['max_tokens']}")
    print("\nBy Category:")
    for cat, cat_stats in sorted(stats['categories'].items()):
        print(f"  {cat}: {cat_stats['count']} chunks ({cat_stats['tokens']:,} tokens)")
    print("="*60)

    # Show sample chunks
    print("\nSample Chunks:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i+1} ({chunk.category}):")
        print(f"  Source: {chunk.source}")
        print(f"  Page: ~{chunk.page}")
        print(f"  Text: {chunk.text[:200]}...")


if __name__ == "__main__":
    main()
