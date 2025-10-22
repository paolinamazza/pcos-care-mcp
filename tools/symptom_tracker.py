"""
Symptom Tracker Tool
Implementa la logica business per il tracking dei sintomi PCOS
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from database import DatabaseManager, SymptomEntry, SymptomType
from pydantic import ValidationError

logger = logging.getLogger("pcos-care-mcp.tools")


class SymptomTracker:
    """
    Tool per tracking sintomi PCOS.
    
    Responsabilità:
    - Validazione input utente
    - Interazione con database
    - Generazione risposte user-friendly
    - Analytics di base
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza symptom tracker.
        
        Args:
            db_manager: Istanza di DatabaseManager
        """
        self.db = db_manager
        logger.info("SymptomTracker initialized")
    
    def track_symptom(
        self,
        symptom_type: str,
        intensity: int,
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Registra un nuovo sintomo.
        
        Args:
            symptom_type: Tipo di sintomo (da enum SymptomType)
            intensity: Intensità 1-10
            notes: Note opzionali
            
        Returns:
            Dizionario con risultato operazione e messaggio user-friendly
        """
        try:
            # Validazione con Pydantic
            symptom_entry = SymptomEntry(
                symptom_type=SymptomType(symptom_type.lower()),
                intensity=intensity,
                notes=notes
            )
            
            # Salva nel database
            response = self.db.add_symptom(symptom_entry)
            
            if response.success:
                # Genera messaggio contextual
                context_msg = self._generate_context_message(symptom_type, intensity)
                
                return {
                    "success": True,
                    "message": response.message,
                    "entry_id": response.entry_id,
                    "timestamp": response.timestamp.isoformat(),
                    "context": context_msg
                }
            else:
                return {
                    "success": False,
                    "message": response.message,
                    "error": "Database operation failed"
                }
                
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return {
                "success": False,
                "message": "Dati non validi. Controlla il tipo di sintomo e l'intensità (1-10).",
                "error": str(e)
            }
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            
            # Suggerisci sintomi validi
            valid_symptoms = [s.value for s in SymptomType]
            
            return {
                "success": False,
                "message": f"Tipo di sintomo non valido: '{symptom_type}'. "
                          f"Sintomi validi: {', '.join(valid_symptoms)}",
                "error": str(e)
            }
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "message": "Errore inaspettato. Riprova più tardi.",
                "error": str(e)
            }
    
    def get_recent_symptoms(self, limit: int = 5) -> Dict[str, Any]:
        """
        Recupera sintomi recenti.
        
        Args:
            limit: Numero massimo di sintomi da recuperare
            
        Returns:
            Dizionario con lista sintomi
        """
        try:
            symptoms = self.db.get_symptoms(limit=limit)
            
            return {
                "success": True,
                "count": len(symptoms),
                "symptoms": symptoms
            }
            
        except Exception as e:
            logger.error(f"Error retrieving symptoms: {e}")
            return {
                "success": False,
                "message": "Errore nel recuperare i sintomi",
                "error": str(e)
            }
    
    def get_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Genera riepilogo sintomi.
        
        Args:
            days: Giorni da analizzare
            
        Returns:
            Dizionario con statistiche
        """
        try:
            summary = self.db.get_symptom_summary(days=days)
            
            # Genera insights
            insights = self._generate_insights(summary)
            
            return {
                "success": True,
                "period_days": days,
                "total_entries": summary.total_entries,
                "most_common_symptom": summary.most_common_symptom,
                "average_intensity": summary.average_intensity,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "success": False,
                "message": "Errore nel generare il riepilogo",
                "error": str(e)
            }
    
    def _generate_context_message(self, symptom_type: str, intensity: int) -> str:
        """
        Genera messaggio contestuale basato sul sintomo.
        
        Args:
            symptom_type: Tipo di sintomo
            intensity: Intensità
            
        Returns:
            Messaggio con suggerimenti
        """
        # High intensity warnings
        if intensity >= 8:
            return (
                f"⚠️ Intensità alta ({intensity}/10) per {symptom_type}. "
                "Se il sintomo persiste o peggiora, consulta un medico."
            )
        
        # Symptom-specific tips
        tips = {
            "crampi": "Considera di applicare calore sulla zona e fare stretching leggero.",
            "mal_di_testa": "Assicurati di essere ben idratata e di riposare a sufficienza.",
            "affaticamento": "Monitora il tuo sonno e considera integratori di vitamina D (consulta il medico).",
            "ansia": "Prova tecniche di respirazione o meditazione. Considera di parlarne con un terapeuta."
        }
        
        tip = tips.get(symptom_type, "Continua a monitorare i tuoi sintomi.")
        
        return f"💡 Suggerimento: {tip}"
    
    def _generate_insights(self, summary) -> List[str]:
        """
        Genera insights basati sul riepilogo.
        
        Args:
            summary: SymptomSummary object
            
        Returns:
            Lista di insights
        """
        insights = []
        
        if summary.total_entries == 0:
            insights.append("📊 Nessun sintomo registrato nel periodo analizzato.")
            return insights
        
        # Frequency insight
        if summary.total_entries > 20:
            insights.append(
                f"📈 Hai registrato {summary.total_entries} sintomi negli ultimi 30 giorni. "
                "Considera di discutere la frequenza con il tuo medico."
            )
        elif summary.total_entries > 10:
            insights.append(f"📊 Stai monitorando regolarmente ({summary.total_entries} entries). Ottimo!")
        
        # Most common symptom
        if summary.most_common_symptom:
            insights.append(
                f"🔍 Il sintomo più frequente è '{summary.most_common_symptom}'. "
                "Cerca pattern correlati (ciclo, dieta, stress)."
            )
        
        # Average intensity
        if summary.average_intensity:
            if summary.average_intensity >= 7:
                insights.append(
                    f"⚠️ Intensità media alta ({summary.average_intensity:.1f}/10). "
                    "Valuta strategie di gestione con il tuo medico."
                )
            elif summary.average_intensity <= 3:
                insights.append(
                    f"✅ Intensità media bassa ({summary.average_intensity:.1f}/10). "
                    "I tuoi sintomi sembrano ben gestiti!"
                )
        
        return insights
