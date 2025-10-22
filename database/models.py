"""
Data Models per PCOS Care MCP Server
Using Pydantic for runtime validation and type safety
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class SymptomType(str, Enum):
    """Enum per i tipi di sintomi PCOS più comuni"""
    CRAMPI = "crampi"
    MAL_DI_TESTA = "mal_di_testa"
    ACNE = "acne"
    AUMENTO_PESO = "aumento_peso"
    PERDITA_CAPELLI = "perdita_capelli"
    IRSUTISMO = "irsutismo"
    IRREGOLARITA_CICLO = "irregolarita_ciclo"
    DOLORE_PELVICO = "dolore_pelvico"
    AFFATICAMENTO = "affaticamento"
    ANSIA = "ansia"
    DEPRESSIONE = "depressione"
    ALTRO = "altro"


class SymptomEntry(BaseModel):
    """
    Modello per un'entry di sintomo.
    
    Validazione automatica con Pydantic:
    - intensity deve essere 1-10
    - notes può essere vuoto ma max 500 caratteri
    - timestamp viene auto-generato se non fornito
    """
    
    symptom_type: SymptomType = Field(
        ...,
        description="Tipo di sintomo dalla lista predefinita"
    )
    
    intensity: int = Field(
        ...,
        ge=1,
        le=10,
        description="Intensità del sintomo da 1 (lieve) a 10 (severo)"
    )
    
    notes: Optional[str] = Field(
        default="",
        max_length=500,
        description="Note aggiuntive sul sintomo"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp dell'entry (auto-generato se non fornito)"
    )
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> str:
        """Sanitizza le note rimuovendo spazi superflui"""
        if v is None:
            return ""
        return v.strip()
    
    class Config:
        """Configurazione Pydantic"""
        json_schema_extra = {
            "example": {
                "symptom_type": "crampi",
                "intensity": 7,
                "notes": "Crampi forti durante il ciclo",
                "timestamp": "2025-10-22T10:30:00"
            }
        }


class SymptomResponse(BaseModel):
    """Risposta dopo aver salvato un sintomo"""
    
    success: bool
    message: str
    entry_id: Optional[int] = None
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Sintomo registrato con successo",
                "entry_id": 42,
                "timestamp": "2025-10-22T10:30:00"
            }
        }


class SymptomSummary(BaseModel):
    """Riepilogo statistiche sintomi"""
    
    total_entries: int
    most_common_symptom: Optional[str] = None
    average_intensity: Optional[float] = None
    date_range: tuple[datetime, datetime]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_entries": 15,
                "most_common_symptom": "crampi",
                "average_intensity": 6.5,
                "date_range": ["2025-10-01T00:00:00", "2025-10-22T23:59:59"]
            }
        }
