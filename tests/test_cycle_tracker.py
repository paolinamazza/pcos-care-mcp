"""
Unit Tests per Cycle Tracker Tool
Test per la logica business del tracking del ciclo mestruale
"""

import pytest
from datetime import datetime, timedelta
from database import DatabaseManager, CycleEntry, FlowIntensity
from tools.cycle_tracker import CycleTracker


@pytest.fixture
def db_manager():
    """Fixture che crea un database in-memory per i test"""
    manager = DatabaseManager(db_url="sqlite:///:memory:")
    yield manager
    # Cleanup automatico (in-memory DB viene distrutto)


@pytest.fixture
def cycle_tracker(db_manager):
    """Fixture che crea un CycleTracker per i test"""
    return CycleTracker(db_manager)


class TestCycleTracker:
    """Test suite per CycleTracker"""

    def test_track_cycle_success(self, cycle_tracker):
        """Test: Registrare un ciclo valido deve funzionare"""
        result = cycle_tracker.track_cycle(
            start_date="today",
            end_date=None,
            flow_intensity="medium",
            notes="Test cycle"
        )

        assert result["success"] is True
        assert result["entry_id"] is not None
        assert "registrato con successo" in result["message"]
        assert "context" in result

    def test_track_cycle_with_end_date(self, cycle_tracker):
        """Test: Registrare un ciclo con data di fine"""
        start = datetime.now() - timedelta(days=5)
        end = datetime.now()

        result = cycle_tracker.track_cycle(
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            flow_intensity="heavy",
            notes="Ciclo completo"
        )

        assert result["success"] is True
        assert result["cycle_length"] == 5
        assert result["entry_id"] is not None

    def test_track_cycle_invalid_flow_intensity(self, cycle_tracker):
        """Test: Flow intensity non valida deve fallire"""
        result = cycle_tracker.track_cycle(
            start_date="today",
            flow_intensity="invalid_intensity"
        )

        assert result["success"] is False
        assert "Flow intensity non valida" in result["message"]
        assert "error" in result

    def test_track_cycle_invalid_date_format(self, cycle_tracker):
        """Test: Formato data non valido deve fallire"""
        result = cycle_tracker.track_cycle(
            start_date="not-a-date",
            flow_intensity="medium"
        )

        assert result["success"] is False
        assert "error" in result

    def test_update_cycle_end(self, cycle_tracker):
        """Test: Aggiornare la data di fine di un ciclo"""
        # Usa date fisse per evitare problemi di timing
        start = datetime(2025, 10, 1, 0, 0, 0)
        end = datetime(2025, 10, 6, 0, 0, 0)

        result1 = cycle_tracker.track_cycle(
            start_date=start.isoformat(),
            flow_intensity="medium"
        )
        cycle_id = result1["entry_id"]

        # Poi aggiorna la fine
        result2 = cycle_tracker.update_cycle_end(
            cycle_id=cycle_id,
            end_date=end.isoformat()
        )

        assert result2["success"] is True
        assert result2["cycle_length"] == 5  # 1-6 ottobre = 5 giorni
        assert "aggiornata" in result2["message"]

    def test_update_cycle_end_invalid_id(self, cycle_tracker):
        """Test: Aggiornare ciclo inesistente deve fallire"""
        result = cycle_tracker.update_cycle_end(
            cycle_id=9999,
            end_date="today"
        )

        assert result["success"] is False
        assert "non trovato" in result["message"]

    def test_get_cycle_history_empty(self, cycle_tracker):
        """Test: Storico su database vuoto"""
        result = cycle_tracker.get_cycle_history()

        assert result["success"] is True
        assert result["count"] == 0
        assert result["cycles"] == []

    def test_get_cycle_history_with_data(self, cycle_tracker):
        """Test: Recuperare storico cicli dopo averli inseriti"""
        # Aggiungi 3 cicli
        for i in range(3):
            start = datetime.now() - timedelta(days=(30 * (i + 1)))
            cycle_tracker.track_cycle(
                start_date=start.isoformat(),
                flow_intensity="medium"
            )

        # Recupera storico
        result = cycle_tracker.get_cycle_history(limit=10)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["cycles"]) == 3

    def test_cycle_analytics_empty_database(self, cycle_tracker):
        """Test: Analytics su database vuoto"""
        result = cycle_tracker.get_cycle_analytics(months=3)

        assert result["success"] is True
        assert result["total_cycles"] == 0
        assert "Nessun ciclo registrato" in result["insights"][0]

    def test_cycle_analytics_regularity_score(self, cycle_tracker):
        """Test: Calcolo regularity score con cicli regolari"""
        # Aggiungi 3 cicli regolari (ogni 28 giorni, durata 5 giorni)
        for i in range(3):
            start = datetime.now() - timedelta(days=(28 * (3 - i)))
            end = start + timedelta(days=5)
            cycle_tracker.track_cycle(
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                flow_intensity="medium"
            )

        result = cycle_tracker.get_cycle_analytics(months=3)

        assert result["success"] is True
        assert result["total_cycles"] == 3
        assert result["average_cycle_length"] == pytest.approx(5.0, 0.1)
        # Con cicli perfettamente regolari, score dovrebbe essere alto
        assert result["regularity_score"] >= 80

    def test_cycle_analytics_irregular_cycles(self, cycle_tracker):
        """Test: Analytics con cicli irregolari"""
        # Aggiungi cicli con lunghezze diverse (dentro gli ultimi 3 mesi)
        cycle_lengths = [3, 7, 4]
        for i, length in enumerate(cycle_lengths):
            start = datetime.now() - timedelta(days=(20 * (i + 1)))
            end = start + timedelta(days=length)
            cycle_tracker.track_cycle(
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                flow_intensity="medium"
            )

        result = cycle_tracker.get_cycle_analytics(months=3)

        assert result["success"] is True
        assert result["total_cycles"] == 3
        assert result["shortest_cycle"] == 3
        assert result["longest_cycle"] == 7
        # Con cicli irregolari, score dovrebbe essere più basso
        assert result["regularity_score"] < 100

    def test_cycle_length_calculation(self, cycle_tracker):
        """Test: Verifica che cycle_length venga calcolato correttamente"""
        start = datetime.now() - timedelta(days=6)
        end = datetime.now()

        result = cycle_tracker.track_cycle(
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            flow_intensity="light"
        )

        assert result["success"] is True
        assert result["cycle_length"] == 6

    def test_next_cycle_prediction(self, cycle_tracker):
        """Test: Verifica predizione prossimo ciclo"""
        # Aggiungi cicli storici regolari (ultimi 3 cicli, ogni 28 giorni)
        for i in range(3):
            # i=0: 56 giorni fa, i=1: 28 giorni fa, i=2: appena passato
            start = datetime.now() - timedelta(days=(28 * (3 - i)))
            end = start + timedelta(days=5)
            cycle_tracker.track_cycle(
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                flow_intensity="medium"
            )

        result = cycle_tracker.get_cycle_analytics(months=6)

        assert result["success"] is True
        assert result["predicted_next_start"] is not None
        # La predizione esiste (potrebbe essere nel passato o futuro a seconda del timing)
        predicted_date = datetime.fromisoformat(result["predicted_next_start"])
        assert isinstance(predicted_date, datetime)


class TestCycleContextMessages:
    """Test per messaggi contestuali generati"""

    def test_very_heavy_flow_warning(self, cycle_tracker):
        """Test: Warning per flusso molto abbondante"""
        result = cycle_tracker.track_cycle(
            start_date="today",
            flow_intensity="very_heavy"
        )

        assert result["success"] is True
        assert "⚠️" in result["context"]
        assert "molto abbondante" in result["context"]

    def test_spotting_message(self, cycle_tracker):
        """Test: Messaggio per spotting"""
        result = cycle_tracker.track_cycle(
            start_date="today",
            flow_intensity="spotting"
        )

        assert result["success"] is True
        assert "💡" in result["context"]
        assert "Spotting" in result["context"]

    def test_long_cycle_warning(self, cycle_tracker):
        """Test: Warning per ciclo lungo"""
        start = datetime.now() - timedelta(days=8)
        end = datetime.now()

        result = cycle_tracker.track_cycle(
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            flow_intensity="medium"
        )

        assert result["success"] is True
        assert "⚠️" in result["context"]
        assert "lungo" in result["context"].lower()

    def test_normal_cycle_confirmation(self, cycle_tracker):
        """Test: Messaggio di conferma per ciclo normale"""
        start = datetime.now() - timedelta(days=5)
        end = datetime.now()

        result = cycle_tracker.track_cycle(
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            flow_intensity="medium"
        )

        assert result["success"] is True
        assert "✅" in result["context"]
        assert "norma" in result["context"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
