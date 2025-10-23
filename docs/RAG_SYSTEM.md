# PCOS RAG System

Sistema RAG (Retrieval-Augmented Generation) completo per il knowledge base PCOS basato su 28 PDF reali di ricerca scientifica.

## Architettura

```
docs/raw_pdfs/                    # 28 PDF organizzati in 6 categorie
    ├── 1_guidelines/             # 6 PDF - Linee guida cliniche
    ├── 2_nutrition/              # 6 PDF - Nutrizione e dieta
    ├── 3_exercise/               # 6 PDF - Esercizio fisico
    ├── 4_mental_health/          # 7 PDF - Salute mentale
    ├── 5_clinical/               # 2 PDF - Aspetti clinici
    └── 6_future_directions/      # 1 PDF - Direzioni future

rag/
    ├── pdf_processor.py          # Estrazione testo da PDF
    ├── chunker.py                # Chunking semantico
    ├── embeddings.py             # Generazione embeddings
    ├── vector_store.py           # ChromaDB integration
    └── knowledge_base.py         # API principale RAG

scripts/
    ├── setup_rag.py              # Setup completo (tutti i PDF)
    └── test_rag_quick.py         # Test rapido (3 PDF)

docs/processed/
    ├── embeddings/chroma_db/     # Database ChromaDB
    ├── chunks/metadata.json      # Metadata chunks
    └── rag_setup.log             # Log setup
```

## Features

### 1. PDF Processing (`pdf_processor.py`)
- Estrazione testo con `pypdf` (fallback a `pdfplumber`)
- Gestione PDF corrotti/scansionati
- Metadata extraction (categoria, pagine, source)
- Error handling robusto

### 2. Intelligent Chunking (`chunker.py`)
- Chunk size: ~700 tokens
- Overlap: ~50 tokens
- Split semantico (rispetta paragrafi/frasi)
- Mai split a metà frase
- Metadata per ogni chunk (source, category, page, chunk_id)

### 3. Embeddings Generation (`embeddings.py`)
- Model: `sentence-transformers/all-MiniLM-L6-v2` (384 dim)
- Espansione acronimi medici (PCOS, BMI, CVD, IR, etc.)
- Batch processing (32 chunks/batch)
- Progress bar con tqdm

### 4. Vector Store (`vector_store.py`)
- ChromaDB per similarity search
- Persistent storage
- Query con filtri per categoria
- Metadata completo per ogni chunk

## Setup

### 1. Installa dipendenze

```bash
pip install -r requirements.txt
```

Dipendenze principali:
- `pypdf==3.17.0` - PDF extraction
- `pdfplumber==0.10.3` - Fallback extraction
- `sentence-transformers>=2.2.0` - Embeddings
- `chromadb>=0.5.0` - Vector store
- `tqdm>=4.66.1` - Progress bars

### 2. Setup RAG completo (tutti i 28 PDF)

```bash
python3 scripts/setup_rag.py
```

Output:
- ChromaDB: `docs/processed/embeddings/chroma_db/`
- Metadata: `docs/processed/chunks/metadata.json`
- Logs: `docs/processed/rag_setup.log`

**Tempo stimato:** ~5-10 minuti (dipende dalla CPU)

### 3. Test rapido (solo 3 PDF)

```bash
python3 scripts/test_rag_quick.py
```

Test veloce per verificare che tutto funzioni.

## Utilizzo

### Query base

```python
from rag.vector_store import VectorStore

# Inizializza vector store
store = VectorStore()

# Query text-based
results = store.query_by_text(
    query_text="What are the Rotterdam criteria for PCOS?",
    top_k=5
)

# Risultati
for chunk in results['chunks']:
    print(f"Source: {chunk['metadata']['source']}")
    print(f"Category: {chunk['metadata']['category']}")
    print(f"Page: {chunk['metadata']['page']}")
    print(f"Distance: {chunk['distance']:.4f}")
    print(f"Text: {chunk['text'][:200]}...")
    print()
```

### Query con filtro categoria

```python
# Solo risultati dalla categoria "guidelines"
results = store.query_by_text(
    query_text="diagnostic criteria",
    top_k=5,
    category_filter="guidelines"
)
```

### Query con embedding custom

```python
from rag.embeddings import EmbeddingsGenerator

# Genera embedding custom
generator = EmbeddingsGenerator()
query_embedding = generator.generate_embedding("your query text")

# Query con embedding
results = store.query(
    query_embedding=query_embedding,
    top_k=5
)
```

### Statistiche vector store

```python
stats = store.get_statistics()

print(f"Total chunks: {stats['total_chunks']}")
print(f"Categories: {list(stats['categories'].keys())}")

for cat, cat_stats in stats['categories'].items():
    print(f"{cat}: {cat_stats['count']} chunks from {cat_stats['num_sources']} sources")
```

## Test Modules

### Test PDF Processor

```bash
cd /Users/paolinamazza/pcos-care-mcp
python3 rag/pdf_processor.py
```

### Test Chunker

```bash
python3 rag/chunker.py
```

### Test Embeddings

```bash
python3 rag/embeddings.py
```

### Test Vector Store

```bash
python3 rag/vector_store.py
```

## Performance

**Test su 28 PDF:**
- Documenti processati: 28
- Pagine totali: ~500-700
- Chunks creati: ~1000-1500
- Embedding dimension: 384
- Query speed: <100ms
- Storage: ~50-100MB

**Caratteristiche embedding:**
- Cosine similarity search
- Medical acronym expansion
- Context-aware chunking

## Troubleshooting

### PDF extraction fails
```python
# Se pypdf fallisce, il sistema usa automaticamente pdfplumber
# Per PDF scansionati, considera OCR preprocessing
```

### ChromaDB errors
```bash
# Rimuovi e ricrea il database
rm -rf docs/processed/embeddings/chroma_db
python3 scripts/setup_rag.py
```

### Memory issues
```python
# Riduci batch_size in embeddings.py
generator = EmbeddingsGenerator(batch_size=16)  # default: 32
```

## Next Steps (FASE 6)

1. **Integrazione con MCP server**
   - Aggiungere metodo `query_pdf_knowledge()` in `knowledge_base.py`
   - Mantenere backward compatibility

2. **Miglioramenti futuri**
   - Re-ranking con cross-encoder
   - Hybrid search (BM25 + semantic)
   - Query expansion con sinonimi medici
   - Multi-hop retrieval per query complesse

## References

- **ChromaDB**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/
- **Model**: all-MiniLM-L6-v2 (384 dim, 80M params)

## License

Questo sistema utilizza dati di ricerca scientifica PCOS. Rispettare le licenze dei documenti originali.
