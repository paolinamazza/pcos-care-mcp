# PCOS MCP Server - PDF RAG Integration Guide

## Overview

Il server MCP è stato aggiornato per utilizzare il nuovo sistema RAG basato su **28 PDF reali** di ricerca scientifica PCOS, con fallback automatico al sistema legacy.

## Architettura

```
MCP Server (server.py)
    ↓
PCOSKnowledgeBase (rag/knowledge_base.py)
    ↓
    ├─→ PDF RAG System (PRIMARY)
    │   ├─→ VectorStore (ChromaDB)
    │   ├─→ EmbeddingsGenerator
    │   └─→ 28 PDF reali (docs/raw_pdfs/)
    │
    └─→ Legacy FAISS System (FALLBACK)
        └─→ Hardcoded documents (pcos_documents.py)
```

## Setup Completo

### 1. Installa Dipendenze

```bash
pip install -r requirements.txt
```

### 2. Popola ChromaDB

**Opzione A: Setup completo (tutti i 28 PDF)**

```bash
python3 scripts/setup_rag.py
```

Tempo stimato: ~5-10 minuti
Output:
- ChromaDB: `docs/processed/embeddings/chroma_db/`
- Metadata: `docs/processed/chunks/metadata.json`
- Logs: `docs/processed/rag_setup.log`

**Opzione B: Test rapido (3 PDF)**

```bash
python3 scripts/test_rag_quick.py
```

Crea un database di test in `docs/processed/embeddings/test_chroma_db/`

### 3. Test Integrazione

```bash
python3 scripts/test_knowledge_base_integration.py
```

Questo script testa:
- Inizializzazione knowledge base
- Query al sistema PDF RAG
- Filtri per categoria
- Fallback al sistema legacy

### 4. Avvia il Server

```bash
python3 server.py
```

Il server:
- Carica automaticamente il sistema PDF RAG se disponibile
- Effettua fallback al sistema legacy se ChromaDB è vuoto
- Log dettagliato della configurazione

## Utilizzo via MCP

### Tool: `get_medical_info`

**Parametri:**
- `question` (string, required): La domanda sulla PCOS
- `num_sources` (integer, 1-5, default=3): Numero di fonti da consultare

**Esempio 1: Query base**

```json
{
  "question": "What are the Rotterdam criteria for PCOS?"
}
```

**Esempio 2: Query con più fonti**

```json
{
  "question": "How does exercise help with PCOS?",
  "num_sources": 5
}
```

**Response Format:**

```
🧠 Informazioni PCOS - Evidence-Based
📚 Sistema: PDF RAG (28 research papers)

Domanda: What are the Rotterdam criteria for PCOS?

Risposta:
[Context estratto dai PDF...]

Fonti consultate:
1. **guideline.pdf** (Categoria: guidelines)
   Pagina: ~15
   Rilevanza: 85%
   Preview: The Rotterdam criteria require 2 of 3...

2. **clinical_review.pdf** (Categoria: clinical)
   Pagina: ~3
   Rilevanza: 78%
   Preview: PCOS diagnosis according to Rotterdam...

📊 Chunk trovati: 12

💡 Questa è un'informazione generale. Per diagnosi e trattamenti, consulta sempre un medico.
```

## Features del Nuovo Sistema

### ✅ PDF RAG System (Primary)

**Vantaggi:**
- ✅ 28 PDF reali di ricerca scientifica
- ✅ ~1000-1500 chunks per coverage completa
- ✅ Citazioni con numero pagina
- ✅ Categoria del documento (guidelines, nutrition, exercise, etc.)
- ✅ Preview del chunk per context
- ✅ Filtri per categoria
- ✅ Confidence score

**Categorie disponibili:**
- `guidelines` - Linee guida cliniche (6 PDF)
- `nutrition` - Nutrizione e dieta (6 PDF)
- `exercise` - Esercizio fisico (6 PDF)
- `mental_health` - Salute mentale (7 PDF)
- `clinical` - Aspetti clinici (2 PDF)
- `future_directions` - Direzioni future (1 PDF)

### 🔄 Fallback Automatico

Se il sistema PDF RAG non è disponibile:
1. Log warning: "PDF RAG failed, falling back to legacy system"
2. Usa sistema FAISS con documenti hardcoded
3. Response indica il sistema usato

**Quando avviene il fallback:**
- ChromaDB vuoto (non eseguito `setup_rag.py`)
- Errore nel query ChromaDB
- Dipendenze mancanti

## API Programmatica

### Python

```python
from rag.knowledge_base import PCOSKnowledgeBase

# Initialize with PDF RAG
kb = PCOSKnowledgeBase(use_pdf_rag=True)

# Query
result = kb.query_pdf_knowledge(
    query="What are the Rotterdam criteria?",
    top_k=5,
    category_filter="guidelines",  # Optional
    include_sources=True
)

if result['success']:
    print(f"Context: {result['context']}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Confidence: {result['confidence']:.2%}")

    for source in result['sources']:
        print(f"- {source['title']} (page {source['page']})")
else:
    print(f"Error: {result['message']}")
```

### Statistics

```python
stats = kb.get_stats()

# PDF RAG stats
if 'pdf_rag' in stats:
    print(f"Total chunks: {stats['pdf_rag']['total_chunks']}")
    print(f"Categories: {stats['pdf_rag']['categories']}")

# Legacy system stats
if 'legacy_faiss' in stats:
    print(f"Documents: {stats['legacy_faiss']['total_documents']}")
```

## Troubleshooting

### Problema: "ChromaDB is empty"

**Causa:** Non è stato eseguito `setup_rag.py`

**Soluzione:**
```bash
python3 scripts/setup_rag.py
```

### Problema: "PDF RAG system not available"

**Causa:** Dipendenze mancanti

**Soluzione:**
```bash
pip install pypdf pdfplumber chromadb sentence-transformers
```

### Problema: Server usa sistema legacy invece di PDF RAG

**Debug:**
```python
# In server.py, dopo l'init:
logger.info(f"PDF RAG enabled: {knowledge_base.use_pdf_rag}")
stats = knowledge_base.get_stats()
logger.info(f"Stats: {stats}")
```

**Possibili cause:**
1. ChromaDB vuoto → Esegui `setup_rag.py`
2. Errore init → Controlla logs in `logs/app.log`
3. Dipendenze mancanti → Reinstalla requirements

### Problema: Query ritorna risultati non rilevanti

**Soluzioni:**
1. Riformula la query in modo più specifico
2. Usa category filter per restringere la ricerca
3. Aumenta `top_k` per avere più context
4. Controlla il confidence score (se < 0.5, risultati poco rilevanti)

### Problema: Performance lento

**Ottimizzazioni:**
1. Riduci `top_k` (default: 5)
2. Usa category filter per ridurre search space
3. Verifica dimensione ChromaDB: `du -sh docs/processed/embeddings/chroma_db/`

## Logs e Monitoring

### Locations

- Server logs: `logs/app.log`
- RAG setup logs: `docs/processed/rag_setup.log`

### Eventi chiave da monitorare

**Startup:**
```
INFO - Initializing PDF-based RAG system...
INFO - PDF RAG system ready: 1234 chunks from 6 categories
```

**Query:**
```
INFO - Tool called: get_medical_info with args: {'question': '...'}
INFO - PDF RAG query successful
```

**Fallback:**
```
WARNING - PDF RAG failed, falling back to legacy system
INFO - Using legacy FAISS system
```

## Performance Benchmarks

**Setup time (28 PDF):**
- PDF processing: ~1-2 min
- Chunking: ~10 sec
- Embeddings: ~2-4 min
- ChromaDB storage: ~10 sec
- **Total: ~5-10 min**

**Query time:**
- PDF RAG: <100ms
- Legacy FAISS: <50ms

**Storage:**
- ChromaDB: ~50-100MB
- Embeddings cache: ~20-30MB

## Migration Notes

### Da Legacy a PDF RAG

Il sistema mantiene **backward compatibility**:
- Stesso tool name: `get_medical_info`
- Stessi parametri input
- Response format simile (con più metadata)

**Differenze response:**
```diff
  🧠 Informazioni PCOS - Evidence-Based
+ 📚 Sistema: PDF RAG (28 research papers)

  Fonti consultate:
  1. **guideline.pdf** (Categoria: guidelines)
+    Pagina: ~15
     Rilevanza: 85%
+    Preview: The Rotterdam criteria...

+ 📊 Chunk trovati: 12
```

### Rollback a Legacy System

Se necessario tornare al sistema legacy:

```python
# In server.py, line 59-66:
knowledge_base = PCOSKnowledgeBase(use_pdf_rag=False)
knowledge_base.build_index()  # Build FAISS
```

O semplicemente rimuovi `docs/processed/embeddings/chroma_db/`

## Next Steps

1. **✅ DONE:** Setup base PDF RAG
2. **✅ DONE:** Integrazione con MCP server
3. **TODO:** Re-ranking con cross-encoder per migliorare relevance
4. **TODO:** Hybrid search (BM25 + semantic)
5. **TODO:** Query expansion con sinonimi medici
6. **TODO:** Multi-hop retrieval per query complesse

## Support

Per problemi o domande:
1. Controlla i logs in `logs/app.log`
2. Verifica lo stato con `get_stats()`
3. Testa con `scripts/test_knowledge_base_integration.py`
