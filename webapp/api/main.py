"""
PCOS Care Web API - FastAPI Backend

REST API per webapp che condivide lo stesso backend del MCP server.
Usa gli stessi database/ e rag/ modules.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import sys
from pathlib import Path
from datetime import timedelta

# Add parent directory to path per importare moduli esistenti
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database import DatabaseManager
from database.auth import User
from tools import SymptomTracker, CycleTracker, PatternAnalyzer
from rag import PCOSKnowledgeBase

# Import auth utilities
from auth import (
    authenticate_user,
    create_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    update_last_login,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Import chatbot
from chatbot import generate_chatbot_response

# Initialize FastAPI app
app = FastAPI(
    title="PCOS Care API",
    description="REST API per tracking sintomi, cicli e Q&A PCOS",
    version="2.0.0"
)

# CORS - permetti richieste dal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://paolinamazza.github.io",  # GitHub Pages
        "https://*.github.io"  # Any GitHub Pages subdomain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared components (stessi del MCP server)
db_manager = DatabaseManager()
symptom_tracker = SymptomTracker(db_manager)
cycle_tracker = CycleTracker(db_manager)
pattern_analyzer = PatternAnalyzer(db_manager)

# Initialize RAG (con try/except per fallback)
# Disable RAG on Render free tier to save memory
import os
ENABLE_RAG = os.getenv("ENABLE_RAG", "false").lower() == "true"

if ENABLE_RAG:
    try:
        knowledge_base = PCOSKnowledgeBase(use_pdf_rag=True)
        RAG_AVAILABLE = True
    except Exception as e:
        knowledge_base = None
        RAG_AVAILABLE = False
        print(f"Warning: RAG system not available: {e}")
else:
    knowledge_base = None
    RAG_AVAILABLE = False
    print("RAG system disabled (set ENABLE_RAG=true to enable)")


# ============================================================================
# Pydantic Models per Request/Response
# ============================================================================

class SymptomCreate(BaseModel):
    symptom_type: str
    intensity: int
    notes: Optional[str] = ""

class CycleCreate(BaseModel):
    start_date: str
    end_date: Optional[str] = None
    flow_intensity: str = "medium"
    notes: Optional[str] = ""

class CycleUpdate(BaseModel):
    end_date: str

class KnowledgeQuery(BaseModel):
    question: str
    num_sources: int = 3
    category_filter: Optional[str] = None

# Authentication Models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    has_anthropic_key: bool
    has_openai_key: bool

class UserAPIKeysUpdate(BaseModel):
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

# Chatbot Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []
    use_rag: bool = True
    category_filter: Optional[str] = None


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "PCOS Care API",
        "version": "2.0.0",
        "rag_available": RAG_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Check database
    db_healthy = True
    try:
        db_manager.get_session()
    except Exception:
        db_healthy = False

    # Check RAG
    rag_stats = None
    if RAG_AVAILABLE and knowledge_base:
        try:
            rag_stats = knowledge_base.get_stats()
        except Exception:
            pass

    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "error",
        "rag": {
            "available": RAG_AVAILABLE,
            "stats": rag_stats
        }
    }


# ============================================================================
# Symptom Routes
# ============================================================================

@app.post("/api/symptoms")
async def create_symptom(symptom: SymptomCreate):
    """Registra un nuovo sintomo"""
    result = symptom_tracker.track_symptom(
        symptom_type=symptom.symptom_type,
        intensity=symptom.intensity,
        notes=symptom.notes
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@app.get("/api/symptoms")
async def get_symptoms(limit: int = 10):
    """Recupera ultimi sintomi"""
    result = symptom_tracker.get_recent_symptoms(limit=limit)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.get("/api/symptoms/summary")
async def get_symptom_summary(days: int = 30):
    """Statistiche sintomi"""
    result = symptom_tracker.get_summary(days=days)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


# ============================================================================
# Cycle Routes
# ============================================================================

@app.post("/api/cycles")
async def create_cycle(cycle: CycleCreate):
    """Registra un nuovo ciclo"""
    result = cycle_tracker.track_cycle(
        start_date=cycle.start_date,
        end_date=cycle.end_date,
        flow_intensity=cycle.flow_intensity,
        notes=cycle.notes
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result

@app.patch("/api/cycles/{cycle_id}")
async def update_cycle(cycle_id: int, cycle: CycleUpdate):
    """Aggiorna data fine ciclo"""
    result = cycle_tracker.update_cycle_end(
        cycle_id=cycle_id,
        end_date=cycle.end_date
    )

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return result

@app.get("/api/cycles")
async def get_cycles(limit: int = 6):
    """Recupera storico cicli"""
    result = cycle_tracker.get_cycle_history(limit=limit)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.get("/api/cycles/analytics")
async def get_cycle_analytics(months: int = 6):
    """Analytics cicli mestruali"""
    result = cycle_tracker.get_cycle_analytics(months=months)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


# ============================================================================
# Analytics Routes
# ============================================================================

@app.get("/api/analytics/correlation")
async def analyze_correlation(months: int = 3):
    """Correlazione sintomi-ciclo"""
    result = pattern_analyzer.analyze_symptom_cycle_correlation(months=months)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.get("/api/analytics/trends")
async def analyze_trends(symptom_type: Optional[str] = None, days: int = 90):
    """Trend sintomi nel tempo"""
    result = pattern_analyzer.analyze_symptom_trends(
        symptom_type=symptom_type,
        days=days
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.get("/api/analytics/patterns")
async def identify_patterns(min_occurrences: int = 2):
    """Pattern ricorrenti"""
    result = pattern_analyzer.identify_recurring_patterns(
        min_occurrences=min_occurrences
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result


# ============================================================================
# Knowledge Base Routes (RAG)
# ============================================================================

@app.post("/api/knowledge/query")
async def query_knowledge(query: KnowledgeQuery):
    """Query sistema RAG per informazioni PCOS"""
    if not RAG_AVAILABLE or knowledge_base is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available. Run: python3 scripts/setup_rag.py"
        )

    try:
        # Try PDF RAG first
        result = knowledge_base.query_pdf_knowledge(
            query=query.question,
            top_k=query.num_sources,
            category_filter=query.category_filter,
            include_sources=True
        )

        # Fallback to legacy if needed
        if not result["success"] and result.get("fallback_available"):
            result = knowledge_base.get_answer(
                query=query.question,
                top_k=query.num_sources,
                include_sources=True
            )
            result["system"] = "legacy_faiss"

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("message", "No information found"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")

@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Statistiche knowledge base"""
    if not RAG_AVAILABLE or knowledge_base is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available"
        )

    try:
        stats = knowledge_base.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Authentication Routes
# ============================================================================

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        # Create user
        user = create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with username/email and password"""
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    update_last_login(user.id)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "has_anthropic_key": bool(current_user.anthropic_api_key),
        "has_openai_key": bool(current_user.openai_api_key)
    }


@app.put("/api/auth/api-keys")
async def update_api_keys(
    keys_data: UserAPIKeysUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user's API keys for AI services"""
    session = db_manager.get_session()

    try:
        user = session.query(User).filter(User.id == current_user.id).first()

        if keys_data.anthropic_api_key is not None:
            user.anthropic_api_key = keys_data.anthropic_api_key

        if keys_data.openai_api_key is not None:
            user.openai_api_key = keys_data.openai_api_key

        session.commit()

        return {
            "success": True,
            "message": "API keys updated successfully",
            "has_anthropic_key": bool(user.anthropic_api_key),
            "has_openai_key": bool(user.openai_api_key)
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")
    finally:
        session.close()


# ============================================================================
# AI Chatbot Routes
# ============================================================================

@app.post("/api/chat")
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    AI Chatbot conversazionale con integrazione RAG.
    Usa le API keys dell'utente per chiamare Claude o GPT.
    """
    # Get RAG context if requested
    rag_context = None

    if chat_request.use_rag and RAG_AVAILABLE and knowledge_base:
        try:
            # Query RAG system
            rag_result = knowledge_base.query_pdf_knowledge(
                query=chat_request.message,
                top_k=5,
                category_filter=chat_request.category_filter,
                include_sources=True
            )

            if rag_result.get("success") and rag_result.get("context"):
                rag_context = rag_result["context"]

                # Add sources to context for better responses
                if rag_result.get("sources"):
                    sources_text = "\n\nFonti:"
                    for i, source in enumerate(rag_result["sources"][:3], 1):
                        sources_text += f"\n{i}. {source['title']} (categoria: {source['category']})"
                    rag_context += sources_text

        except Exception as e:
            print(f"RAG query failed: {e}")
            # Continue without RAG context

    # Prepare user API keys
    user_api_keys = {
        "anthropic": current_user.anthropic_api_key,
        "openai": current_user.openai_api_key
    }

    # Generate chatbot response
    result = generate_chatbot_response(
        message=chat_request.message,
        conversation_history=[msg.dict() for msg in chat_request.conversation_history],
        user_api_keys=user_api_keys,
        rag_context=rag_context,
        preferred_provider="anthropic"  # Default to Claude
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Chatbot error"))

    # Return response with RAG info
    return {
        "success": True,
        "message": result["message"],
        "model": result.get("model"),
        "provider": result.get("provider"),
        "used_rag": bool(rag_context),
        "rag_context_length": len(rag_context) if rag_context else 0
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("PCOS Care Web API Starting...")
    print("=" * 60)
    print(f"Database: {'Connected' if db_manager else 'Error'}")
    print(f"RAG System: {'Available' if RAG_AVAILABLE else 'Unavailable'}")
    print("=" * 60)
    print("\nServer running at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
