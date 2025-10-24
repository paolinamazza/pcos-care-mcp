import React, { useState, useEffect } from 'react';
import { getHealth, getSymptomSummary, getCycles, getKnowledgeStats } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [healthStatus, setHealthStatus] = useState(null);
  const [symptomSummary, setSymptomSummary] = useState(null);
  const [recentCycles, setRecentCycles] = useState(null);
  const [ragStats, setRagStats] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [health, symptoms, cycles, stats] = await Promise.all([
        getHealth(),
        getSymptomSummary(30),
        getCycles(3),
        getKnowledgeStats()
      ]);

      setHealthStatus(health);
      setSymptomSummary(symptoms);
      setRecentCycles(cycles);
      setRagStats(stats);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <p>Caricamento dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Panoramica completa del tuo monitoraggio PCOS</p>
      </div>

      {/* System Status */}
      <div className="dashboard-grid">
        <div className="card status-card">
          <div className="card-header">
            <h3 className="card-title">Stato Sistema</h3>
          </div>
          <div className="status-items">
            <div className="status-item">
              <span className="status-label">Database</span>
              <span className={`badge ${healthStatus?.database === 'connected' ? 'badge-success' : 'badge-error'}`}>
                {healthStatus?.database || 'Unknown'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">RAG System</span>
              <span className={`badge ${healthStatus?.rag?.available ? 'badge-success' : 'badge-warning'}`}>
                {healthStatus?.rag?.available ? 'Disponibile' : 'Non disponibile'}
              </span>
            </div>
            {ragStats?.pdf_rag && (
              <div className="status-item">
                <span className="status-label">Knowledge Base</span>
                <span className="badge badge-info">
                  {ragStats.pdf_rag.total_chunks?.toLocaleString()} chunks
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Symptom Summary */}
        <div className="card summary-card">
          <div className="card-header">
            <h3 className="card-title">Sintomi - Ultimi 30 giorni</h3>
          </div>
          {symptomSummary?.success ? (
            <div className="summary-stats">
              <div className="stat-item">
                <div className="stat-value">{symptomSummary.total_symptoms || 0}</div>
                <div className="stat-label">Totale sintomi registrati</div>
              </div>
              {symptomSummary.by_type && Object.keys(symptomSummary.by_type).length > 0 && (
                <div className="symptom-types">
                  <h4>Per tipologia:</h4>
                  <ul>
                    {Object.entries(symptomSummary.by_type).map(([type, count]) => (
                      <li key={type}>
                        <span className="type-name">{type}</span>
                        <span className="badge badge-primary">{count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted">Nessun sintomo registrato negli ultimi 30 giorni</p>
          )}
        </div>

        {/* Recent Cycles */}
        <div className="card cycles-card">
          <div className="card-header">
            <h3 className="card-title">Ultimi Cicli</h3>
          </div>
          {recentCycles?.success && recentCycles?.cycles?.length > 0 ? (
            <div className="cycles-list">
              {recentCycles.cycles.slice(0, 3).map((cycle, index) => (
                <div key={cycle.id || index} className="cycle-item">
                  <div className="cycle-dates">
                    <strong>{new Date(cycle.start_date).toLocaleDateString('it-IT')}</strong>
                    {cycle.end_date && (
                      <span> - {new Date(cycle.end_date).toLocaleDateString('it-IT')}</span>
                    )}
                  </div>
                  <div className="cycle-meta">
                    {cycle.length_days && <span className="badge badge-info">{cycle.length_days} giorni</span>}
                    <span className="badge">{cycle.flow_intensity || 'N/A'}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">Nessun ciclo registrato</p>
          )}
        </div>

        {/* Knowledge Base Info */}
        {ragStats?.pdf_rag && (
          <div className="card knowledge-card">
            <div className="card-header">
              <h3 className="card-title">Knowledge Base</h3>
            </div>
            <div className="knowledge-stats">
              <p className="stat-highlight">
                {ragStats.pdf_rag.total_chunks?.toLocaleString()} chunks da PDF reali
              </p>
              {ragStats.pdf_rag.categories && (
                <div className="categories-list">
                  <h4>Categorie disponibili:</h4>
                  <div className="categories-grid">
                    {Object.entries(ragStats.pdf_rag.categories).map(([category, stats]) => (
                      <div key={category} className="category-badge">
                        <span className="category-name">{category}</span>
                        <span className="category-count">{stats.count} chunks</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card quick-actions-card">
        <div className="card-header">
          <h3 className="card-title">Azioni Rapide</h3>
        </div>
        <div className="quick-actions">
          <a href="/symptoms" className="action-button btn btn-primary">
            📝 Registra Sintomo
          </a>
          <a href="/cycles" className="action-button btn btn-primary">
            🩸 Registra Ciclo
          </a>
          <a href="/analytics" className="action-button btn btn-secondary">
            📊 Visualizza Analytics
          </a>
          <a href="/knowledge" className="action-button btn btn-secondary">
            🧠 Consulta Knowledge Base
          </a>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
