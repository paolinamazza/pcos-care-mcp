"""
Pattern Analyzer Tool - FASE 3
Analisi avanzata di correlazioni tra sintomi e ciclo mestruale
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

try:
    import numpy as np
    import pandas as pd
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning("Pattern analysis dependencies not installed. Run: pip install pandas numpy")

from database import DatabaseManager

logger = logging.getLogger("pcos-care-mcp.tools")


class PatternAnalyzer:
    """
    Tool per analisi pattern avanzata.

    Responsabilità:
    - Correlazione sintomi-ciclo
    - Identificazione pattern ricorrenti
    - Trend analysis
    - Insights predittivi
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Inizializza pattern analyzer.

        Args:
            db_manager: Istanza di DatabaseManager
        """
        self.db = db_manager
        logger.info("PatternAnalyzer initialized")

    def analyze_symptom_cycle_correlation(
        self,
        months: int = 3
    ) -> Dict[str, Any]:
        """
        Analizza correlazione tra sintomi e fasi del ciclo mestruale.

        Args:
            months: Numero di mesi da analizzare

        Returns:
            Dizionario con analisi correlazione
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {
                    "success": False,
                    "message": "Dipendenze per pattern analysis non installate. Installa pandas e numpy."
                }

            # Get data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            symptoms = self.db.get_symptoms(
                limit=1000,
                start_date=start_date,
                end_date=end_date
            )

            cycles = self.db.get_cycles(
                limit=12,
                start_date=start_date,
                end_date=end_date
            )

            if not symptoms or not cycles:
                return {
                    "success": False,
                    "message": "Dati insufficienti per l'analisi. Registra più sintomi e cicli."
                }

            # Analyze correlation
            correlations = self._find_symptom_cycle_patterns(symptoms, cycles)

            # Generate insights
            insights = self._generate_correlation_insights(correlations)

            return {
                "success": True,
                "period_months": months,
                "total_symptoms_analyzed": len(symptoms),
                "total_cycles_analyzed": len(cycles),
                "correlations": correlations,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error in symptom-cycle correlation analysis: {e}")
            return {
                "success": False,
                "message": f"Errore nell'analisi: {str(e)}"
            }

    def analyze_symptom_trends(
        self,
        symptom_type: Optional[str] = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Analizza trend nel tempo per sintomi specifici.

        Args:
            symptom_type: Tipo di sintomo da analizzare (opzionale)
            days: Giorni da analizzare

        Returns:
            Dizionario con trend analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            symptoms = self.db.get_symptoms(
                limit=1000,
                symptom_type=symptom_type,
                start_date=start_date,
                end_date=end_date
            )

            if not symptoms:
                return {
                    "success": False,
                    "message": "Nessun sintomo trovato per l'analisi."
                }

            # Analyze trends
            trends = self._calculate_trends(symptoms)

            # Generate insights
            insights = self._generate_trend_insights(trends, symptom_type)

            return {
                "success": True,
                "period_days": days,
                "symptom_type": symptom_type or "all",
                "total_entries": len(symptoms),
                "trends": trends,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {
                "success": False,
                "message": f"Errore nell'analisi: {str(e)}"
            }

    def identify_recurring_patterns(
        self,
        min_occurrences: int = 2
    ) -> Dict[str, Any]:
        """
        Identifica pattern ricorrenti nei dati.

        Args:
            min_occurrences: Numero minimo di occorrenze per considerare un pattern

        Returns:
            Dizionario con pattern ricorrenti
        """
        try:
            # Get last 6 months of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)

            symptoms = self.db.get_symptoms(
                limit=1000,
                start_date=start_date,
                end_date=end_date
            )

            cycles = self.db.get_cycles(
                limit=12,
                start_date=start_date,
                end_date=end_date
            )

            if not symptoms:
                return {
                    "success": False,
                    "message": "Dati insufficienti per identificare pattern."
                }

            # Find patterns
            patterns = self._find_recurring_patterns(
                symptoms,
                cycles,
                min_occurrences
            )

            # Generate insights
            insights = self._generate_pattern_insights(patterns)

            return {
                "success": True,
                "min_occurrences": min_occurrences,
                "patterns_found": len(patterns),
                "patterns": patterns,
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Error identifying patterns: {e}")
            return {
                "success": False,
                "message": f"Errore nell'identificazione pattern: {str(e)}"
            }

    def _find_symptom_cycle_patterns(
        self,
        symptoms: List[Dict],
        cycles: List[Dict]
    ) -> Dict[str, Any]:
        """
        Trova correlazioni tra sintomi e fasi del ciclo.

        Args:
            symptoms: Lista sintomi
            cycles: Lista cicli

        Returns:
            Dizionario con correlazioni
        """
        # Convert to pandas for easier analysis
        if not cycles:
            return {"phase_distribution": {}, "symptom_intensity_by_phase": {}}

        # For each symptom, determine cycle phase
        phase_symptoms = defaultdict(list)

        for symptom in symptoms:
            symptom_date = datetime.fromisoformat(symptom['timestamp'])

            # Find which cycle phase this symptom belongs to
            phase = self._determine_cycle_phase(symptom_date, cycles)

            if phase:
                phase_symptoms[phase].append({
                    "type": symptom['symptom_type'],
                    "intensity": symptom['intensity']
                })

        # Calculate statistics per phase
        phase_distribution = {}
        symptom_intensity_by_phase = {}

        for phase, symptoms_list in phase_symptoms.items():
            phase_distribution[phase] = len(symptoms_list)

            # Group by symptom type
            symptom_types = defaultdict(list)
            for s in symptoms_list:
                symptom_types[s['type']].append(s['intensity'])

            # Calculate average intensity per symptom type
            symptom_intensity_by_phase[phase] = {
                stype: round(sum(intensities) / len(intensities), 1)
                for stype, intensities in symptom_types.items()
            }

        return {
            "phase_distribution": phase_distribution,
            "symptom_intensity_by_phase": symptom_intensity_by_phase
        }

    def _determine_cycle_phase(
        self,
        date: datetime,
        cycles: List[Dict]
    ) -> Optional[str]:
        """
        Determina la fase del ciclo per una data specifica.

        Fasi:
        - early: primi 1-5 giorni del ciclo (mestruazione)
        - mid: giorni 6-14 (fase follicolare/ovulazione)
        - late: giorni 15+ (fase luteale)
        - pre_menstrual: 2-3 giorni prima del prossimo ciclo

        Args:
            date: Data da verificare
            cycles: Lista cicli

        Returns:
            Fase del ciclo o None
        """
        for cycle in cycles:
            start_date = datetime.fromisoformat(cycle['start_date'])

            # Find next cycle start (if exists)
            next_cycle_start = None
            for next_cycle in cycles:
                next_start = datetime.fromisoformat(next_cycle['start_date'])
                if next_start > start_date:
                    if next_cycle_start is None or next_start < next_cycle_start:
                        next_cycle_start = next_start

            # If date is during this cycle
            if date >= start_date:
                if next_cycle_start and date < next_cycle_start:
                    days_from_start = (date - start_date).days

                    if days_from_start <= 5:
                        return "early"  # Menstruation
                    elif days_from_start <= 14:
                        return "mid"  # Follicular/Ovulation
                    else:
                        # Check if pre-menstrual
                        days_to_next = (next_cycle_start - date).days
                        if days_to_next <= 3:
                            return "pre_menstrual"
                        else:
                            return "late"  # Luteal

                elif not next_cycle_start:
                    # Last cycle, can't determine post phases accurately
                    days_from_start = (date - start_date).days
                    if days_from_start <= 5:
                        return "early"
                    elif days_from_start <= 14:
                        return "mid"
                    else:
                        return "late"

        return None

    def _calculate_trends(self, symptoms: List[Dict]) -> Dict[str, Any]:
        """Calcola trend temporali"""
        if not symptoms:
            return {}

        # Group by symptom type
        symptom_groups = defaultdict(list)
        for s in symptoms:
            symptom_groups[s['symptom_type']].append({
                "date": datetime.fromisoformat(s['timestamp']),
                "intensity": s['intensity']
            })

        trends = {}
        for stype, entries in symptom_groups.items():
            # Sort by date
            entries_sorted = sorted(entries, key=lambda x: x['date'])

            # Calculate if increasing/decreasing trend
            if len(entries_sorted) >= 3:
                intensities = [e['intensity'] for e in entries_sorted]

                # Simple linear regression slope
                x = np.arange(len(intensities))
                y = np.array(intensities)
                slope = np.polyfit(x, y, 1)[0]

                if slope > 0.1:
                    trend = "increasing"
                elif slope < -0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"

                trends[stype] = {
                    "count": len(entries_sorted),
                    "avg_intensity": round(sum(intensities) / len(intensities), 1),
                    "trend": trend,
                    "slope": round(float(slope), 2)
                }

        return trends

    def _find_recurring_patterns(
        self,
        symptoms: List[Dict],
        cycles: List[Dict],
        min_occurrences: int
    ) -> List[Dict[str, Any]]:
        """Identifica pattern ricorrenti"""
        patterns = []

        if not cycles:
            return patterns

        # Pattern 1: Sintomi che si ripetono in stessa fase ciclo
        phase_patterns = defaultdict(lambda: defaultdict(int))

        for symptom in symptoms:
            symptom_date = datetime.fromisoformat(symptom['timestamp'])
            phase = self._determine_cycle_phase(symptom_date, cycles)

            if phase:
                stype = symptom['symptom_type']
                phase_patterns[stype][phase] += 1

        # Convert to pattern list
        for stype, phases in phase_patterns.items():
            for phase, count in phases.items():
                if count >= min_occurrences:
                    patterns.append({
                        "type": "cycle_phase_recurrence",
                        "symptom": stype,
                        "phase": phase,
                        "occurrences": count,
                        "description": f"{stype} ricorre {count} volte in fase {phase}"
                    })

        # Pattern 2: Combinazioni di sintomi
        # (simplified - look for symptoms on same day)
        symptom_combos = defaultdict(int)
        symptoms_by_date = defaultdict(list)

        for symptom in symptoms:
            date_key = symptom['timestamp'][:10]  # YYYY-MM-DD
            symptoms_by_date[date_key].append(symptom['symptom_type'])

        for date, stypes in symptoms_by_date.items():
            if len(stypes) >= 2:
                combo = tuple(sorted(set(stypes)))
                symptom_combos[combo] += 1

        for combo, count in symptom_combos.items():
            if count >= min_occurrences:
                patterns.append({
                    "type": "symptom_combination",
                    "symptoms": list(combo),
                    "occurrences": count,
                    "description": f"Combinazione {', '.join(combo)} si ripete {count} volte"
                })

        return patterns

    def _generate_correlation_insights(self, correlations: Dict) -> List[str]:
        """Genera insights dalle correlazioni"""
        insights = []

        phase_dist = correlations.get("phase_distribution", {})
        intensity_by_phase = correlations.get("symptom_intensity_by_phase", {})

        if not phase_dist:
            insights.append("📊 Dati insufficienti per identificare correlazioni ciclo-sintomi.")
            return insights

        # Most symptomatic phase
        if phase_dist:
            max_phase = max(phase_dist, key=phase_dist.get)
            phase_names = {
                "early": "mestruazione (giorni 1-5)",
                "mid": "fase follicolare/ovulazione (giorni 6-14)",
                "late": "fase luteale (giorni 15+)",
                "pre_menstrual": "pre-mestruale (2-3 giorni prima)"
            }

            insights.append(
                f"📈 La fase del ciclo con più sintomi è: {phase_names.get(max_phase, max_phase)} "
                f"({phase_dist[max_phase]} sintomi registrati)"
            )

        # High intensity phases
        for phase, symptoms_dict in intensity_by_phase.items():
            for symptom, avg_intensity in symptoms_dict.items():
                if avg_intensity >= 7:
                    insights.append(
                        f"⚠️ {symptom} ha intensità alta (media {avg_intensity}/10) "
                        f"durante fase {phase_names.get(phase, phase)}"
                    )

        return insights

    def _generate_trend_insights(
        self,
        trends: Dict,
        symptom_type: Optional[str]
    ) -> List[str]:
        """Genera insights dai trend"""
        insights = []

        if not trends:
            insights.append("📊 Nessun trend significativo identificato.")
            return insights

        for stype, data in trends.items():
            if data['trend'] == "increasing":
                insights.append(
                    f"📈 {stype}: trend in aumento (intensità media {data['avg_intensity']}/10)"
                )
            elif data['trend'] == "decreasing":
                insights.append(
                    f"📉 {stype}: trend in diminuzione (intensità media {data['avg_intensity']}/10) - ottimo!"
                )
            else:
                insights.append(
                    f"➡️ {stype}: stabile (intensità media {data['avg_intensity']}/10)"
                )

        return insights

    def _generate_pattern_insights(self, patterns: List[Dict]) -> List[str]:
        """Genera insights dai pattern ricorrenti"""
        insights = []

        if not patterns:
            insights.append("📊 Nessun pattern ricorrente significativo identificato.")
            return insights

        for pattern in patterns:
            if pattern['type'] == "cycle_phase_recurrence":
                insights.append(
                    f"🔄 Pattern identificato: {pattern['description']}"
                )
            elif pattern['type'] == "symptom_combination":
                insights.append(
                    f"🔗 Pattern combinazione: {pattern['description']}"
                )

        return insights
