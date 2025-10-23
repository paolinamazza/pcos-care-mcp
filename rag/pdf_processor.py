"""
PDF Processor - Extract text and metadata from PCOS research PDFs

Handles:
- PDF text extraction with error handling
- Metadata extraction (category, filename, pages)
- Corrupted/scanned PDF detection
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class PDFDocument:
    """Represents a processed PDF document with metadata"""
    text: str
    source: str
    category: str
    num_pages: int
    file_path: str
    extraction_method: str  # 'pypdf' or 'pdfplumber'


class PDFProcessor:
    """Process PDF files and extract text with metadata"""

    def __init__(self, pdf_dir: str = "docs/raw_pdfs"):
        """
        Initialize PDF processor

        Args:
            pdf_dir: Directory containing PDF files organized in categories
        """
        self.pdf_dir = Path(pdf_dir)

        if not self.pdf_dir.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

        # Check available libraries
        self.use_pypdf = pypdf is not None
        self.use_pdfplumber = pdfplumber is not None

        if not self.use_pypdf and not self.use_pdfplumber:
            raise ImportError(
                "Neither pypdf nor pdfplumber is installed. "
                "Install with: pip install pypdf pdfplumber"
            )

        logger.info(f"PDF Processor initialized with pdf_dir={pdf_dir}")
        logger.info(f"Available libraries - pypdf: {self.use_pypdf}, pdfplumber: {self.use_pdfplumber}")

    def _extract_category_from_path(self, pdf_path: Path) -> str:
        """
        Extract category from file path

        Args:
            pdf_path: Path to PDF file

        Returns:
            Category name (e.g., 'guidelines', 'nutrition')
        """
        # Category is the parent directory name (e.g., '1_guidelines' -> 'guidelines')
        category_raw = pdf_path.parent.name

        # Remove number prefix if present
        if '_' in category_raw:
            category = category_raw.split('_', 1)[1]
        else:
            category = category_raw

        return category

    def _extract_with_pypdf(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text using pypdf library

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        if not self.use_pypdf:
            return None

        try:
            text_parts = []

            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num} from {pdf_path.name}: {e}")
                        continue

            full_text = "\n\n".join(text_parts)

            # Check if extraction was successful (not empty or too short)
            if len(full_text.strip()) < 100:
                logger.warning(f"pypdf extraction too short for {pdf_path.name} ({len(full_text)} chars)")
                return None

            return full_text

        except Exception as e:
            logger.error(f"pypdf failed for {pdf_path.name}: {e}")
            return None

    def _extract_with_pdfplumber(self, pdf_path: Path) -> Optional[str]:
        """
        Extract text using pdfplumber library (fallback method)

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text or None if failed
        """
        if not self.use_pdfplumber:
            return None

        try:
            text_parts = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_parts.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num} from {pdf_path.name}: {e}")
                        continue

            full_text = "\n\n".join(text_parts)

            # Check if extraction was successful
            if len(full_text.strip()) < 100:
                logger.warning(f"pdfplumber extraction too short for {pdf_path.name} ({len(full_text)} chars)")
                return None

            return full_text

        except Exception as e:
            logger.error(f"pdfplumber failed for {pdf_path.name}: {e}")
            return None

    def _get_num_pages(self, pdf_path: Path) -> int:
        """
        Get number of pages in PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of pages or 0 if failed
        """
        try:
            if self.use_pypdf:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    return len(pdf_reader.pages)
            elif self.use_pdfplumber:
                with pdfplumber.open(pdf_path) as pdf:
                    return len(pdf.pages)
        except Exception as e:
            logger.warning(f"Failed to get page count for {pdf_path.name}: {e}")
            return 0

        return 0

    def process_pdf(self, pdf_path: Path) -> Optional[PDFDocument]:
        """
        Process a single PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFDocument object or None if processing failed
        """
        logger.info(f"Processing: {pdf_path.name}")

        # Extract metadata
        category = self._extract_category_from_path(pdf_path)
        num_pages = self._get_num_pages(pdf_path)

        # Try extraction with pypdf first, then pdfplumber as fallback
        text = None
        extraction_method = None

        if self.use_pypdf:
            text = self._extract_with_pypdf(pdf_path)
            if text:
                extraction_method = "pypdf"

        if not text and self.use_pdfplumber:
            logger.info(f"Falling back to pdfplumber for {pdf_path.name}")
            text = self._extract_with_pdfplumber(pdf_path)
            if text:
                extraction_method = "pdfplumber"

        if not text:
            logger.error(f"Failed to extract text from {pdf_path.name} (may be scanned/corrupted)")
            return None

        # Create document object
        doc = PDFDocument(
            text=text,
            source=pdf_path.name,
            category=category,
            num_pages=num_pages,
            file_path=str(pdf_path),
            extraction_method=extraction_method
        )

        logger.info(
            f"✓ Extracted {len(text)} chars from {pdf_path.name} "
            f"({num_pages} pages, category: {category}, method: {extraction_method})"
        )

        return doc

    def process_all_pdfs(self) -> List[PDFDocument]:
        """
        Process all PDF files in the directory

        Returns:
            List of successfully processed PDFDocument objects
        """
        # Find all PDF files
        pdf_files = list(self.pdf_dir.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")

        documents = []
        failed_count = 0

        for pdf_path in sorted(pdf_files):
            doc = self.process_pdf(pdf_path)

            if doc:
                documents.append(doc)
            else:
                failed_count += 1

        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"PDF Processing Complete:")
        logger.info(f"  ✓ Successfully processed: {len(documents)}")
        logger.info(f"  ✗ Failed: {failed_count}")
        logger.info(f"{'='*60}\n")

        # Log stats by category
        category_stats = {}
        for doc in documents:
            category_stats[doc.category] = category_stats.get(doc.category, 0) + 1

        logger.info("Documents by category:")
        for category, count in sorted(category_stats.items()):
            logger.info(f"  - {category}: {count} documents")

        return documents

    def get_statistics(self, documents: List[PDFDocument]) -> Dict:
        """
        Get processing statistics

        Args:
            documents: List of processed documents

        Returns:
            Dictionary with statistics
        """
        if not documents:
            return {
                "total_documents": 0,
                "total_pages": 0,
                "total_chars": 0,
                "categories": {},
                "avg_pages_per_doc": 0,
                "avg_chars_per_doc": 0
            }

        category_stats = {}
        total_pages = 0
        total_chars = 0

        for doc in documents:
            # Category stats
            if doc.category not in category_stats:
                category_stats[doc.category] = {
                    "count": 0,
                    "pages": 0,
                    "chars": 0
                }

            category_stats[doc.category]["count"] += 1
            category_stats[doc.category]["pages"] += doc.num_pages
            category_stats[doc.category]["chars"] += len(doc.text)

            total_pages += doc.num_pages
            total_chars += len(doc.text)

        return {
            "total_documents": len(documents),
            "total_pages": total_pages,
            "total_chars": total_chars,
            "categories": category_stats,
            "avg_pages_per_doc": total_pages / len(documents),
            "avg_chars_per_doc": total_chars / len(documents)
        }


def main():
    """Test the PDF processor"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    processor = PDFProcessor()
    documents = processor.process_all_pdfs()

    stats = processor.get_statistics(documents)

    print("\n" + "="*60)
    print("PROCESSING STATISTICS")
    print("="*60)
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Total Pages: {stats['total_pages']}")
    print(f"Total Characters: {stats['total_chars']:,}")
    print(f"Avg Pages/Doc: {stats['avg_pages_per_doc']:.1f}")
    print(f"Avg Chars/Doc: {stats['avg_chars_per_doc']:,.0f}")
    print("\nBy Category:")
    for cat, cat_stats in sorted(stats['categories'].items()):
        print(f"  {cat}: {cat_stats['count']} docs, {cat_stats['pages']} pages")
    print("="*60)


if __name__ == "__main__":
    main()
