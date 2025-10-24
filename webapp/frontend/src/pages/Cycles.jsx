import React, { useState, useEffect } from 'react';
import { createCycle, getCycles, getCycleAnalytics } from '../services/api';
import { format } from 'date-fns';

function Cycles() {
  const [formData, setFormData] = useState({
    start_date: format(new Date(), 'yyyy-MM-dd'),
    flow_intensity: 'medium',
    notes: ''
  });
  const [cycles, setCycles] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [cyclesData, analyticsData] = await Promise.all([
        getCycles(12),
        getCycleAnalytics(6)
      ]);
      if (cyclesData.success) setCycles(cyclesData.cycles || []);
      if (analyticsData.success) setAnalytics(analyticsData);
    } catch (err) {
      console.error('Error loading cycles:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await createCycle(formData);
      if (result.success) {
        setSuccess('Ciclo registrato con successo!');
        setFormData({
          start_date: format(new Date(), 'yyyy-MM-dd'),
          flow_intensity: 'medium',
          notes: ''
        });
        loadData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante il salvataggio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Tracciamento Cicli</h1>
        <p className="page-subtitle">Monitora i tuoi cicli mestruali</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Registra Nuovo Ciclo</h3>
          </div>

          {success && <div className="alert alert-success">{success}</div>}
          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <div className="form-group">
              <label htmlFor="start_date">Data Inizio</label>
              <input
                type="date"
                id="start_date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="flow_intensity">Intensità Flusso</label>
              <select
                id="flow_intensity"
                value={formData.flow_intensity}
                onChange={(e) => setFormData({ ...formData, flow_intensity: e.target.value })}
                disabled={loading}
              >
                <option value="light">Leggero</option>
                <option value="medium">Medio</option>
                <option value="heavy">Abbondante</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="notes">Note</label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Salvataggio...' : '🩸 Registra Ciclo'}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Analytics Cicli (ultimi 6 mesi)</h3>
          </div>

          {analytics && (
            <div className="flex flex-col gap-2">
              <div style={{padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)'}}>
                <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--primary-color)'}}>
                  {analytics.average_length_days || 'N/A'}
                </div>
                <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                  Durata media (giorni)
                </div>
              </div>
              <div style={{padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)'}}>
                <div style={{fontSize: '2rem', fontWeight: 700, color: 'var(--primary-color)'}}>
                  {analytics.regularity_score || 'N/A'}
                </div>
                <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                  Score di regolarità
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h3 className="card-title">Storico Cicli</h3>
        </div>

        {cycles.length === 0 ? (
          <p className="text-muted">Nessun ciclo registrato</p>
        ) : (
          <div style={{display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)'}}>
            {cycles.map((cycle, index) => (
              <div key={cycle.id || index} style={{padding: 'var(--spacing-md)', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--secondary-color)'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--spacing-sm)'}}>
                  <strong>{new Date(cycle.start_date).toLocaleDateString('it-IT')}</strong>
                  {cycle.length_days && <span className="badge badge-info">{cycle.length_days} giorni</span>}
                </div>
                <div style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                  Intensità: {cycle.flow_intensity}
                </div>
                {cycle.notes && (
                  <div style={{marginTop: 'var(--spacing-sm)', fontSize: '0.875rem', color: 'var(--text-secondary)'}}>
                    {cycle.notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Cycles;
