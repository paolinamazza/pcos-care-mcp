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
from database.models import SymptomEntry, SymptomResponse, SymptomSummary

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
