"""
Unit Tests per Database Layer
Best practice: Test isolati, setup/teardown, edge cases
"""

import pytest
from datetime import datetime, timedelta
from database import DatabaseManager, SymptomEntry, SymptomType


@pytest.fixture
def db_manager():
    """Fixture che crea un database in-memory per i test"""
    # Database in-memory per test veloci e isolati
    manager = DatabaseManager(db_url="sqlite:///:memory:")
    yield manager
    # Cleanup automatico (in-memory DB viene distrutto)


class TestDatabaseManager:
    """Test suite per DatabaseManager"""
    
    def test_add_symptom_success(self, db_manager):
        """Test: Aggiungere un sintomo valido deve funzionare"""
        symptom = SymptomEntry(
            symptom_type=SymptomType.CRAMPI,
            intensity=7,
            notes="Test crampi"
        )
        
        response = db_manager.add_symptom(symptom)
        
        assert response.success is True
        assert response.entry_id is not None
        assert "registrato con successo" in response.message
    
    def test_add_symptom_validation(self, db_manager):
        """Test: Intensità fuori range deve fallire"""
        with pytest.raises(Exception):
            symptom = SymptomEntry(
                symptom_type=SymptomType.CRAMPI,
                intensity=15,  # Fuori range!
                notes="Invalid intensity"
            )
    
    def test_get_symptoms_empty(self, db_manager):
        """Test: Database vuoto deve ritornare lista vuota"""
        symptoms = db_manager.get_symptoms()
        assert len(symptoms) == 0
    
    def test_get_symptoms_with_data(self, db_manager):
        """Test: Recuperare sintomi dopo averli inseriti"""
        # Aggiungi 3 sintomi
        for i in range(3):
            symptom = SymptomEntry(
                symptom_type=SymptomType.CRAMPI,
                intensity=5 + i,
                notes=f"Test {i}"
            )
            db_manager.add_symptom(symptom)
        
        # Recupera
        symptoms = db_manager.get_symptoms(limit=10)
        
        assert len(symptoms) == 3
        # Devono essere ordinati per timestamp discendente
        assert symptoms[0]['intensity'] == 7  # Ultimo inserito
    
    def test_get_symptoms_with_filter(self, db_manager):
        """Test: Filtrare sintomi per tipo"""
        # Aggiungi sintomi diversi
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.CRAMPI, intensity=5
        ))
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.MAL_DI_TESTA, intensity=6
        ))
        
        # Filtra solo crampi
        symptoms = db_manager.get_symptoms(symptom_type="crampi")
        
        assert len(symptoms) == 1
        assert symptoms[0]['symptom_type'] == 'crampi'
    
    def test_get_summary_empty(self, db_manager):
        """Test: Summary su database vuoto"""
        summary = db_manager.get_symptom_summary()
        
        assert summary.total_entries == 0
        assert summary.most_common_symptom is None
        assert summary.average_intensity is None
    
    def test_get_summary_with_data(self, db_manager):
        """Test: Summary con dati reali"""
        # Aggiungi sintomi
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.CRAMPI, intensity=8
        ))
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.CRAMPI, intensity=6
        ))
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.MAL_DI_TESTA, intensity=5
        ))
        
        summary = db_manager.get_symptom_summary(days=30)
        
        assert summary.total_entries == 3
        assert summary.most_common_symptom == "crampi"
        assert summary.average_intensity == pytest.approx(6.33, 0.1)
    
    def test_delete_symptom_success(self, db_manager):
        """Test: Eliminare un sintomo esistente"""
        # Aggiungi sintomo
        response = db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.CRAMPI, intensity=5
        ))
        symptom_id = response.entry_id
        
        # Elimina
        result = db_manager.delete_symptom(symptom_id)
        
        assert result is True
        
        # Verifica che sia eliminato
        symptoms = db_manager.get_symptoms()
        assert len(symptoms) == 0
    
    def test_delete_symptom_not_found(self, db_manager):
        """Test: Eliminare sintomo inesistente deve ritornare False"""
        result = db_manager.delete_symptom(9999)
        assert result is False


class TestDataModels:
    """Test per Pydantic models"""
    
    def test_symptom_entry_valid(self):
        """Test: Creazione SymptomEntry valido"""
        symptom = SymptomEntry(
            symptom_type=SymptomType.CRAMPI,
            intensity=7,
            notes="Test note"
        )
        
        assert symptom.symptom_type == SymptomType.CRAMPI
        assert symptom.intensity == 7
        assert symptom.notes == "Test note"
        assert isinstance(symptom.timestamp, datetime)
    
    def test_symptom_entry_invalid_intensity(self):
        """Test: Intensità fuori range deve fallire"""
        with pytest.raises(Exception):
            SymptomEntry(
                symptom_type=SymptomType.CRAMPI,
                intensity=11  # Fuori range!
            )
    
    def test_symptom_entry_notes_sanitization(self):
        """Test: Note con spazi vengono sanitizzate"""
        symptom = SymptomEntry(
            symptom_type=SymptomType.CRAMPI,
            intensity=5,
            notes="  Test with spaces  "
        )
        
        assert symptom.notes == "Test with spaces"
    
    def test_symptom_entry_default_timestamp(self):
        """Test: Timestamp viene auto-generato"""
        before = datetime.now()
        symptom = SymptomEntry(
            symptom_type=SymptomType.CRAMPI,
            intensity=5
        )
        after = datetime.now()
        
        assert before <= symptom.timestamp <= after


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
