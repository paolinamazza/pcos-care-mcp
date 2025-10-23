"""
Unit Tests per Pattern Analyzer Tool
Test per analisi pattern e correlazioni sintomi-ciclo
"""

import pytest
from datetime import datetime, timedelta
from database import DatabaseManager, SymptomEntry, SymptomType, CycleEntry, FlowIntensity
from tools.pattern_analyzer import PatternAnalyzer


@pytest.fixture
def db_manager():
    """Fixture che crea un database in-memory per i test"""
    manager = DatabaseManager(db_url="sqlite:///:memory:")
    yield manager


@pytest.fixture
def pattern_analyzer(db_manager):
    """Fixture che crea un PatternAnalyzer per i test"""
    return PatternAnalyzer(db_manager)


@pytest.fixture
def populated_db(db_manager):
    """Fixture con database popolato con dati sintomi e cicli"""
    # Aggiungi cicli degli ultimi 3 mesi
    for i in range(3):
        start = datetime.now() - timedelta(days=(28 * (3 - i)))
        end = start + timedelta(days=5)
        db_manager.add_cycle(CycleEntry(
            start_date=start,
            end_date=end,
            flow_intensity=FlowIntensity.MEDIUM
        ))

    # Aggiungi sintomi correlati
    for i in range(10):
        days_ago = i * 7  # Un sintomo a settimana
        timestamp = datetime.now() - timedelta(days=days_ago)
        db_manager.add_symptom(SymptomEntry(
            symptom_type=SymptomType.CRAMPI,
            intensity=5 + (i % 3),
            timestamp=timestamp
        ))

    return db_manager


class TestPatternAnalyzer:
    """Test suite per PatternAnalyzer"""

    def test_init_pattern_analyzer(self, pattern_analyzer):
        """Test: Inizializzazione pattern analyzer"""
        assert pattern_analyzer is not None
        assert pattern_analyzer.db is not None

    def test_correlation_analysis_insufficient_data(self, pattern_analyzer):
        """Test: Analisi correlazione con dati insufficienti"""
        result = pattern_analyzer.analyze_symptom_cycle_correlation(months=3)

        assert result["success"] is False
        assert "insufficienti" in result["message"].lower()

    def test_correlation_analysis_with_data(self, populated_db):
        """Test: Analisi correlazione con dati sufficienti"""
        analyzer = PatternAnalyzer(populated_db)
        result = analyzer.analyze_symptom_cycle_correlation(months=3)

        # Potrebbe fallire se pandas/numpy non sono installati
        if "Dipendenze" in result.get("message", ""):
            pytest.skip("Dependencies not available")

        assert result["success"] is True
        assert "total_symptoms_analyzed" in result
        assert "total_cycles_analyzed" in result
        assert result["total_symptoms_analyzed"] > 0
        assert result["total_cycles_analyzed"] > 0

    def test_symptom_trends_no_data(self, pattern_analyzer):
        """Test: Analisi trend senza dati"""
        result = pattern_analyzer.analyze_symptom_trends(
            symptom_type="crampi",
            days=90
        )

        assert result["success"] is False
        assert "Nessun sintomo" in result["message"]

    def test_symptom_trends_with_data(self, populated_db):
        """Test: Analisi trend con dati"""
        analyzer = PatternAnalyzer(populated_db)
        result = analyzer.analyze_symptom_trends(
            symptom_type="crampi",
            days=90
        )

        assert result["success"] is True
        assert "period_days" in result
        assert result["period_days"] == 90
        assert "symptom_type" in result

    def test_symptom_trends_all_types(self, populated_db):
        """Test: Analisi trend per tutti i tipi di sintomi"""
        analyzer = PatternAnalyzer(populated_db)
        result = analyzer.analyze_symptom_trends(days=30)

        assert result["success"] is True
        assert result["symptom_type"] == "all"

    def test_identify_patterns_no_data(self, pattern_analyzer):
        """Test: Identificazione pattern senza dati"""
        result = pattern_analyzer.identify_recurring_patterns(min_occurrences=2)

        assert result["success"] is False
        assert "insufficienti" in result["message"].lower()

    def test_identify_patterns_with_data(self, populated_db):
        """Test: Identificazione pattern con dati"""
        analyzer = PatternAnalyzer(populated_db)
        result = analyzer.identify_recurring_patterns(min_occurrences=2)

        assert result["success"] is True
        assert "patterns" in result
        assert "patterns_found" in result
        assert isinstance(result["patterns"], list)

    def test_error_handling(self, db_manager):
        """Test: Gestione errori durante analisi"""
        analyzer = PatternAnalyzer(db_manager)

        # Test con parametri validi ma DB vuoto
        result = analyzer.analyze_symptom_cycle_correlation(months=3)

        # Dovrebbe gestire gracefully il caso di dati insufficienti
        assert "success" in result
        assert isinstance(result["success"], bool)

    def test_multiple_symptom_types(self, db_manager):
        """Test: Analisi con multiple tipi di sintomi"""
        # Aggiungi sintomi diversi
        symptom_types = [SymptomType.CRAMPI, SymptomType.MAL_DI_TESTA, SymptomType.ACNE]

        for i, stype in enumerate(symptom_types):
            for j in range(3):
                timestamp = datetime.now() - timedelta(days=(i * 10 + j))
                db_manager.add_symptom(SymptomEntry(
                    symptom_type=stype,
                    intensity=5 + j,
                    timestamp=timestamp
                ))

        # Aggiungi un ciclo
        start = datetime.now() - timedelta(days=15)
        end = start + timedelta(days=5)
        db_manager.add_cycle(CycleEntry(
            start_date=start,
            end_date=end,
            flow_intensity=FlowIntensity.MEDIUM
        ))

        analyzer = PatternAnalyzer(db_manager)
        result = analyzer.identify_recurring_patterns(min_occurrences=2)

        assert result["success"] is True

    def test_time_range_parameters(self, populated_db):
        """Test: Parametri di range temporale"""
        analyzer = PatternAnalyzer(populated_db)

        # Test con diversi range temporali
        for months in [1, 3, 6]:
            result = analyzer.analyze_symptom_cycle_correlation(months=months)
            if result["success"]:
                assert result["period_months"] == months

    def test_insights_generation(self, populated_db):
        """Test: Generazione insights"""
        analyzer = PatternAnalyzer(populated_db)
        result = analyzer.identify_recurring_patterns(min_occurrences=2)

        if result["success"]:
            assert "insights" in result
            assert isinstance(result["insights"], list)


class TestPatternAnalyzerHelpers:
    """Test per metodi helper del PatternAnalyzer"""

    def test_dependencies_check(self):
        """Test: Verifica disponibilità dipendenze"""
        from tools import pattern_analyzer

        assert hasattr(pattern_analyzer, 'DEPENDENCIES_AVAILABLE')
        assert isinstance(pattern_analyzer.DEPENDENCIES_AVAILABLE, bool)

    def test_logger_configuration(self):
        """Test: Verifica configurazione logger"""
        from tools import pattern_analyzer

        assert hasattr(pattern_analyzer, 'logger')
        assert pattern_analyzer.logger is not None

    def test_class_methods_exist(self):
        """Test: Verifica esistenza metodi principali"""
        assert hasattr(PatternAnalyzer, '__init__')
        assert hasattr(PatternAnalyzer, 'analyze_symptom_cycle_correlation')
        assert hasattr(PatternAnalyzer, 'analyze_symptom_trends')
        assert hasattr(PatternAnalyzer, 'identify_recurring_patterns')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
