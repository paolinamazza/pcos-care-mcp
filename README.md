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

### ✅ Implementati

- `hello_pcos`: Tool di test per verificare connessione

### 🚧 In sviluppo

- `track_symptom`: Registra sintomi giornalieri
- `track_cycle`: Traccia ciclo mestruale
- `analyze_patterns`: Analizza pattern nei dati
- `get_nutrition_tips`: Consigli nutrizionali RAG-based
- `risk_assessment`: Valutazione rischio Rotterdam criteria

## 📁 Struttura Progetto

```
pcos-care-mcp/
├── server.py                      # Main MCP server
├── test_server.py                 # Test automatici
├── test_with_inspector.sh         # Script per MCP Inspector
├── claude_desktop_config.json     # Config esempio
├── README.md                      # Questa documentazione
└── (in futuro)
    ├── database.py                # SQLite database layer
    ├── rag.py                     # RAG per knowledge base PCOS
    └── tools/                     # Tools individuali
        ├── symptom_tracker.py
        ├── cycle_tracker.py
        └── nutrition.py
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

**Week 1:**
- [x] Setup MCP server base
- [x] Test con MCP Inspector
- [x] Connessione Claude Desktop
- [ ] Database SQLite
- [ ] Tool `track_symptom()`

**Week 2:**
- [ ] Tool `track_cycle()`
- [ ] RAG setup
- [ ] Tool `get_nutrition_tips()`
- [ ] Tool `analyze_patterns()`

**Week 3:**
- [ ] Polish & error handling
- [ ] Unit tests completi
- [ ] README accademico
- [ ] Demo video
- [ ] Presentation

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

**Status:** ✅ v0.1 - Hello World funzionante
**Next:** 🚧 Implementazione database e primo tool reale
