# PCOS Care MCP Server

Un server MCP (Model Context Protocol) per supporto e tracking PCOS, utilizzabile con Claude Desktop.

## 🎯 Cosa fa questo progetto

Questo MCP server fornisce tools AI-powered per:
- 📊 Tracking sintomi PCOS
- 📅 Monitoraggio ciclo mestruale  
- 🧠 Analisi pattern e insights
- 📚 Q&A evidence-based su PCOS (RAG)
- 🥗 Consigli nutrizionali personalizzati

## 🏗️ Architettura

```
Claude Desktop (UI)
        ↓
  MCP Protocol
        ↓
PCOS Care MCP Server (Python)
        ↓
    Data Layer (SQLite + FAISS)
```

## 📦 Installazione

### Prerequisiti
- Python 3.10+
- Claude Desktop
- npm (per MCP Inspector)

### Setup

1. **Clona/crea il progetto:**
```bash
mkdir pcos-care-mcp
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
- `sentence-transformers==2.2.2` - RAG embeddings
- `faiss-cpu>=1.7.4` - Vector search
- `pandas>=2.0.0` - Data analysis
- `scikit-learn>=1.3.0` - Pattern analysis
- `pytest>=7.4.0` - Testing framework

3. **Test il server:**
```bash
# Test server standalone
python3 test_server.py

# Run full test suite
pytest tests/ --cov=database --cov=tools --cov=rag
```

## 🧪 Testing

### Test Suite Completa

**✅ 70 unit tests con 74% code coverage**

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
- `rag/knowledge_base.py`: 21% (dipendenze opzionali)

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

Una volta connesso a Claude Desktop, puoi chattare naturalmente:

```
Tu: "Ciao! Voglio iniziare a tracciare i miei sintomi PCOS"

Claude: [usa il tool hello_pcos per verificare connessione]
        "Ciao! Benvenuta nel PCOS Care Assistant..."
```

## 🛠️ Tools Disponibili

### ✅ Implementati - FASE 3 COMPLETA

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

**Medical Info (RAG System):**
- `get_medical_info`: Q&A evidence-based su PCOS con citazioni fonti

**Utility:**
- `hello_pcos`: Tool di test per verificare connessione

### 🚧 Future Enhancements

- Risk assessment con Rotterdam criteria
- Integrazione con wearables per tracking automatico
- Grafici e visualizzazioni dati
- Export PDF report

## 📁 Struttura Progetto

```
pcos-care-mcp/
├── server.py                      # Main MCP server (entry point)
├── requirements.txt               # Dipendenze Python
├── test_server.py                 # Test automatici
├── test_with_inspector.sh         # Script per MCP Inspector
├── claude_desktop_config.json     # Config esempio
├── README.md                      # Questa documentazione
├── database/                      # Database layer
│   ├── __init__.py
│   ├── schema.py                  # SQLAlchemy ORM models
│   ├── db_manager.py              # Database operations
│   └── models.py                  # Pydantic validation models
├── tools/                         # Business logic tools
│   ├── __init__.py
│   ├── symptom_tracker.py         # Symptom tracking logic
│   ├── cycle_tracker.py           # Cycle tracking logic
│   └── pattern_analyzer.py        # Pattern analysis logic
├── rag/                           # RAG System (FASE 3)
│   ├── __init__.py
│   ├── knowledge_base.py          # FAISS + embeddings
│   └── pcos_documents.py          # Knowledge base documenti PCOS
├── data/                          # Data storage (auto-generated)
│   ├── pcos_care.db              # SQLite database
│   └── rag_cache/                # FAISS index cache
├── logs/                          # Application logs (auto-generated)
│   └── app.log
└── tests/                         # Unit tests (70 tests, 74% coverage)
    ├── __init__.py
    ├── test_database.py           # Database layer tests (13 tests)
    ├── test_symptom_tracker.py    # Symptom tracker tests (17 tests)
    ├── test_cycle_tracker.py      # Cycle tracker tests (17 tests)
    ├── test_pattern_analyzer.py   # Pattern analyzer tests (15 tests)
    └── test_rag.py                # RAG system tests (11 tests)
```

## 🎓 Sviluppo per Progetto Universitario

### Divisione Tasks (per gruppo)

**Persona 1: Tools & Database**
- Implementare `track_symptom()`
- Setup SQLite schema
- Tool `track_cycle()`

**Persona 2: RAG & Knowledge Base**
- Ingest documenti PCOS
- Setup FAISS vector store
- Tool `get_nutrition_tips()`

**Persona 3: Analytics & Testing**
- Tool `analyze_patterns()`
- Unit tests
- Documentazione

### Roadmap 3 Settimane

**Week 1:** ✅ COMPLETATA
- [x] Setup MCP server base
- [x] Test con MCP Inspector
- [x] Connessione Claude Desktop
- [x] Database SQLite + SQLAlchemy ORM
- [x] Tool `track_symptom()` completo

**Week 2:** ✅ COMPLETATA
- [x] Tool `track_cycle()` completo
- [x] RAG setup con FAISS + sentence-transformers
- [x] Knowledge base PCOS (15 documenti evidence-based)
- [x] Tool `get_medical_info()` con citazioni

**Week 3:** ✅ FASE 3 COMPLETATA
- [x] Pattern Analysis (correlazioni, trend, pattern ricorrenti)
- [x] Cycle analytics e predizioni
- [x] Error handling robusto
- [x] Logging professionale
- [x] README completo
- [x] Unit tests completi (70 tests, 74% coverage)
- [x] Documentazione completa
- [ ] Demo video (opzionale)
- [ ] Presentation slides (opzionale)

## 🐛 Troubleshooting

### "Module 'mcp' not found"
```bash
pip install mcp --break-system-packages
```

### "Server not connecting to Claude Desktop"
- Verifica che il path in `claude_desktop_config.json` sia corretto
- Riavvia Claude Desktop
- Controlla i log: `~/Library/Logs/Claude/` (macOS)

### "Permission denied"
```bash
chmod +x server.py
chmod +x test_with_inspector.sh
```

## 📚 Risorse

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)

## 📝 License

MIT License - Progetto universitario per corso "AI Frontiers: LLM"

## 👥 Contributors

- [Il tuo nome]
- [Nome gruppo 1]
- [Nome gruppo 2]

---

**Status:** ✅ v1.0.0 - PRODUCTION READY
**Features:** 12 Tools | Symptom + Cycle Tracking | Pattern Analysis | RAG System
**Quality:** 70 Unit Tests | 74% Coverage | Full Documentation
**Next:** 🎓 Presentazione progetto universitario
