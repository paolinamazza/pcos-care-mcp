# PCOS Care Web Application

Applicazione web standalone per monitoraggio PCOS con sistema RAG evidence-based.

## Architettura

```
webapp/
├── api/                    # FastAPI Backend
│   └── main.py            # REST API endpoints
└── frontend/              # React Frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── pages/         # Page components
    │   ├── services/      # API services
    │   └── main.jsx       # Entry point
    └── vite.config.js     # Vite configuration
```

## Features

- **Dashboard**: Panoramica completa del sistema e statistiche
- **Tracciamento Sintomi**: Registra e monitora sintomi PCOS con intensità
- **Tracciamento Cicli**: Monitora cicli mestruali con analytics
- **Analytics**: Correlazioni, trend e pattern ricorrenti
- **Knowledge Base**: Query RAG su 28 PDF di ricerca scientifica

## Setup

### 1. Backend (FastAPI)

```bash
# Dalla root del progetto
cd webapp/api

# Il backend usa le stesse dipendenze del progetto principale
# Assicurati che siano installate:
pip install -r ../../requirements.txt

# Avvia il backend
python main.py

# Il server sarà disponibile su:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### 2. Frontend (React + Vite)

```bash
# Dalla webapp/frontend
cd webapp/frontend

# Installa dipendenze (già fatto se hai seguito il setup)
npm install

# Avvia il dev server
npm run dev

# La webapp sarà disponibile su:
# http://localhost:5173
```

## Avvio Rapido

Usa lo script di avvio per lanciare sia backend che frontend:

```bash
# Dalla root del progetto
./webapp/start.sh
```

Questo script:
1. Avvia il backend FastAPI in background
2. Avvia il frontend Vite
3. Apre automaticamente il browser

Per fermare entrambi i servizi: `Ctrl+C` (ferma il frontend, il backend continuerà)

Per fermare il backend:
```bash
# Trova il processo
ps aux | grep "python.*webapp/api/main.py"

# Kill il processo
kill <PID>
```

## API Endpoints

### Health
- `GET /` - Health check
- `GET /health` - Detailed health check

### Symptoms
- `POST /api/symptoms` - Crea nuovo sintomo
- `GET /api/symptoms?limit=10` - Ottieni ultimi sintomi
- `GET /api/symptoms/summary?days=30` - Statistiche sintomi

### Cycles
- `POST /api/cycles` - Crea nuovo ciclo
- `PATCH /api/cycles/{id}` - Aggiorna ciclo
- `GET /api/cycles?limit=6` - Ottieni cicli
- `GET /api/cycles/analytics?months=6` - Analytics cicli

### Analytics
- `GET /api/analytics/correlation?months=3` - Correlazione sintomi-ciclo
- `GET /api/analytics/trends?days=90` - Trend sintomi
- `GET /api/analytics/patterns?min_occurrences=2` - Pattern ricorrenti

### Knowledge Base
- `POST /api/knowledge/query` - Query RAG system
  ```json
  {
    "question": "What are the Rotterdam criteria?",
    "num_sources": 5,
    "category_filter": "guidelines"  // optional
  }
  ```
- `GET /api/knowledge/stats` - Statistiche knowledge base

## Tecnologie Utilizzate

### Backend
- **FastAPI**: Web framework moderno e veloce
- **SQLAlchemy**: ORM per database
- **Pydantic**: Validazione dati
- **ChromaDB**: Vector database per RAG
- **sentence-transformers**: Embeddings semantici

### Frontend
- **React 18**: UI library
- **Vite**: Build tool veloce
- **React Router**: Routing
- **Axios**: HTTP client
- **Recharts**: Data visualization
- **date-fns**: Date utilities

## Struttura Pagine

### Dashboard
- Stato sistema (database, RAG)
- Sintomi ultimi 30 giorni
- Ultimi cicli
- Knowledge base stats
- Azioni rapide

### Sintomi
- Form registrazione sintomo
- Slider intensità 1-10
- Storico sintomi registrati

### Cicli
- Form registrazione ciclo
- Analytics (durata media, regolarità)
- Storico cicli

### Analytics
- Correlazione sintomi-ciclo
- Trend sintomi nel tempo
- Pattern ricorrenti

### Knowledge Base
- Query form con filtri categoria
- Selezione numero fonti (3-10)
- Domande suggerite
- Risultati con:
  - Context estratto
  - Fonti con rilevanza
  - Numero pagina
  - Preview chunk
  - Confidence score

## Condivisione Backend

La webapp utilizza gli stessi moduli del MCP server:
- `database/`: Database manager e modelli SQLAlchemy
- `tools/`: SymptomTracker, CycleTracker, PatternAnalyzer
- `rag/`: Sistema RAG completo (PDF processor, vector store, embeddings)

Questo garantisce:
- ✅ Stesso database per MCP e webapp
- ✅ Stessa logica di business
- ✅ Stesso knowledge base RAG
- ✅ Zero duplicazione codice

## Sviluppo

### Hot Reload
- Frontend: Vite con HMR automatico
- Backend: Uvicorn con `reload=True`

### CORS
Il backend è configurato per accettare richieste da:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (alternative React dev server)

Per produzione, modifica `webapp/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

### Proxy API
Il frontend è configurato per proxy le richieste `/api` al backend:
```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

## Build Produzione

### Frontend
```bash
cd webapp/frontend
npm run build

# Output in webapp/frontend/dist/
```

### Deployment
Per deployare in produzione:

1. Build del frontend
2. Servi i file statici con un web server (nginx, apache)
3. Configura il backend FastAPI con WSGI (gunicorn)
4. Setup HTTPS con reverse proxy

Esempio nginx:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /path/to/webapp/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Backend non si avvia
- Verifica che le dipendenze siano installate: `pip install -r requirements.txt`
- Controlla che la porta 8000 sia libera: `lsof -i :8000`
- Verifica i log: il backend stampa errori di inizializzazione

### Frontend non si connette al backend
- Verifica che il backend sia in esecuzione: `curl http://localhost:8000/health`
- Controlla la console del browser per errori CORS
- Verifica il proxy in `vite.config.js`

### RAG system non disponibile
- Verifica che ChromaDB sia popolato: `python -c "from rag.vector_store import VectorStore; print(VectorStore().get_statistics())"`
- Se vuoto, esegui: `python scripts/setup_rag.py`
- Controlla i log del backend per errori di inizializzazione RAG

### Database vuoto
- Il database viene creato automaticamente in `data/pcos_care.db`
- Inizia a registrare sintomi/cicli per popolare il database
- Per reset: elimina `data/pcos_care.db` e riavvia il backend

## Differenze MCP vs WebApp

### MCP Server
- **Uso**: Integrazione con Claude Desktop
- **Interfaccia**: MCP Tools Protocol
- **Accesso**: Solo tramite Claude
- **Output**: Text-based responses

### WebApp
- **Uso**: Standalone, accessibile da browser
- **Interfaccia**: REST API + React UI
- **Accesso**: Diretto via browser
- **Output**: UI interattiva con grafici e visualizzazioni

**Stesso backend, due interfacce diverse!**

## Next Steps

- [ ] Aggiungere grafici per visualizzazione trend (con recharts)
- [ ] Implementare calendar view per cicli
- [ ] Aggiungere export dati (PDF/CSV)
- [ ] Implementare authentication (opzionale)
- [ ] Dark mode toggle
- [ ] PWA support per uso mobile
- [ ] Notifiche per reminder cicli

## Support

Per problemi o domande:
1. Controlla i logs del backend
2. Apri console browser (F12) per errori frontend
3. Verifica che entrambi i servizi siano in esecuzione
4. Controlla la documentazione API: http://localhost:8000/docs
