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


# ============================================================================
# FASE 3: Cycle Tracking Models
# ============================================================================

class FlowIntensity(str, Enum):
    """Enum per intensità del flusso mestruale"""
    SPOTTING = "spotting"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    VERY_HEAVY = "very_heavy"


class CycleEntry(BaseModel):
    """
    Modello per un'entry del ciclo mestruale.

    Validazione:
    - start_date obbligatorio
    - end_date opzionale (può essere aggiornato dopo)
    - flow_intensity da enum
    - cycle_length calcolato automaticamente se end_date presente
    """

    start_date: datetime = Field(
        ...,
        description="Data di inizio del ciclo mestruale"
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Data di fine del ciclo (opzionale, può essere aggiornato)"
    )

    flow_intensity: FlowIntensity = Field(
        default=FlowIntensity.MEDIUM,
        description="Intensità del flusso mestruale"
    )

    notes: Optional[str] = Field(
        default="",
        max_length=500,
        description="Note aggiuntive sul ciclo"
    )

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Valida che end_date sia dopo start_date"""
        if v is not None and 'start_date' in info.data:
            if v < info.data['start_date']:
                raise ValueError("end_date deve essere dopo start_date")
        return v

    @property
    def cycle_length(self) -> Optional[int]:
        """Calcola lunghezza ciclo in giorni"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-10-01T00:00:00",
                "end_date": "2025-10-05T00:00:00",
                "flow_intensity": "medium",
                "notes": "Ciclo regolare"
            }
        }


class CycleResponse(BaseModel):
    """Risposta dopo aver salvato un ciclo"""

    success: bool
    message: str
    entry_id: Optional[int] = None
    cycle_length: Optional[int] = None
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Ciclo registrato con successo",
                "entry_id": 5,
                "cycle_length": 4,
                "timestamp": "2025-10-22T10:30:00"
            }
        }


class CycleSummary(BaseModel):
    """Riepilogo statistiche cicli mestruali"""

    total_cycles: int
    average_cycle_length: Optional[float] = None
    shortest_cycle: Optional[int] = None
    longest_cycle: Optional[int] = None
    regularity_score: Optional[float] = None  # 0-100, 100 = molto regolare
    predicted_next_start: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_cycles": 6,
                "average_cycle_length": 28.5,
                "shortest_cycle": 26,
                "longest_cycle": 31,
                "regularity_score": 75.0,
                "predicted_next_start": "2025-11-15T00:00:00"
            }
        }
