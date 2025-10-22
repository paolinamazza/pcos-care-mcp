"""
Database Schema usando SQLAlchemy ORM
Best practice: ORM invece di raw SQL per type safety e maintainability
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class SymptomRecord(Base):
    """
    Tabella per il tracking dei sintomi PCOS.
    
    Design choices:
    - id: Primary key auto-increment
    - symptom_type: String indexed per query veloci
    - intensity: Integer per semplicità (1-10)
    - notes: Text per note lunghe
    - timestamp: DateTime con default per auto-tracking
    - created_at: Per audit trail
    """
    
    __tablename__ = 'symptom_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symptom_type = Column(String(50), nullable=False, index=True)
    intensity = Column(Integer, nullable=False)
    notes = Column(Text, default="")
    timestamp = Column(DateTime, nullable=False, default=datetime.now, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SymptomRecord(id={self.id}, type='{self.symptom_type}', intensity={self.intensity})>"
    
    def to_dict(self):
        """Converte record in dizionario per serializzazione"""
        return {
            'id': self.id,
            'symptom_type': self.symptom_type,
            'intensity': self.intensity,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class CycleRecord(Base):
    """
    Tabella per il tracking del ciclo mestruale.
    
    Future implementation - placeholder per FASE 3
    """
    
    __tablename__ = 'cycle_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=True)
    flow_intensity = Column(String(20))  # light, medium, heavy
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<CycleRecord(id={self.id}, start='{self.start_date}')>"


def get_database_url(db_name: str = "pcos_care.db") -> str:
    """
    Genera database URL.
    
    Args:
        db_name: Nome del file database
        
    Returns:
        SQLAlchemy database URL
    """
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, db_name)
    return f'sqlite:///{db_path}'


def create_tables(engine):
    """
    Crea tutte le tabelle nel database.
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def get_session_maker(db_url: str = None):
    """
    Factory per creare session maker.
    
    Args:
        db_url: Database URL (default: local SQLite)
        
    Returns:
        SQLAlchemy sessionmaker
    """
    if db_url is None:
        db_url = get_database_url()
    
    engine = create_engine(
        db_url,
        echo=False,  # Set True per debug SQL queries
        future=True
    )
    
    # Crea tabelle se non esistono
    create_tables(engine)
    
    return sessionmaker(bind=engine, expire_on_commit=False)
