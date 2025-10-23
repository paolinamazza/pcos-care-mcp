# PCOS Care MCP Server

Un server MCP (Model Context Protocol) per supporto e tracking PCOS, utilizzabile con Claude Desktop.

## 🎯 Cosa fa questo progetto

Questo MCP server fornisce tools AI-powered per:
- 📊 **Tracking sintomi PCOS** con insights intelligenti
- 📅 **Monitoraggio ciclo mestruale** con predizioni
- 🧠 **Analisi pattern** e correlazioni sintomi-ciclo
- 📚 **Q&A evidence-based su PCOS** (RAG con 28 PDF reali di ricerca)
- 💡 **Consigli personalizzati** basati sui tuoi dati

## ✨ Novità v2.0 - Sistema RAG PDF

**🎉 Nuovo sistema RAG basato su 28 PDF reali di ricerca scientifica PCOS!**

- ✅ **8,978 chunks** da 27 PDF scientifici (~6,400 pagine)
- ✅ **6 categorie** (guidelines, nutrition, exercise, mental_health, clinical, future_directions)
- ✅ **Citazioni con pagina** per ogni risposta
- ✅ **Ricerca semantica** con ChromaDB
- ✅ **Filtri per categoria** per query mirate
- ✅ **Fallback automatico** al sistema legacy

## 🏗️ Architettura

```
Claude Desktop (UI)
        ↓
  MCP Protocol
        ↓
PCOS Care MCP Server (Python)
        ↓
    ├─→ Symptom/Cycle Tracking (SQLite)
    └─→ RAG System (ChromaDB + 28 PDF)
            ↓
        PDF Knowledge Base
        - 8,978 semantic chunks
        - 6 categories
        - Real-time retrieval
```

## 📦 Installazione

### Prerequisiti
- Python 3.10+
- Claude Desktop
- npm (per MCP Inspector)

### Setup Rapido

1. **Clona il progetto:**
```bash
git clone https://github.com/paolinamazza/pcos-care-mcp.git
cd pcos-care-mcp
```

2. **Installa dipendenze:**
```bash
pip install -r requirements.txt
```

**Dipendenze principali:**
- `mcp>=0.9.0` - MCP Server SDK
- `sqlalchemy>=2.0.0` - Database ORM
- `pydantic>=2.0.0` - Data validation
- `sentence-transformers>=2.2.0` - Embeddings
- `chromadb>=0.5.0` - Vector database (attualmente 1.2.1)
- `pypdf==3.17.0` - PDF extraction
- `pdfplumber==0.10.3` - Fallback PDF extraction
- `pandas>=2.0.0` - Data analysis
- `scikit-learn>=1.3.0` - Pattern analysis
- `pytest>=7.4.0` - Testing

3. **Setup RAG Knowledge Base (IMPORTANTE!):**

```bash
# Setup completo con tutti i 28 PDF (~7 minuti)
python3 scripts/setup_rag.py

# Oppure test rapido con 3 PDF (~1 minuto)
python3 scripts/test_rag_quick.py
```

**Output atteso:**
```
📊 FINAL SUMMARY:
  Documents Processed: 27
  Pages Processed: 6,396
  Chunks Created: 8,978
  Embeddings Generated: 8,978
  Time Elapsed: ~400 seconds
```

4. **Test il server:**
```bash
# Test server standalone
python3 test_server.py

# Test integrazione RAG
python3 scripts/test_knowledge_base_integration.py

# Run full test suite
pytest tests/ --cov=database --cov=tools --cov=rag
```

## 🧪 Testing

### Test Suite Completa

**✅ 70+ unit tests con 74% code coverage**

```bash
# Run all tests with coverage
pytest tests/ --cov=database --cov=tools --cov=rag --cov-report=term-missing

# Run specific test file
pytest tests/test_cycle_tracker.py -v
pytest tests/test_pattern_analyzer.py -v
pytest tests/test_rag.py -v
pytest tests/test_symptom_tracker.py -v
```

**Coverage per modulo:**
- `database/`: 81-94% ✅
- `tools/symptom_tracker.py`: 80% ✅
- `tools/cycle_tracker.py`: 78% ✅
- `tools/pattern_analyzer.py`: 84% ✅
- `rag/knowledge_base.py`: Completo con PDF RAG ✅

### Test RAG System

```bash
# Test quick (3 PDF)
python3 scripts/test_rag_quick.py

# Test integrazione completa
python3 scripts/test_knowledge_base_integration.py

# Verifica ChromaDB
python3 -c "from rag.vector_store import VectorStore; store = VectorStore(); print(store.get_statistics())"
```

### Test con MCP Inspector
```bash
./test_with_inspector.sh
```

MCP Inspector aprirà un'interfaccia web dove puoi:
- Vedere tutti i 12 tools disponibili
- Testare ogni tool manualmente
- Vedere i log in real-time

## 🔌 Connessione a Claude Desktop

### Su macOS/Linux:

1. **Trova il file di configurazione:**
```bash
# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

2. **Aggiungi questa configurazione:**
```json
{
  "mcpServers": {
    "pcos-care": {
      "command": "python3",
      "args": [
        "/percorso/completo/a/pcos-care-mcp/server.py"
      ]
    }
  }
}
```

3. **Riavvia Claude Desktop**

4. **Verifica connessione:**
   - Apri Claude Desktop
   - Cerca l'icona 🔌 o "MCP" nella UI
   - Dovresti vedere "pcos-care" connesso

### Su Windows:

1. **File di configurazione:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

2. **Usa path Windows:**
```json
{
  "mcpServers": {
    "pcos-care": {
      "command": "python",
      "args": [
        "C:\\path\\to\\pcos-care-mcp\\server.py"
      ]
    }
  }
}
```

## 📖 Uso

### Esempi di Conversazioni

**Tracking Sintomi:**
```
Tu: "Ho avuto crampi intensi oggi, intensità 7"
Claude: [usa track_symptom]
     ✅ Sintomo registrato!
     Tipo: crampi
     Intensità: 7/10
     💡 Insights: Questo è il 3° episodio questo mese...
```

**Query RAG System:**
```
Tu: "Quali sono i criteri Rotterdam per la PCOS?"
Claude: [usa get_medical_info con nuovo sistema PDF RAG]
     🧠 Informazioni PCOS - Evidence-Based
     📚 Sistema: PDF RAG (28 research papers)

     Risposta: [Context dai PDF reali con 8,978 chunks...]

     Fonti consultate:
     1. Evidence-Based-Guidelines-2023.pdf (Categoria: guidelines)
        Pagina: ~145
        Rilevanza: 85%
        Preview: The Rotterdam criteria require 2 of 3...

     📊 Chunk trovati: 12
```

**Analisi Pattern:**
```
Tu: "Analizza i pattern tra i miei sintomi e il ciclo"
Claude: [usa analyze_symptom_cycle_correlation]
     📊 Analisi Correlazione Sintomi-Ciclo

     Pattern identificati:
     - Crampi più intensi durante fase mestruale (correlazione 0.85)
     - Acne aumenta pre-mestruale
     ...
```

## 🛠️ Tools Disponibili

### ✅ Implementati - v2.0 COMPLETA

**Symptom Tracking:**
- `track_symptom`: Registra sintomi PCOS con intensità e note
- `get_recent_symptoms`: Visualizza storico sintomi
- `get_symptom_summary`: Statistiche e insights sui sintomi

**Cycle Tracking:**
- `track_cycle`: Registra ciclo mestruale (inizio, fine, intensità flusso)
- `update_cycle_end`: Aggiorna data fine ciclo
- `get_cycle_history`: Storico cicli mestruali
- `get_cycle_analytics`: Analytics avanzate (regolarità, predizione prossimo ciclo)

**Pattern Analysis:**
- `analyze_symptom_cycle_correlation`: Correlazioni tra sintomi e fasi del ciclo
- `analyze_symptom_trends`: Trend sintomi nel tempo
- `identify_patterns`: Identifica pattern ricorrenti

**Medical Info (RAG System v2.0 - PDF):**
- `get_medical_info`: Q&A evidence-based su PCOS con:
  - ✨ **28 PDF reali** di ricerca scientifica
  - ✨ **8,978 chunks** semantici
  - ✨ **Citazioni con pagina**
  - ✨ **Filtri per categoria**
  - ✨ **Preview dei chunk**
  - ✨ **Confidence score**

**Utility:**
- `hello_pcos`: Tool di test per verificare connessione

## 📊 Sistema RAG - Dettagli Tecnici

### Knowledge Base

**27 PDF Processati:**
- **Guidelines**: 6 PDF, 8,451 chunks (Evidence-Based Guidelines 2023, etc.)
- **Nutrition**: 6 PDF, 86 chunks (dieta, alimentazione, lifestyle)
- **Exercise**: 6 PDF, 179 chunks (attività fisica, exercise recommendations)
- **Mental Health**: 6 PDF, 159 chunks (anxiety, depression, psychological support)
- **Clinical**: 2 PDF, 68 chunks (cardiovascular, metabolic aspects)
- **Future Directions**: 1 PDF, 35 chunks (research frontiers)

**Statistiche:**
- 📄 6,396 pagine processate
- 🧩 8,978 chunks semantici (avg: 318 tokens/chunk)
- 🔍 384-dim embeddings (all-MiniLM-L6-v2)
- ⚡ Query speed: <100ms
- 💾 ChromaDB v1.2.1 (persistent storage)

### Query Features

```python
# Query con filtro categoria
result = store.query_by_text(
    "exercise recommendations",
    top_k=5,
    category_filter="exercise"  # Solo risultati da PDF exercise
)

# Response include:
# - context: Text rilevante dai chunk
# - sources: Lista fonti con:
#   - title: Nome PDF
#   - category: Categoria documento
#   - page: Numero pagina approssimativo
#   - relevance_score: Score 0-1
#   - chunk_preview: Preview del testo
# - confidence: Overall confidence score
# - total_chunks_found: Numero chunk trovati
```

### Fallback System

Il sistema ha fallback automatico:
1. **Primary**: PDF RAG (ChromaDB con 8,978 chunks)
2. **Fallback**: Legacy FAISS system (documenti hardcoded)

Il fallback avviene automaticamente se:
- ChromaDB vuoto (non eseguito setup)
- Errori durante query
- Dipendenze mancanti

## 📁 Struttura Progetto

```
pcos-care-mcp/
├── server.py                      # Main MCP server (entry point)
├── requirements.txt               # Dipendenze Python
├── test_server.py                 # Test automatici
├── test_with_inspector.sh         # Script per MCP Inspector
├── claude_desktop_config.json     # Config esempio
├── README.md                      # Questa documentazione
│
├── database/                      # Database layer (SQLite)
│   ├── __init__.py
│   ├── schema.py                  # SQLAlchemy ORM models
│   ├── db_manager.py              # Database operations
│   └── models.py                  # Pydantic validation models
│
├── tools/                         # Business logic tools
│   ├── __init__.py
│   ├── symptom_tracker.py         # Symptom tracking logic
│   ├── cycle_tracker.py           # Cycle tracking logic
│   └── pattern_analyzer.py        # Pattern analysis logic
│
├── rag/                           # RAG System v2.0 (PDF-based)
│   ├── __init__.py
│   ├── knowledge_base.py          # Unified API (PDF RAG + Legacy fallback)
│   ├── pdf_processor.py           # PDF text extraction (pypdf/pdfplumber)
│   ├── chunker.py                 # Semantic chunking (700 tokens, 50 overlap)
│   ├── embeddings.py              # Embeddings generator (sentence-transformers)
│   ├── vector_store.py            # ChromaDB integration (v0.x & v1.x compatible)
│   └── pcos_documents.py          # Legacy hardcoded documents (fallback)
│
├── scripts/                       # Setup & test scripts
│   ├── setup_rag.py               # Full RAG setup (all 28 PDF)
│   ├── test_rag_quick.py          # Quick test (3 PDF)
│   └── test_knowledge_base_integration.py  # Integration tests
│
├── docs/                          # Documentation
│   ├── raw_pdfs/                  # 28 PDF organized in 6 categories
│   │   ├── 1_guidelines/         (6 PDF)
│   │   ├── 2_nutrition/          (6 PDF)
│   │   ├── 3_exercise/           (6 PDF)
│   │   ├── 4_mental_health/      (7 PDF)
│   │   ├── 5_clinical/           (2 PDF)
│   │   └── 6_future_directions/  (1 PDF)
│   ├── processed/                 # Generated data
│   │   ├── embeddings/chroma_db/  # ChromaDB persistent storage
│   │   ├── chunks/metadata.json   # Chunks metadata
│   │   └── rag_setup.log          # Setup logs
│   ├── RAG_SYSTEM.md              # RAG technical guide
│   └── INTEGRATION_GUIDE.md       # MCP integration guide
│
├── data/                          # Data storage (auto-generated)
│   ├── pcos_care.db              # SQLite database (symptoms + cycles)
│   └── rag_cache/                # Legacy FAISS index cache
│
├── logs/                          # Application logs (auto-generated)
│   └── app.log
│
└── tests/                         # Unit tests (70+ tests, 74% coverage)
    ├── __init__.py
    ├── test_database.py           # Database layer tests (13 tests)
    ├── test_symptom_tracker.py    # Symptom tracker tests (17 tests)
    ├── test_cycle_tracker.py      # Cycle tracker tests (17 tests)
    ├── test_pattern_analyzer.py   # Pattern analyzer tests (15 tests)
    └── test_rag.py                # RAG system tests (11 tests)
```

## 🔧 Manutenzione

### Ricostruire il Knowledge Base

Se aggiungi nuovi PDF o modifichi quelli esistenti:

```bash
# 1. Aggiungi PDF in docs/raw_pdfs/[categoria]/
# 2. Ricostruisci il database
python3 scripts/setup_rag.py

# 3. Verifica
python3 -c "from rag.vector_store import VectorStore; print(VectorStore().get_statistics())"
```

### Backup Database

```bash
# Backup SQLite (symptoms + cycles)
cp data/pcos_care.db data/pcos_care_backup_$(date +%Y%m%d).db

# Backup ChromaDB (non necessario, persistente)
# Il database è già in docs/processed/embeddings/chroma_db/
```

### Update Dependencies

```bash
pip install --upgrade sentence-transformers chromadb pypdf
python3 scripts/setup_rag.py  # Rebuild se necessario
```

## 🐛 Troubleshooting

### "Module 'mcp' not found"
```bash
pip install mcp --break-system-packages
```

### "ChromaDB is empty"
```bash
# Setup il knowledge base
python3 scripts/setup_rag.py

# Verifica
python3 scripts/test_knowledge_base_integration.py
```

### "Server not connecting to Claude Desktop"
- Verifica che il path in `claude_desktop_config.json` sia corretto (path assoluto!)
- Riavvia Claude Desktop
- Controlla i log: `~/Library/Logs/Claude/` (macOS)
- Verifica che Python 3.10+ sia installato: `python3 --version`

### "Permission denied"
```bash
chmod +x server.py
chmod +x test_with_inspector.sh
chmod +x scripts/*.py
```

### "PDF extraction failed"
Se un PDF non viene estratto:
- Il sistema prova automaticamente pypdf → pdfplumber
- PDF scansionati potrebbero non essere leggibili (serve OCR)
- Controlla i log in `docs/processed/rag_setup.log`

### "Query returns irrelevant results"
- Riformula la query in modo più specifico
- Usa i filtri per categoria: `category_filter="guidelines"`
- Aumenta `top_k` per ottenere più context
- Controlla il confidence score (<0.5 = bassa rilevanza)

## 📚 Risorse

### Documentation
- [RAG System Technical Guide](docs/RAG_SYSTEM.md)
- [MCP Integration Guide](docs/INTEGRATION_GUIDE.md)

### External Links
- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 🎓 Sviluppo per Progetto Universitario

### Roadmap Completa

**✅ v1.0 - FASE 1-2 (Settimana 1-2):**
- [x] Setup MCP server base
- [x] Database SQLite + SQLAlchemy ORM
- [x] Symptom & Cycle tracking completo
- [x] RAG setup con FAISS (legacy)
- [x] 15 documenti hardcoded

**✅ v2.0 - FASE 3 (Settimana 3):**
- [x] **Nuovo sistema RAG con 28 PDF reali**
- [x] Pattern Analysis (correlazioni, trend)
- [x] Cycle analytics e predizioni
- [x] Unit tests completi (70+ tests)
- [x] Documentazione tecnica completa

**🚀 v2.1 - Enhancements (Opzionali):**
- [ ] Re-ranking con cross-encoder
- [ ] Hybrid search (BM25 + semantic)
- [ ] Query expansion
- [ ] Web UI per data visualization
- [ ] Export PDF reports

### Divisione Tasks (per gruppo)

**Persona 1: Backend & Database**
- ✅ Setup SQLite + SQLAlchemy
- ✅ Symptom/Cycle tracking API
- ✅ Pattern analyzer
- ✅ Unit tests database layer

**Persona 2: RAG & Knowledge Base**
- ✅ PDF processing pipeline
- ✅ ChromaDB integration
- ✅ Embeddings generation
- ✅ Query optimization
- ✅ Documentation RAG system

**Persona 3: MCP Integration & Testing**
- ✅ Server.py MCP integration
- ✅ Tool schemas & validation
- ✅ Integration tests
- ✅ README & guides
- ✅ Demo preparation

## 📊 Metriche Progetto

**Codice:**
- 📝 3,000+ lines of code
- 🧪 70+ unit tests (74% coverage)
- 📁 50+ files

**Features:**
- 🛠️ 12 tools MCP
- 📚 8,978 knowledge chunks
- 📄 27 PDF processed
- 🔍 6 categorie ricerca

**Performance:**
- ⚡ Query <100ms
- 📊 Setup ~7 minuti
- 💾 ~100MB storage
- 🎯 85% avg relevance

## 📝 License

MIT License - Progetto universitario per corso "AI Frontiers: LLM"

## 👥 Contributors

- Paolina Mazza - [@paolinamazza](https://github.com/paolinamazza)

---

**Status:** ✅ v2.0.0 - PRODUCTION READY with PDF RAG
**Features:** 12 Tools | Symptom + Cycle Tracking | Pattern Analysis | PDF RAG (8,978 chunks)
**Quality:** 70+ Unit Tests | 74% Coverage | Complete Documentation
**Next:** 🎓 Presentazione progetto universitario

---

## 🌟 Changelog

### v2.0.0 (2025-10-23) - PDF RAG System
- ✨ **NEW:** Sistema RAG basato su 28 PDF reali di ricerca
- ✨ **NEW:** 8,978 chunks semantici con ChromaDB
- ✨ **NEW:** Citazioni con pagina e preview chunk
- ✨ **NEW:** 6 categorie filtrabili
- ✨ **NEW:** Fallback automatico al sistema legacy
- ✨ **NEW:** Scripts per setup e testing
- ✨ **NEW:** Documentazione tecnica completa
- 🔧 **FIX:** ChromaDB compatibility (v0.x e v1.x)
- 🔧 **FIX:** Import dependencies opzionali
- 📚 **DOCS:** RAG_SYSTEM.md e INTEGRATION_GUIDE.md

### v1.0.0 (2025-10-20) - Initial Release
- ✅ MCP server base
- ✅ Symptom & Cycle tracking
- ✅ Pattern analysis
- ✅ RAG legacy system (FAISS)
- ✅ 70+ unit tests
