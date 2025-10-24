import React, { useState, useEffect } from 'react';
import { createSymptom, getSymptoms } from '../services/api';
import './Symptoms.css';

const SYMPTOM_TYPES = [
  'acne',
  'hirsutism',
  'hair_loss',
  'weight_gain',
  'mood_swings',
  'fatigue',
  'sleep_issues',
  'irregular_periods',
  'pelvic_pain',
  'headaches',
  'other'
];

function Symptoms() {
  const [formData, setFormData] = useState({
    symptom_type: 'acne',
    intensity: 5,
    notes: ''
  });
  const [symptoms, setSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadSymptoms();
  }, []);

  const loadSymptoms = async () => {
    try {
      const data = await getSymptoms(20);
      if (data.success) {
        setSymptoms(data.symptoms || []);
      }
    } catch (err) {
      console.error('Error loading symptoms:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await createSymptom({
        symptom_type: formData.symptom_type,
        intensity: parseInt(formData.intensity),
        notes: formData.notes
      });

      if (result.success) {
        setSuccess('Sintomo registrato con successo!');
        setFormData({ symptom_type: 'acne', intensity: 5, notes: '' });
        loadSymptoms();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante il salvataggio');
    } finally {
      setLoading(false);
    }
  };

  const getIntensityColor = (intensity) => {
    if (intensity <= 3) return 'low';
    if (intensity <= 7) return 'medium';
    return 'high';
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Tracciamento Sintomi</h1>
        <p className="page-subtitle">Registra e monitora i tuoi sintomi PCOS</p>
      </div>

      <div className="symptoms-layout">
        {/* Form Card */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Registra Nuovo Sintomo</h3>
          </div>

          {success && <div className="alert alert-success">{success}</div>}
          {error && <div className="alert alert-error">{error}</div>}

          <form onSubmit={handleSubmit} className="symptom-form">
            <div className="form-group">
              <label htmlFor="symptom_type">Tipo di Sintomo</label>
              <select
                id="symptom_type"
                value={formData.symptom_type}
                onChange={(e) => setFormData({ ...formData, symptom_type: e.target.value })}
                disabled={loading}
              >
                {SYMPTOM_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type.replace('_', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="intensity">
                Intensità: {formData.intensity}/10
              </label>
              <input
                type="range"
                id="intensity"
                min="1"
                max="10"
                value={formData.intensity}
                onChange={(e) => setFormData({ ...formData, intensity: e.target.value })}
                className={`intensity-slider ${getIntensityColor(formData.intensity)}`}
                disabled={loading}
              />
              <div className="intensity-labels">
                <span>Leggero</span>
                <span>Moderato</span>
                <span>Grave</span>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="notes">Note (opzionale)</label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Aggiungi dettagli aggiuntivi..."
                rows={3}
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Salvataggio...' : '📝 Registra Sintomo'}
            </button>
          </form>
        </div>

        {/* Recent Symptoms */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Ultimi Sintomi Registrati</h3>
          </div>

          {symptoms.length === 0 ? (
            <p className="text-muted">Nessun sintomo registrato</p>
          ) : (
            <div className="symptoms-list">
              {symptoms.map((symptom, index) => (
                <div key={symptom.id || index} className="symptom-item">
                  <div className="symptom-header">
                    <div className="symptom-type">
                      <strong>{symptom.symptom_type?.replace('_', ' ').toUpperCase()}</strong>
                      <span className="symptom-date">
                        {new Date(symptom.timestamp).toLocaleString('it-IT')}
                      </span>
                    </div>
                    <span className={`intensity-badge ${getIntensityColor(symptom.intensity)}`}>
                      {symptom.intensity}/10
                    </span>
                  </div>
                  {symptom.notes && (
                    <div className="symptom-notes">
                      {symptom.notes}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Symptoms;
