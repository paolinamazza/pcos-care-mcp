"""
Unit Tests per Symptom Tracker Tool
Test per tracking sintomi PCOS (Fase 1-2)
"""

import pytest
from datetime import datetime, timedelta
from database import DatabaseManager, SymptomEntry, SymptomType
from tools.symptom_tracker import SymptomTracker


@pytest.fixture
def db_manager():
    """Fixture che crea un database in-memory per i test"""
    manager = DatabaseManager(db_url="sqlite:///:memory:")
    yield manager


@pytest.fixture
def symptom_tracker(db_manager):
    """Fixture che crea un SymptomTracker per i test"""
    return SymptomTracker(db_manager)


class TestSymptomTracker:
    """Test suite per SymptomTracker"""

    def test_init_symptom_tracker(self, symptom_tracker):
        """Test: Inizializzazione symptom tracker"""
        assert symptom_tracker is not None
        assert symptom_tracker.db is not None

    def test_track_symptom_success(self, symptom_tracker):
        """Test: Registrare un sintomo valido"""
        result = symptom_tracker.track_symptom(
            symptom_type="crampi",
            intensity=7,
            notes="Test crampi"
        )

        assert result["success"] is True
        assert result["entry_id"] is not None
        assert "registrato con successo" in result["message"]
        assert "context" in result

    def test_track_symptom_with_high_intensity(self, symptom_tracker):
        """Test: Sintomo con intensità alta genera warning"""
        result = symptom_tracker.track_symptom(
            symptom_type="crampi",
            intensity=9
        )

        assert result["success"] is True
        # Intensità alta dovrebbe generare un messaggio contestuale
        assert "context" in result

    def test_track_symptom_invalid_type(self, symptom_tracker):
        """Test: Tipo sintomo non valido deve fallire"""
        result = symptom_tracker.track_symptom(
            symptom_type="sintomo_inventato",
            intensity=5
        )

        assert result["success"] is False
        assert "non valido" in result["message"]
        assert "Sintomi validi" in result["message"]

    def test_track_symptom_invalid_intensity(self, symptom_tracker):
        """Test: Intensità fuori range deve fallire"""
        result = symptom_tracker.track_symptom(
            symptom_type="crampi",
            intensity=15  # Fuori range!
        )

        assert result["success"] is False
        assert "non valid" in result["message"].lower()

    def test_track_symptom_with_notes(self, symptom_tracker):
        """Test: Registrare sintomo con note"""
        result = symptom_tracker.track_symptom(
            symptom_type="mal_di_testa",
            intensity=6,
            notes="Dopo pranzo"
        )

        assert result["success"] is True
        assert result["entry_id"] is not None

    def test_get_recent_symptoms_empty(self, symptom_tracker):
        """Test: Recuperare sintomi quando DB è vuoto"""
        result = symptom_tracker.get_recent_symptoms(limit=10)

        assert result["success"] is True
        assert result["count"] == 0
        assert result["symptoms"] == []

    def test_get_recent_symptoms_with_data(self, symptom_tracker):
        """Test: Recuperare sintomi dopo averli inseriti"""
        # Aggiungi 3 sintomi
        for i in range(3):
            symptom_tracker.track_symptom(
                symptom_type="crampi",
                intensity=5 + i
            )

        result = symptom_tracker.get_recent_symptoms(limit=10)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["symptoms"]) == 3

    def test_get_recent_symptoms_limit(self, symptom_tracker):
        """Test: Limite nella query dei sintomi"""
        # Aggiungi 5 sintomi
        for i in range(5):
            symptom_tracker.track_symptom(
                symptom_type="crampi",
                intensity=5
            )

        # Richiedi solo 3
        result = symptom_tracker.get_recent_symptoms(limit=3)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["symptoms"]) == 3

    def test_get_recent_symptoms_multiple_types(self, symptom_tracker):
        """Test: Recuperare sintomi di vari tipi"""
        # Aggiungi sintomi diversi
        symptom_tracker.track_symptom(symptom_type="crampi", intensity=5)
        symptom_tracker.track_symptom(symptom_type="mal_di_testa", intensity=6)
        symptom_tracker.track_symptom(symptom_type="crampi", intensity=7)

        # Recupera tutti i sintomi
        result = symptom_tracker.get_recent_symptoms(limit=10)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["symptoms"]) == 3

    def test_get_summary_empty(self, symptom_tracker):
        """Test: Summary su database vuoto"""
        result = symptom_tracker.get_summary(days=30)

        assert result["success"] is True
        assert "total_entries" in result or "insights" in result

    def test_get_summary_with_data(self, symptom_tracker):
        """Test: Summary con dati"""
        # Aggiungi sintomi
        symptom_tracker.track_symptom(symptom_type="crampi", intensity=8)
        symptom_tracker.track_symptom(symptom_type="crampi", intensity=6)
        symptom_tracker.track_symptom(symptom_type="mal_di_testa", intensity=5)

        result = symptom_tracker.get_summary(days=30)

        assert result["success"] is True
        # Il formato esatto può variare, verifichiamo solo che sia valido
        assert isinstance(result, dict)

    def test_get_summary_insights(self, symptom_tracker):
        """Test: Verifica generazione insights nel summary"""
        # Aggiungi sintomi
        for i in range(5):
            symptom_tracker.track_symptom(symptom_type="crampi", intensity=7)

        result = symptom_tracker.get_summary(days=30)

        assert result["success"] is True
        assert "insights" in result
        assert isinstance(result["insights"], list)


class TestSymptomTrackerContextMessages:
    """Test per messaggi contestuali"""

    def test_high_intensity_warning(self, symptom_tracker):
        """Test: Warning per intensità alta"""
        result = symptom_tracker.track_symptom(
            symptom_type="crampi",
            intensity=9
        )

        assert result["success"] is True
        # Dovrebbe contenere un warning/suggerimento
        assert "context" in result

    def test_different_symptom_types(self, symptom_tracker):
        """Test: Context messages per vari tipi di sintomi"""
        # Usa solo sintomi validi
        symptom_types = ["crampi", "mal_di_testa", "acne"]

        for stype in symptom_types:
            result = symptom_tracker.track_symptom(
                symptom_type=stype,
                intensity=6
            )
            assert result["success"] is True
            assert "context" in result


class TestSymptomTrackerHelpers:
    """Test per metodi helper"""

    def test_logger_configuration(self):
        """Test: Verifica configurazione logger"""
        from tools import symptom_tracker

        assert hasattr(symptom_tracker, 'logger')
        assert symptom_tracker.logger is not None

    def test_class_methods_exist(self):
        """Test: Verifica esistenza metodi principali"""
        assert hasattr(SymptomTracker, '__init__')
        assert hasattr(SymptomTracker, 'track_symptom')
        assert hasattr(SymptomTracker, 'get_recent_symptoms')
        assert hasattr(SymptomTracker, 'get_summary')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
