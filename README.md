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
pip install mcp --break-system-packages
```

3. **Test il server:**
```bash
python3 test_server.py
```

## 🧪 Testing

### Test automatico
```bash
python3 test_server.py
```

### Test con MCP Inspector
```bash
./test_with_inspector.sh
```

MCP Inspector aprirà un'interfaccia web dove puoi:
- Vedere tutti i tools disponibili
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
└── tests/                         # Unit tests
    ├── __init__.py
    └── test_database.py
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
- [ ] Unit tests completi (in progress)
- [ ] Demo video
- [ ] Presentation slides

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

**Status:** ✅ v0.3 - FASE 3 COMPLETA
**Features:** Symptom + Cycle Tracking, Pattern Analysis, RAG System
**Next:** 🧪 Testing completo e presentazione progetto
