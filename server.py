#!/usr/bin/env python3
"""
PCOS Care MCP Server - v0.2 (Production Ready)
Un server MCP per tracking e supporto PCOS con database e tools reali

Architecture:
- MCP Server (questo file): Entry point e routing
- Database Layer: SQLite + SQLAlchemy ORM
- Business Logic: Tools separati per ogni funzionalità
- Validation: Pydantic models per type safety
"""

import asyncio
import logging
import json
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import business logic
from database import DatabaseManager, SymptomType
from tools import SymptomTracker

# Setup logging professionale
def setup_logging():
    """Configura logging con file e console"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger("pcos-care-mcp")

# Inizializza database e tools
db_manager = DatabaseManager()
symptom_tracker = SymptomTracker(db_manager)

# Crea l'istanza del server MCP
app = Server("pcos-care-mcp")

logger.info("=" * 60)
logger.info("PCOS Care MCP Server v0.2 - Starting...")
logger.info("Database: Initialized")
logger.info("Tools: Symptom Tracker ready")
logger.info("=" * 60)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Lista dei tools disponibili nel server MCP.
    Best practice: Schema JSON ben definito per ogni tool
    """
    return [
        Tool(
            name="track_symptom",
            description=(
                "Registra un sintomo PCOS nel database. "
                "Salva tipo di sintomo, intensità (1-10) e note opzionali. "
                "Fornisce feedback contestuale e suggerimenti."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symptom_type": {
                        "type": "string",
                        "enum": [s.value for s in SymptomType],
                        "description": "Tipo di sintomo dalla lista predefinita"
                    },
                    "intensity": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Intensità del sintomo da 1 (lieve) a 10 (severo)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Note aggiuntive opzionali (max 500 caratteri)",
                        "maxLength": 500
                    }
                },
                "required": ["symptom_type", "intensity"]
            }
        ),
        Tool(
            name="get_recent_symptoms",
            description=(
                "Recupera gli ultimi sintomi registrati. "
                "Utile per vedere lo storico recente."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 50,
                        "default": 5,
                        "description": "Numero di sintomi da recuperare (default: 5)"
                    }
                }
            }
        ),
        Tool(
            name="get_symptom_summary",
            description=(
                "Genera un riepilogo statistico dei sintomi. "
                "Include: totale entries, sintomo più comune, intensità media, insights."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 365,
                        "default": 30,
                        "description": "Numero di giorni da analizzare (default: 30)"
                    }
                }
            }
        ),
        Tool(
            name="hello_pcos",
            description="Tool di test per verificare la connessione (deprecato - usa i tool reali)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Il nome dell'utente"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Gestisce le chiamate ai tools.
    
    Best practices:
    - Logging dettagliato per debugging
    - Error handling robusto
    - Risposte user-friendly
    - Validazione input
    """
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        if name == "track_symptom":
            # Estrai parametri
            symptom_type = arguments.get("symptom_type")
            intensity = arguments.get("intensity")
            notes = arguments.get("notes", "")
            
            # Chiama business logic
            result = symptom_tracker.track_symptom(
                symptom_type=symptom_type,
                intensity=intensity,
                notes=notes
            )
            
            # Formatta risposta
            if result["success"]:
                response = f"""
✅ **Sintomo Registrato!**

**Dettagli:**
- Tipo: {symptom_type}
- Intensità: {intensity}/10
- Data/Ora: {result['timestamp']}
- ID Entry: #{result['entry_id']}

{result.get('context', '')}

💡 Usa `get_recent_symptoms` per vedere lo storico o `get_symptom_summary` per analytics.
"""
            else:
                response = f"""
❌ **Errore nel Salvare il Sintomo**

{result['message']}

Riprova o controlla i parametri.
"""
            
            return [TextContent(type="text", text=response.strip())]
        
        elif name == "get_recent_symptoms":
            limit = arguments.get("limit", 5)
            
            result = symptom_tracker.get_recent_symptoms(limit=limit)
            
            if result["success"] and result["count"] > 0:
                symptoms = result["symptoms"]
                
                response = f"📊 **Ultimi {result['count']} Sintomi Registrati**\n\n"
                
                for s in symptoms:
                    response += f"""
**ID #{s['id']}** - {s['timestamp'][:10]}
- Tipo: {s['symptom_type']}
- Intensità: {s['intensity']}/10
- Note: {s['notes'] if s['notes'] else 'Nessuna nota'}
---
"""
            else:
                response = "📭 Nessun sintomo registrato ancora. Inizia con `track_symptom`!"
            
            return [TextContent(type="text", text=response.strip())]
        
        elif name == "get_symptom_summary":
            days = arguments.get("days", 30)
            
            result = symptom_tracker.get_summary(days=days)
            
            if result["success"]:
                response = f"""
📈 **Riepilogo Sintomi - Ultimi {days} Giorni**

**Statistiche:**
- Totale sintomi registrati: {result['total_entries']}
- Sintomo più frequente: {result['most_common_symptom'] or 'N/A'}
- Intensità media: {result['average_intensity'] or 'N/A'}/10

**Insights:**
"""
                for insight in result.get('insights', []):
                    response += f"\n{insight}"
                
                response += "\n\n💡 Continua a monitorare regolarmente per identificare pattern!"
            else:
                response = f"❌ Errore nel generare il riepilogo: {result.get('message', 'Unknown error')}"
            
            return [TextContent(type="text", text=response.strip())]
        
        elif name == "hello_pcos":
            # Manteniamo il tool di test per backward compatibility
            user_name = arguments.get("name", "Unknown")
            
            response = f"""
👋 Ciao {user_name}! 

**PCOS Care MCP Server v0.2** - Ora con Database Reale!

🎉 Novità:
✅ Database SQLite funzionante
✅ Tool `track_symptom` - Registra sintomi PCOS
✅ Tool `get_recent_symptoms` - Vedi storico
✅ Tool `get_symptom_summary` - Analytics e insights

📚 **Tools Disponibili:**
1. `track_symptom` - Registra un nuovo sintomo
2. `get_recent_symptoms` - Vedi ultimi sintomi
3. `get_symptom_summary` - Statistiche e insights

**Prova a dire:** "Registra crampi intensità 7"
"""
            
            return [TextContent(type="text", text=response.strip())]
        
        else:
            raise ValueError(f"Tool sconosciuto: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool '{name}': {str(e)}", exc_info=True)
        error_response = f"""
❌ **Errore Imprevisto**

Tool: {name}
Errore: {str(e)}

Controlla i log per dettagli o contatta il supporto.
"""
        return [TextContent(type="text", text=error_response.strip())]

async def main():
    """
    Entry point principale del server MCP.
    Usa stdio per comunicare con Claude Desktop.
    """
    logger.info("🚀 Avvio PCOS Care MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("✅ Server in ascolto su stdio")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
