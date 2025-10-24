import React, { useState, useEffect } from 'react';
import { analyzeCorrelation, analyzeTrends, identifyPatterns } from '../services/api';

function Analytics() {
  const [correlation, setCorrelation] = useState(null);
  const [trends, setTrends] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const [corrData, trendsData, patternsData] = await Promise.all([
        analyzeCorrelation(3),
        analyzeTrends(null, 90),
        identifyPatterns(2)
      ]);

      if (corrData.success) setCorrelation(corrData);
      if (trendsData.success) setTrends(trendsData);
      if (patternsData.success) setPatterns(patternsData);
    } catch (err) {
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Caricamento analytics...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Analytics e Pattern</h1>
        <p className="page-subtitle">Analisi dei tuoi dati PCOS</p>
      </div>

      {/* Correlation */}
      {correlation && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📊 Correlazione Sintomi-Ciclo</h3>
            <p className="card-subtitle">Ultimi 3 mesi</p>
          </div>

          {correlation.correlations && correlation.correlations.length > 0 ? (
            <div style={{display: 'grid', gap: 'var(--spacing-md)'}}>
              {correlation.correlations.map((corr, index) => (
                <div key={index} style={{padding: 'var(--spacing-md)', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <strong>{corr.symptom_type}</strong>
                      <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                        {corr.phase} - Occorrenze: {corr.count}
                      </div>
                    </div>
                    <span className="badge badge-primary">{corr.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">Dati insufficienti per analisi correlazione</p>
          )}
        </div>
      )}

      {/* Trends */}
      {trends && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">📈 Trend Sintomi</h3>
            <p className="card-subtitle">Ultimi 90 giorni</p>
          </div>

          {trends.trends && Object.keys(trends.trends).length > 0 ? (
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--spacing-md)'}}>
              {Object.entries(trends.trends).map(([symptomType, data]) => (
                <div key={symptomType} style={{padding: 'var(--spacing-lg)', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)'}}>
                  <h4 style={{marginBottom: 'var(--spacing-md)'}}>{symptomType.replace('_', ' ').toUpperCase()}</h4>
                  <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--primary-color)', marginBottom: 'var(--spacing-sm)'}}>
                    {data.avg_intensity?.toFixed(1) || 'N/A'}
                  </div>
                  <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                    Intensità media ({data.count} occorrenze)
                  </div>
                  {data.trend && (
                    <div style={{marginTop: 'var(--spacing-sm)'}}>
                      <span className={`badge ${data.trend === 'increasing' ? 'badge-error' : data.trend === 'decreasing' ? 'badge-success' : 'badge-info'}`}>
                        {data.trend}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">Nessun dato disponibile per i trend</p>
          )}
        </div>
      )}

      {/* Patterns */}
      {patterns && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🔍 Pattern Ricorrenti</h3>
          </div>

          {patterns.patterns && patterns.patterns.length > 0 ? (
            <div style={{display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)'}}>
              {patterns.patterns.map((pattern, index) => (
                <div key={index} style={{padding: 'var(--spacing-lg)', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--info-color)'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)'}}>
                    <strong>{pattern.symptom_type?.replace('_', ' ').toUpperCase()}</strong>
                    <span className="badge badge-info">{pattern.occurrences} occorrenze</span>
                  </div>
                  {pattern.description && (
                    <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                      {pattern.description}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">Nessun pattern ricorrente identificato</p>
          )}
        </div>
      )}

      {!correlation && !trends && !patterns && (
        <div className="card">
          <p className="text-center text-muted">
            Non ci sono ancora dati sufficienti per generare analytics.
            <br />
            Continua a registrare sintomi e cicli per vedere le analisi qui.
          </p>
        </div>
      )}
    </div>
  );
}

export default Analytics;
