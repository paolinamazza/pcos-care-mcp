"""
Database Manager - Business Logic Layer
Gestisce tutte le operazioni database con error handling robusto
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from database.schema import get_session_maker, SymptomRecord, CycleRecord
from database.models import (
    SymptomEntry, SymptomResponse, SymptomSummary,
    CycleEntry, CycleResponse, CycleSummary
)

logger = logging.getLogger("pcos-care-mcp.database")


class DatabaseManager:
    """
    Manager per operazioni database.
    
    Implementa pattern Repository per separare business logic da data access.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Inizializza database manager.

        Args:
            db_url: Database URL (optional, default: local SQLite)
        """
        self.SessionMaker = get_session_maker(db_url)
        logger.info("Database Manager initialized")

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy Session
        """
        return self.SessionMaker()
    
    def add_symptom(self, symptom: SymptomEntry) -> SymptomResponse:
        """
        Aggiunge un nuovo sintomo al database.
        
        Args:
            symptom: SymptomEntry validato con Pydantic
            
        Returns:
            SymptomResponse con esito operazione
            
        Raises:
            Exception: Se operazione fallisce
        """
        session: Session = self.SessionMaker()
        
        try:
            # Crea record database
            record = SymptomRecord(
                symptom_type=symptom.symptom_type.value,
                intensity=symptom.intensity,
                notes=symptom.notes,
                timestamp=symptom.timestamp
            )
            
            session.add(record)
            session.commit()
            session.refresh(record)
            
            logger.info(f"Symptom added: ID={record.id}, type={record.symptom_type}")
            
            return SymptomResponse(
                success=True,
                message=f"Sintomo '{symptom.symptom_type.value}' registrato con successo",
                entry_id=record.id,
                timestamp=record.timestamp
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding symptom: {str(e)}")
            
            return SymptomResponse(
                success=False,
                message=f"Errore nel salvare il sintomo: {str(e)}",
                timestamp=datetime.now()
            )
            
        finally:
            session.close()
    
    def get_symptoms(
        self,
        limit: int = 10,
        symptom_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera sintomi dal database con filtri opzionali.
        
        Args:
            limit: Numero massimo di risultati
            symptom_type: Filtra per tipo di sintomo
            start_date: Filtra da questa data
            end_date: Filtra fino a questa data
            
        Returns:
            Lista di sintomi come dizionari
        """
        session: Session = self.SessionMaker()
        
        try:
            query = session.query(SymptomRecord)
            
            # Applica filtri
            if symptom_type:
                query = query.filter(SymptomRecord.symptom_type == symptom_type)
            
            if start_date:
                query = query.filter(SymptomRecord.timestamp >= start_date)
            
            if end_date:
                query = query.filter(SymptomRecord.timestamp <= end_date)
            
            # Ordina per timestamp discendente (più recenti prima)
            query = query.order_by(desc(SymptomRecord.timestamp))
            
            # Limita risultati
            records = query.limit(limit).all()
            
            logger.info(f"Retrieved {len(records)} symptom records")
            
            return [record.to_dict() for record in records]
            
        except Exception as e:
            logger.error(f"Error retrieving symptoms: {str(e)}")
            return []
            
        finally:
            session.close()
    
    def get_symptom_summary(
        self,
        days: int = 30
    ) -> SymptomSummary:
        """
        Genera un riepilogo statistico dei sintomi.
        
        Args:
            days: Numero di giorni da analizzare (default: 30)
            
        Returns:
            SymptomSummary con statistiche
        """
        session: Session = self.SessionMaker()
        
        try:
            # Calcola date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Query per sintomi nel periodo
            query = session.query(SymptomRecord).filter(
                SymptomRecord.timestamp >= start_date,
                SymptomRecord.timestamp <= end_date
            )
            
            # Conta totale
            total_entries = query.count()
            
            if total_entries == 0:
                return SymptomSummary(
                    total_entries=0,
                    most_common_symptom=None,
                    average_intensity=None,
                    date_range=(start_date, end_date)
                )
            
            # Sintomo più comune
            most_common = session.query(
                SymptomRecord.symptom_type,
                func.count(SymptomRecord.id).label('count')
            ).filter(
                SymptomRecord.timestamp >= start_date,
                SymptomRecord.timestamp <= end_date
            ).group_by(
                SymptomRecord.symptom_type
            ).order_by(
                desc('count')
            ).first()
            
            # Intensità media
            avg_intensity = session.query(
                func.avg(SymptomRecord.intensity)
            ).filter(
                SymptomRecord.timestamp >= start_date,
                SymptomRecord.timestamp <= end_date
            ).scalar()
            
            logger.info(f"Generated summary: {total_entries} entries in last {days} days")
            
            return SymptomSummary(
                total_entries=total_entries,
                most_common_symptom=most_common[0] if most_common else None,
                average_intensity=round(float(avg_intensity), 2) if avg_intensity else None,
                date_range=(start_date, end_date)
            )
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return SymptomSummary(
                total_entries=0,
                most_common_symptom=None,
                average_intensity=None,
                date_range=(start_date, end_date)
            )
            
        finally:
            session.close()
    
    def delete_symptom(self, symptom_id: int) -> bool:
        """
        Elimina un sintomo dal database.

        Args:
            symptom_id: ID del sintomo da eliminare

        Returns:
            True se eliminato, False altrimenti
        """
        session: Session = self.SessionMaker()

        try:
            record = session.query(SymptomRecord).filter(
                SymptomRecord.id == symptom_id
            ).first()

            if record:
                session.delete(record)
                session.commit()
                logger.info(f"Symptom deleted: ID={symptom_id}")
                return True
            else:
                logger.warning(f"Symptom not found: ID={symptom_id}")
                return False

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting symptom: {str(e)}")
            return False

        finally:
            session.close()

    # ========================================================================
    # FASE 3: Cycle Tracking Methods
    # ========================================================================

    def add_cycle(self, cycle: CycleEntry) -> CycleResponse:
        """
        Aggiunge un nuovo ciclo mestruale al database.

        Args:
            cycle: CycleEntry validato con Pydantic

        Returns:
            CycleResponse con esito operazione
        """
        session: Session = self.SessionMaker()

        try:
            # Crea record database
            record = CycleRecord(
                start_date=cycle.start_date,
                end_date=cycle.end_date,
                flow_intensity=cycle.flow_intensity.value,
                notes=cycle.notes
            )

            session.add(record)
            session.commit()
            session.refresh(record)

            # Calcola lunghezza ciclo se end_date presente
            cycle_length = None
            if record.end_date:
                cycle_length = (record.end_date - record.start_date).days

            logger.info(f"Cycle added: ID={record.id}, start={record.start_date}")

            return CycleResponse(
                success=True,
                message="Ciclo mestruale registrato con successo",
                entry_id=record.id,
                cycle_length=cycle_length,
                timestamp=datetime.now()
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding cycle: {str(e)}")

            return CycleResponse(
                success=False,
                message=f"Errore nel salvare il ciclo: {str(e)}",
                timestamp=datetime.now()
            )

        finally:
            session.close()

    def get_cycles(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera cicli dal database con filtri opzionali.

        Args:
            limit: Numero massimo di risultati
            start_date: Filtra da questa data
            end_date: Filtra fino a questa data

        Returns:
            Lista di cicli come dizionari
        """
        session: Session = self.SessionMaker()

        try:
            query = session.query(CycleRecord)

            # Applica filtri
            if start_date:
                query = query.filter(CycleRecord.start_date >= start_date)

            if end_date:
                query = query.filter(CycleRecord.start_date <= end_date)

            # Ordina per start_date discendente (più recenti prima)
            query = query.order_by(desc(CycleRecord.start_date))

            # Limita risultati
            records = query.limit(limit).all()

            logger.info(f"Retrieved {len(records)} cycle records")

            # Converti in dizionari con calcolo cycle_length
            result = []
            for record in records:
                cycle_dict = {
                    'id': record.id,
                    'start_date': record.start_date.isoformat(),
                    'end_date': record.end_date.isoformat() if record.end_date else None,
                    'flow_intensity': record.flow_intensity,
                    'notes': record.notes,
                    'created_at': record.created_at.isoformat(),
                    'cycle_length': (record.end_date - record.start_date).days if record.end_date else None
                }
                result.append(cycle_dict)

            return result

        except Exception as e:
            logger.error(f"Error retrieving cycles: {str(e)}")
            return []

        finally:
            session.close()

    def update_cycle_end_date(
        self,
        cycle_id: int,
        end_date: datetime
    ) -> CycleResponse:
        """
        Aggiorna la data di fine di un ciclo esistente.

        Args:
            cycle_id: ID del ciclo da aggiornare
            end_date: Nuova data di fine

        Returns:
            CycleResponse con esito operazione
        """
        session: Session = self.SessionMaker()

        try:
            record = session.query(CycleRecord).filter(
                CycleRecord.id == cycle_id
            ).first()

            if not record:
                return CycleResponse(
                    success=False,
                    message=f"Ciclo con ID {cycle_id} non trovato",
                    timestamp=datetime.now()
                )

            # Valida che end_date sia dopo start_date
            if end_date < record.start_date:
                return CycleResponse(
                    success=False,
                    message="La data di fine deve essere dopo la data di inizio",
                    timestamp=datetime.now()
                )

            record.end_date = end_date
            session.commit()
            session.refresh(record)

            cycle_length = (record.end_date - record.start_date).days

            logger.info(f"Cycle updated: ID={cycle_id}, end_date={end_date}")

            return CycleResponse(
                success=True,
                message="Data di fine ciclo aggiornata con successo",
                entry_id=record.id,
                cycle_length=cycle_length,
                timestamp=datetime.now()
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating cycle: {str(e)}")

            return CycleResponse(
                success=False,
                message=f"Errore nell'aggiornare il ciclo: {str(e)}",
                timestamp=datetime.now()
            )

        finally:
            session.close()

    def get_cycle_summary(
        self,
        months: int = 6
    ) -> CycleSummary:
        """
        Genera un riepilogo statistico dei cicli mestruali.

        Args:
            months: Numero di mesi da analizzare (default: 6)

        Returns:
            CycleSummary con statistiche
        """
        session: Session = self.SessionMaker()

        try:
            # Calcola date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            # Query per cicli nel periodo con end_date non null
            query = session.query(CycleRecord).filter(
                CycleRecord.start_date >= start_date,
                CycleRecord.start_date <= end_date,
                CycleRecord.end_date.isnot(None)
            )

            # Conta totale
            total_cycles = query.count()

            if total_cycles == 0:
                return CycleSummary(
                    total_cycles=0,
                    average_cycle_length=None,
                    shortest_cycle=None,
                    longest_cycle=None,
                    regularity_score=None,
                    predicted_next_start=None
                )

            # Recupera tutti i cicli per calcoli
            cycles = query.order_by(CycleRecord.start_date).all()

            # Calcola lunghezze cicli
            cycle_lengths = [
                (c.end_date - c.start_date).days
                for c in cycles
                if c.end_date
            ]

            if not cycle_lengths:
                return CycleSummary(
                    total_cycles=total_cycles,
                    average_cycle_length=None,
                    shortest_cycle=None,
                    longest_cycle=None,
                    regularity_score=None,
                    predicted_next_start=None
                )

            # Statistiche di base
            avg_length = sum(cycle_lengths) / len(cycle_lengths)
            shortest = min(cycle_lengths)
            longest = max(cycle_lengths)

            # Calcola regularity score (più bassa la varianza, più alto il score)
            variance = sum((x - avg_length) ** 2 for x in cycle_lengths) / len(cycle_lengths)
            std_dev = variance ** 0.5
            regularity = max(0, 100 - (std_dev * 10))  # 0-100 scale

            # Predici prossimo ciclo basato su media
            last_cycle = cycles[-1]
            if last_cycle.end_date:
                predicted_next = last_cycle.end_date + timedelta(days=int(avg_length))
            else:
                predicted_next = None

            logger.info(f"Generated cycle summary: {total_cycles} cycles in last {months} months")

            return CycleSummary(
                total_cycles=total_cycles,
                average_cycle_length=round(avg_length, 1),
                shortest_cycle=shortest,
                longest_cycle=longest,
                regularity_score=round(regularity, 1),
                predicted_next_start=predicted_next
            )

        except Exception as e:
            logger.error(f"Error generating cycle summary: {str(e)}")
            return CycleSummary(
                total_cycles=0,
                average_cycle_length=None,
                shortest_cycle=None,
                longest_cycle=None,
                regularity_score=None,
                predicted_next_start=None
            )

        finally:
            session.close()
