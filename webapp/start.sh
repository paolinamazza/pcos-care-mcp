#!/bin/bash

# PCOS Care WebApp Launcher
# Avvia sia backend (FastAPI) che frontend (Vite)

echo "=========================================="
echo "🚀 PCOS Care WebApp Launcher"
echo "=========================================="
echo ""

# Colori per output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Controlla se il backend è già in esecuzione
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠️  Backend già in esecuzione sulla porta 8000${NC}"
    BACKEND_RUNNING=1
else
    BACKEND_RUNNING=0
fi

# Funzione per pulire i processi al exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Chiusura servizi...${NC}"

    if [ $BACKEND_RUNNING -eq 0 ]; then
        # Kill backend se è stato avviato da questo script
        if [ ! -z "$BACKEND_PID" ]; then
            echo -e "${BLUE}   Fermando backend (PID: $BACKEND_PID)...${NC}"
            kill $BACKEND_PID 2>/dev/null
        fi
    fi

    echo -e "${GREEN}✅ Servizi chiusi${NC}"
    exit 0
}

trap cleanup EXIT INT TERM

# 1. Avvia Backend (se non già in esecuzione)
if [ $BACKEND_RUNNING -eq 0 ]; then
    echo -e "${BLUE}📦 Avvio backend FastAPI...${NC}"
    cd "$SCRIPT_DIR/api"

    # Controlla se uvicorn è installato
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ python3 non trovato!${NC}"
        exit 1
    fi

    # Avvia backend in background
    python3 main.py > "$SCRIPT_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!

    echo -e "${GREEN}   Backend avviato (PID: $BACKEND_PID)${NC}"
    echo -e "${BLUE}   Logs: $SCRIPT_DIR/backend.log${NC}"

    # Aspetta che il backend sia pronto
    echo -e "${YELLOW}   Attendo che il backend sia pronto...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Backend pronto!${NC}"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
else
    echo -e "${GREEN}✅ Backend già in esecuzione${NC}"
fi

# Controlla che il backend risponda
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend non risponde su http://localhost:8000${NC}"
    echo -e "${YELLOW}   Controlla i log in: $SCRIPT_DIR/backend.log${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Backend disponibile su: ${NC}http://localhost:8000"
echo -e "${BLUE}   API Docs: ${NC}http://localhost:8000/docs"
echo ""

# 2. Avvia Frontend
echo -e "${BLUE}⚛️  Avvio frontend React + Vite...${NC}"
cd "$SCRIPT_DIR/frontend"

# Controlla se node_modules esiste
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   node_modules non trovato, eseguo npm install...${NC}"
    npm install
fi

echo -e "${GREEN}   Frontend in avvio...${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 PCOS Care WebApp è pronto!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Backend API:${NC}  http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}     http://localhost:8000/docs"
echo -e "${BLUE}Frontend:${NC}     http://localhost:5173"
echo ""
echo -e "${YELLOW}Premi Ctrl+C per fermare tutti i servizi${NC}"
echo "=========================================="
echo ""

# Avvia frontend (in foreground)
npm run dev

# Quando npm run dev termina, cleanup verrà chiamato automaticamente
