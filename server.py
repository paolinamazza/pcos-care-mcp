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
from database import DatabaseManager, SymptomType, FlowIntensity
from tools import SymptomTracker, CycleTracker, PatternAnalyzer

# Import RAG system (with fallback if dependencies not installed)
try:
    from rag import PCOSKnowledgeBase
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG dependencies not installed - get_medical_info tool will be disabled")

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
cycle_tracker = CycleTracker(db_manager)
pattern_analyzer = PatternAnalyzer(db_manager)

# Inizializza RAG system (se disponibile)
knowledge_base = None
if RAG_AVAILABLE:
    try:
        knowledge_base = PCOSKnowledgeBase()
        knowledge_base.build_index()  # Build/load FAISS index
        logger.info("RAG Knowledge Base initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        RAG_AVAILABLE = False

# Crea l'istanza del server MCP
app = Server("pcos-care-mcp")

logger.info("=" * 60)
logger.info("PCOS Care MCP Server v0.3 - FASE 3 - Starting...")
logger.info("Database: Initialized")
logger.info("Tools: Symptom Tracker ready")
logger.info("Tools: Cycle Tracker ready")
logger.info("Tools: Pattern Analyzer ready")
logger.info(f"Tools: RAG System {'ready' if RAG_AVAILABLE else 'unavailable (install dependencies)'}")
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
            name="track_cycle",
            description=(
                "Registra un ciclo mestruale nel database. "
                "Salva data inizio, fine (opzionale), intensità flusso e note. "
                "Calcola automaticamente la lunghezza del ciclo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Data di inizio ciclo (ISO format o 'today')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Data di fine ciclo (ISO format o 'today', opzionale)"
                    },
                    "flow_intensity": {
                        "type": "string",
                        "enum": [f.value for f in FlowIntensity],
                        "default": "medium",
                        "description": "Intensità del flusso mestruale"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Note aggiuntive opzionali (max 500 caratteri)",
                        "maxLength": 500
                    }
                },
                "required": ["start_date"]
            }
        ),
        Tool(
            name="update_cycle_end",
            description=(
                "Aggiorna la data di fine di un ciclo esistente. "
                "Utile quando registri l'inizio ma non sai ancora quando finirà."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "cycle_id": {
                        "type": "integer",
                        "description": "ID del ciclo da aggiornare"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Data di fine ciclo (ISO format o 'today')"
                    }
                },
                "required": ["cycle_id", "end_date"]
            }
        ),
        Tool(
            name="get_cycle_history",
            description=(
                "Recupera lo storico dei cicli mestruali registrati. "
                "Mostra date, lunghezza, intensità."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 6,
                        "description": "Numero di cicli da recuperare (default: 6)"
                    }
                }
            }
        ),
        Tool(
            name="get_cycle_analytics",
            description=(
                "Genera analytics avanzate sui cicli mestruali. "
                "Include: lunghezza media, regolarità, predizione prossimo ciclo, insights."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "months": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 6,
                        "description": "Numero di mesi da analizzare (default: 6)"
                    }
                }
            }
        ),
        Tool(
            name="analyze_symptom_cycle_correlation",
            description=(
                "Analizza le correlazioni tra sintomi e fasi del ciclo mestruale. "
                "Identifica pattern ricorrenti (es: crampi sempre durante mestruazione). "
                "Richiede dati di almeno 2-3 cicli per analisi significativa."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "months": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 12,
                        "default": 3,
                        "description": "Numero di mesi da analizzare (default: 3)"
                    }
                }
            }
        ),
        Tool(
            name="analyze_symptom_trends",
            description=(
                "Analizza i trend nel tempo per sintomi specifici. "
                "Identifica se i sintomi stanno migliorando, peggiorando o sono stabili."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "symptom_type": {
                        "type": "string",
                        "description": "Tipo di sintomo da analizzare (opzionale, altrimenti tutti)"
                    },
                    "days": {
                        "type": "integer",
                        "minimum": 30,
                        "maximum": 365,
                        "default": 90,
                        "description": "Giorni da analizzare (default: 90)"
                    }
                }
            }
        ),
        Tool(
            name="identify_patterns",
            description=(
                "Identifica pattern ricorrenti nei dati (sintomi che si ripetono, "
                "combinazioni di sintomi, correlazioni temporali)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "min_occurrences": {
                        "type": "integer",
                        "minimum": 2,
                        "maximum": 10,
                        "default": 2,
                        "description": "Numero minimo di occorrenze per considerare un pattern (default: 2)"
                    }
                }
            }
        ),
        Tool(
            name="get_medical_info",
            description=(
                "Sistema RAG per ottenere informazioni evidence-based su PCOS. "
                "Risponde a domande su sintomi, nutrizione, lifestyle, trattamenti, fertilità. "
                "Include citazioni delle fonti."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "La domanda sulla PCOS"
                    },
                    "num_sources": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 3,
                        "description": "Numero di fonti da considerare (default: 3)"
                    }
                },
                "required": ["question"]
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

        elif name == "track_cycle":
            # Estrai parametri
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            flow_intensity = arguments.get("flow_intensity", "medium")
            notes = arguments.get("notes", "")

            # Chiama business logic
            result = cycle_tracker.track_cycle(
                start_date=start_date,
                end_date=end_date,
                flow_intensity=flow_intensity,
                notes=notes
            )

            # Formatta risposta
            if result["success"]:
                cycle_info = f"- Lunghezza: {result['cycle_length']} giorni" if result.get('cycle_length') else "- Ciclo ancora in corso"

                response = f"""
✅ **Ciclo Registrato!**

**Dettagli:**
- Data inizio: {start_date}
{f"- Data fine: {end_date}" if end_date else "- Fine: Da aggiornare"}
{cycle_info}
- Intensità flusso: {flow_intensity}
- ID Entry: #{result['entry_id']}

{result.get('context', '')}

💡 Usa `get_cycle_history` per vedere lo storico o `get_cycle_analytics` per statistiche.
"""
            else:
                response = f"""
❌ **Errore nel Salvare il Ciclo**

{result['message']}

Riprova o controlla i parametri.
"""

            return [TextContent(type="text", text=response.strip())]

        elif name == "update_cycle_end":
            cycle_id = arguments.get("cycle_id")
            end_date = arguments.get("end_date")

            result = cycle_tracker.update_cycle_end(
                cycle_id=cycle_id,
                end_date=end_date
            )

            if result["success"]:
                response = f"""
✅ **Ciclo Aggiornato!**

**Dettagli:**
- ID Ciclo: #{result['entry_id']}
- Data fine aggiornata: {end_date}
- Lunghezza ciclo: {result['cycle_length']} giorni

💡 Usa `get_cycle_analytics` per vedere le statistiche aggiornate.
"""
            else:
                response = f"""
❌ **Errore nell'Aggiornare il Ciclo**

{result['message']}
"""

            return [TextContent(type="text", text=response.strip())]

        elif name == "get_cycle_history":
            limit = arguments.get("limit", 6)

            result = cycle_tracker.get_cycle_history(limit=limit)

            if result["success"] and result["count"] > 0:
                cycles = result["cycles"]

                response = f"📅 **Storico Ultimi {result['count']} Cicli**\n\n"

                for c in cycles:
                    cycle_len = f"{c['cycle_length']} giorni" if c['cycle_length'] else 'N/A'
                    response += f"""
**ID #{c['id']}**
- Inizio: {c['start_date'][:10]}
- Fine: {c['end_date'][:10] if c['end_date'] else 'In corso'}
- Lunghezza: {cycle_len}
- Intensità: {c['flow_intensity']}
- Note: {c['notes'] if c['notes'] else 'Nessuna nota'}
---
"""
            else:
                response = "📭 Nessun ciclo registrato ancora. Inizia con `track_cycle`!"

            return [TextContent(type="text", text=response.strip())]

        elif name == "get_cycle_analytics":
            months = arguments.get("months", 6)

            result = cycle_tracker.get_cycle_analytics(months=months)

            if result["success"]:
                response = f"""
📊 **Analytics Cicli - Ultimi {months} Mesi**

**Statistiche:**
- Totale cicli registrati: {result['total_cycles']}
- Lunghezza media: {result['average_cycle_length'] or 'N/A'} giorni
- Ciclo più breve: {result['shortest_cycle'] or 'N/A'} giorni
- Ciclo più lungo: {result['longest_cycle'] or 'N/A'} giorni
- Regolarità: {result['regularity_score'] or 'N/A'}/100

{f"🔮 **Prossimo ciclo previsto:** {result['predicted_next_start'][:10] if result['predicted_next_start'] else 'N/A'}" if result.get('predicted_next_start') else ""}

**Insights:**
"""
                for insight in result.get('insights', []):
                    response += f"\n{insight}"

                response += "\n\n💡 Continua a monitorare per predizioni più accurate!"
            else:
                response = f"❌ Errore nel generare analytics: {result.get('message', 'Unknown error')}"

            return [TextContent(type="text", text=response.strip())]

        elif name == "analyze_symptom_cycle_correlation":
            months = arguments.get("months", 3)

            result = pattern_analyzer.analyze_symptom_cycle_correlation(months=months)

            if result["success"]:
                response = f"""
📊 **Analisi Correlazione Sintomi-Ciclo - Ultimi {months} Mesi**

**Dati analizzati:**
- Sintomi: {result['total_symptoms_analyzed']}
- Cicli: {result['total_cycles_analyzed']}

**Insights:**
"""
                for insight in result.get('insights', []):
                    response += f"\n{insight}"

                response += "\n\n💡 Più dati raccogli, più accurate saranno le correlazioni identificate!"
            else:
                response = f"❌ {result.get('message', 'Errore nell analisi')}"

            return [TextContent(type="text", text=response.strip())]

        elif name == "analyze_symptom_trends":
            symptom_type = arguments.get("symptom_type")
            days = arguments.get("days", 90)

            result = pattern_analyzer.analyze_symptom_trends(
                symptom_type=symptom_type,
                days=days
            )

            if result["success"]:
                response = f"""
📈 **Analisi Trend Sintomi - Ultimi {days} Giorni**

**Sintomo:** {result['symptom_type']}
**Entries analizzate:** {result['total_entries']}

**Insights:**
"""
                for insight in result.get('insights', []):
                    response += f"\n{insight}"
            else:
                response = f"❌ {result.get('message', 'Errore nell analisi')}"

            return [TextContent(type="text", text=response.strip())]

        elif name == "identify_patterns":
            min_occurrences = arguments.get("min_occurrences", 2)

            result = pattern_analyzer.identify_recurring_patterns(
                min_occurrences=min_occurrences
            )

            if result["success"]:
                response = f"""
🔍 **Pattern Ricorrenti Identificati**

**Pattern trovati:** {result['patterns_found']}
**Occorrenze minime richieste:** {min_occurrences}

**Insights:**
"""
                for insight in result.get('insights', []):
                    response += f"\n{insight}"

                if result['patterns_found'] == 0:
                    response += "\n\n💡 Continua a tracciare sintomi e cicli per identificare pattern più chiari!"
            else:
                response = f"❌ {result.get('message', 'Errore nell identificazione pattern')}"

            return [TextContent(type="text", text=response.strip())]

        elif name == "get_medical_info":
            if not RAG_AVAILABLE or knowledge_base is None:
                response = """
❌ **RAG System Non Disponibile**

Il sistema RAG per Q&A mediche richiede dipendenze aggiuntive.
Installa con: `pip install sentence-transformers chromadb pypdf`

Poi riavvia il server.
"""
                return [TextContent(type="text", text=response.strip())]

            question = arguments.get("question")
            num_sources = arguments.get("num_sources", 3)

            try:
                # Try PDF-based RAG first (new system with real PDFs)
                result = knowledge_base.query_pdf_knowledge(
                    query=question,
                    top_k=num_sources,
                    include_sources=True
                )

                # Fallback to legacy FAISS system if PDF RAG fails
                if not result["success"] and result.get("fallback_available"):
                    logger.info("PDF RAG failed, falling back to legacy system")
                    result = knowledge_base.get_answer(
                        query=question,
                        top_k=num_sources,
                        include_sources=True
                    )
                    result["system"] = "legacy_faiss"

                if result["success"]:
                    # Check which system was used
                    system_name = "PDF RAG (28 research papers)" if result.get("system") == "pdf_rag" else "Legacy Knowledge Base"

                    response = f"""
🧠 **Informazioni PCOS - Evidence-Based**
📚 Sistema: {system_name}

**Domanda:** {question}

**Risposta:**
{result.get('context') or result.get('answer', 'N/A')}

**Fonti consultate:**
"""
                    for i, source in enumerate(result.get('sources', []), 1):
                        response += f"\n{i}. **{source['title']}** (Categoria: {source['category']})"

                        # Show different metadata based on system
                        if result.get("system") == "pdf_rag":
                            response += f"\n   Pagina: ~{source.get('page', 'N/A')}"
                            response += f"\n   Rilevanza: {source['relevance_score']:.0%}"
                            if 'chunk_preview' in source:
                                response += f"\n   Preview: {source['chunk_preview'][:100]}..."
                        else:
                            response += f"\n   Fonte: {source.get('source', 'N/A')}"
                            response += f"\n   Rilevanza: {source.get('relevance_score', 0):.0%}"

                    # Confidence warning
                    confidence = result.get('confidence', 0)
                    if confidence < 0.5:
                        response += "\n\n⚠️ Nota: La risposta potrebbe non essere perfettamente rilevante. Prova a riformulare la domanda."

                    # Category info if using PDF RAG
                    if result.get("system") == "pdf_rag":
                        response += f"\n\n📊 Chunk trovati: {result.get('total_chunks_found', 0)}"
                        if result.get('category_filter'):
                            response += f" (filtrati per categoria: {result['category_filter']})"

                    response += "\n\n💡 Questa è un'informazione generale. Per diagnosi e trattamenti, consulta sempre un medico."

                else:
                    response = f"""
❌ **Nessuna Informazione Trovata**

Non ho trovato informazioni rilevanti per: "{question}"

{result.get('message', '')}

💡 Prova a:
- Riformulare la domanda in modo più specifico
- Chiedere su: sintomi, nutrizione, lifestyle, trattamenti, fertilità
- Esempi: "Quali sono i criteri Rotterdam?", "Dieta per PCOS?", "Esercizio fisico e PCOS?"
"""

                return [TextContent(type="text", text=response.strip())]

            except Exception as e:
                logger.error(f"Error in RAG system: {e}", exc_info=True)
                response = f"""
❌ **Errore nel Sistema RAG**

Si è verificato un errore nel processare la domanda.
Errore: {str(e)}

Riprova o contatta il supporto.
"""
                return [TextContent(type="text", text=response.strip())]

        elif name == "hello_pcos":
            # Manteniamo il tool di test per backward compatibility
            user_name = arguments.get("name", "Unknown")
            
            response = f"""
👋 Ciao {user_name}!

**PCOS Care MCP Server v0.3 - FASE 3** 🎉

✨ **Nuove Features FASE 3:**
✅ Cycle Tracking completo
✅ Predizione prossimo ciclo
✅ Analytics avanzate (regolarità, trend)
✅ Pattern Analysis (correlazioni sintomi-ciclo)
✅ RAG System (Q&A evidence-based)

📚 **Tools Disponibili:**

**Symptom Tracking:**
1. `track_symptom` - Registra sintomo PCOS
2. `get_recent_symptoms` - Vedi storico sintomi
3. `get_symptom_summary` - Statistiche sintomi

**Cycle Tracking:**
4. `track_cycle` - Registra ciclo mestruale
5. `update_cycle_end` - Aggiorna fine ciclo
6. `get_cycle_history` - Storico cicli
7. `get_cycle_analytics` - Analytics e predizioni

**Pattern Analysis:**
8. `analyze_symptom_cycle_correlation` - Correlazioni sintomi-ciclo
9. `analyze_symptom_trends` - Trend sintomi nel tempo
10. `identify_patterns` - Pattern ricorrenti

**Medical Info (RAG):**
11. `get_medical_info` - Q&A evidence-based su PCOS

**Prova a dire:**
- "Registra crampi intensità 7"
- "Traccia il mio ciclo iniziato oggi"
- "Analizza le correlazioni tra sintomi e ciclo"
- "Quali sono i sintomi della PCOS?"
- "Mostrami i pattern nei miei dati"
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
