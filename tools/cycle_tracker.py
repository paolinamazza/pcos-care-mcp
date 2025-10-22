"""
Cycle Tracker Tool - FASE 3
Implementa la logica business per il tracking del ciclo mestruale
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from database import DatabaseManager, CycleEntry, FlowIntensity
from pydantic import ValidationError

logger = logging.getLogger("pcos-care-mcp.tools")


class CycleTracker:
    """
    Tool per tracking del ciclo mestruale.

    Responsabilità:
    - Registrare inizio/fine ciclo
    - Calcolare lunghezza e regolarità
    - Predire prossimo ciclo
    - Generare insights personalizzati
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza cycle tracker.

        Args:
            db_manager: Istanza di DatabaseManager
        """
        self.db = db_manager
        logger.info("CycleTracker initialized")

    def track_cycle(
        self,
        start_date: str,
        end_date: Optional[str] = None,
        flow_intensity: str = "medium",
        notes: str = ""
    ) -> Dict[str, Any]:
        """
        Registra un nuovo ciclo mestruale.

        Args:
            start_date: Data di inizio (ISO format o "today")
            end_date: Data di fine opzionale (ISO format)
            flow_intensity: Intensità flusso (spotting, light, medium, heavy, very_heavy)
            notes: Note opzionali

        Returns:
            Dizionario con risultato operazione
        """
        try:
            # Parse date strings
            if start_date.lower() == "today":
                start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))

            end_dt = None
            if end_date:
                if end_date.lower() == "today":
                    end_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

            # Validazione con Pydantic
            cycle_entry = CycleEntry(
                start_date=start_dt,
                end_date=end_dt,
                flow_intensity=FlowIntensity(flow_intensity.lower()),
                notes=notes
            )

            # Salva nel database
            response = self.db.add_cycle(cycle_entry)

            if response.success:
                # Genera messaggio contextual
                context_msg = self._generate_context_message(
                    flow_intensity,
                    response.cycle_length
                )

                return {
                    "success": True,
                    "message": response.message,
                    "entry_id": response.entry_id,
                    "cycle_length": response.cycle_length,
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
                "message": "Dati non validi. Controlla il formato date e flow_intensity.",
                "error": str(e)
            }

        except ValueError as e:
            logger.error(f"Value error: {e}")

            # Suggerisci valori validi
            valid_intensities = [f.value for f in FlowIntensity]

            return {
                "success": False,
                "message": f"Flow intensity non valida. Valori validi: {', '.join(valid_intensities)}",
                "error": str(e)
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "message": "Errore inaspettato. Riprova più tardi.",
                "error": str(e)
            }

    def update_cycle_end(
        self,
        cycle_id: int,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Aggiorna la data di fine di un ciclo esistente.

        Args:
            cycle_id: ID del ciclo da aggiornare
            end_date: Nuova data di fine

        Returns:
            Dizionario con risultato operazione
        """
        try:
            # Parse date string
            if end_date.lower() == "today":
                end_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

            # Aggiorna nel database
            response = self.db.update_cycle_end_date(cycle_id, end_dt)

            if response.success:
                return {
                    "success": True,
                    "message": response.message,
                    "entry_id": response.entry_id,
                    "cycle_length": response.cycle_length,
                    "timestamp": response.timestamp.isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": response.message
                }

        except Exception as e:
            logger.error(f"Error updating cycle: {e}")
            return {
                "success": False,
                "message": "Errore nell'aggiornare il ciclo",
                "error": str(e)
            }

    def get_cycle_history(
        self,
        limit: int = 6
    ) -> Dict[str, Any]:
        """
        Recupera storico cicli.

        Args:
            limit: Numero massimo di cicli da recuperare

        Returns:
            Dizionario con lista cicli
        """
        try:
            cycles = self.db.get_cycles(limit=limit)

            return {
                "success": True,
                "count": len(cycles),
                "cycles": cycles
            }

        except Exception as e:
            logger.error(f"Error retrieving cycles: {e}")
            return {
                "success": False,
                "message": "Errore nel recuperare i cicli",
                "error": str(e)
            }

    def get_cycle_analytics(
        self,
        months: int = 6
    ) -> Dict[str, Any]:
        """
        Genera analytics e predizioni sui cicli.

        Args:
            months: Numero di mesi da analizzare

        Returns:
            Dizionario con statistiche e predizioni
        """
        try:
            summary = self.db.get_cycle_summary(months=months)

            # Genera insights
            insights = self._generate_insights(summary)

            return {
                "success": True,
                "period_months": months,
                "total_cycles": summary.total_cycles,
                "average_cycle_length": summary.average_cycle_length,
                "shortest_cycle": summary.shortest_cycle,
                "longest_cycle": summary.longest_cycle,
                "regularity_score": summary.regularity_score,
                "predicted_next_start": summary.predicted_next_start.isoformat() if summary.predicted_next_start else None,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error generating cycle analytics: {e}")
            return {
                "success": False,
                "message": "Errore nel generare le analytics",
                "error": str(e)
            }

    def _generate_context_message(
        self,
        flow_intensity: str,
        cycle_length: Optional[int]
    ) -> str:
        """
        Genera messaggio contestuale basato sui dati del ciclo.

        Args:
            flow_intensity: Intensità del flusso
            cycle_length: Lunghezza del ciclo

        Returns:
            Messaggio con suggerimenti
        """
        messages = []

        # Flow intensity tips
        if flow_intensity == "very_heavy":
            messages.append(
                "⚠️ Flusso molto abbondante rilevato. Se hai bisogno di cambiare "
                "l'assorbente più di una volta ogni 2 ore, consulta un medico."
            )
        elif flow_intensity == "spotting":
            messages.append(
                "💡 Spotting può essere normale, ma se persiste o hai dubbi, "
                "consulta il tuo medico."
            )

        # Cycle length tips
        if cycle_length:
            if cycle_length < 3:
                messages.append(
                    "ℹ️ Ciclo molto breve. È normale una certa variabilità, "
                    "ma monitora se si ripete."
                )
            elif cycle_length > 7:
                messages.append(
                    "⚠️ Ciclo lungo. Se supera regolarmente i 7 giorni, "
                    "è consigliabile consultare un medico."
                )
            else:
                messages.append(
                    "✅ Lunghezza ciclo nella norma (3-7 giorni)."
                )

        return " ".join(messages) if messages else "✅ Ciclo registrato correttamente."

    def _generate_insights(self, summary) -> List[str]:
        """
        Genera insights basati sul riepilogo cicli.

        Args:
            summary: CycleSummary object

        Returns:
            Lista di insights
        """
        insights = []

        if summary.total_cycles == 0:
            insights.append("📊 Nessun ciclo registrato. Inizia a tracciare per ottenere insights!")
            return insights

        # Regularity insight
        if summary.regularity_score is not None:
            if summary.regularity_score >= 80:
                insights.append(
                    f"✅ Ottima regolarità del ciclo (score: {summary.regularity_score:.0f}/100). "
                    "I tuoi cicli sono molto prevedibili!"
                )
            elif summary.regularity_score >= 60:
                insights.append(
                    f"📊 Regolarità moderata (score: {summary.regularity_score:.0f}/100). "
                    "C'è una certa variabilità nei tuoi cicli."
                )
            else:
                insights.append(
                    f"⚠️ Cicli irregolari (score: {summary.regularity_score:.0f}/100). "
                    "Considera di discuterne con il tuo medico, specialmente se hai PCOS."
                )

        # Average length insight
        if summary.average_cycle_length:
            if 3 <= summary.average_cycle_length <= 7:
                insights.append(
                    f"✅ Lunghezza media del ciclo nella norma ({summary.average_cycle_length:.1f} giorni)."
                )
            else:
                insights.append(
                    f"ℹ️ Lunghezza media del ciclo: {summary.average_cycle_length:.1f} giorni. "
                    "Monitora eventuali cambiamenti."
                )

        # Variability insight
        if summary.shortest_cycle and summary.longest_cycle:
            variability = summary.longest_cycle - summary.shortest_cycle
            if variability > 3:
                insights.append(
                    f"📈 Alta variabilità: da {summary.shortest_cycle} a {summary.longest_cycle} giorni. "
                    "Cerca pattern correlati (stress, dieta, sintomi PCOS)."
                )

        # Prediction insight
        if summary.predicted_next_start:
            days_until = (summary.predicted_next_start - datetime.now()).days
            if days_until > 0:
                insights.append(
                    f"🔮 Prossimo ciclo previsto tra circa {days_until} giorni "
                    f"({summary.predicted_next_start.strftime('%d/%m/%Y')})"
                )
            else:
                insights.append(
                    f"🔮 Il prossimo ciclo potrebbe iniziare a breve, "
                    f"secondo le previsioni entro il {summary.predicted_next_start.strftime('%d/%m/%Y')}"
                )

        # Data quality insight
        if summary.total_cycles < 3:
            insights.append(
                "💡 Continua a tracciare per almeno 3 cicli per ottenere predizioni più accurate!"
            )

        return insights
