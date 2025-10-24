import React, { useState, useEffect } from 'react';
import { queryKnowledge, getKnowledgeStats } from '../services/api';
import './Knowledge.css';

const CATEGORIES = [
  { value: null, label: 'Tutte le categorie' },
  { value: 'guidelines', label: 'Linee Guida Cliniche' },
  { value: 'nutrition', label: 'Nutrizione' },
  { value: 'exercise', label: 'Esercizio Fisico' },
  { value: 'mental_health', label: 'Salute Mentale' },
  { value: 'clinical', label: 'Aspetti Clinici' },
  { value: 'future_directions', label: 'Direzioni Future' }
];

function Knowledge() {
  const [question, setQuestion] = useState('');
  const [category, setCategory] = useState(null);
  const [numSources, setNumSources] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getKnowledgeStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      setError('Inserisci una domanda');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await queryKnowledge(question, numSources, category);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante la ricerca. Verifica che il backend sia attivo.');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    "Quali sono i criteri di Rotterdam per la PCOS?",
    "Che ruolo ha l'esercizio fisico nella gestione della PCOS?",
    "Quali sono le migliori strategie nutrizionali per la PCOS?",
    "Come la PCOS influenza la salute mentale?",
    "Quali sono i trattamenti farmacologici per la PCOS?"
  ];

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Knowledge Base PCOS</h1>
        <p className="page-subtitle">
          Consulta la knowledge base basata su 28 PDF di ricerca scientifica
        </p>
      </div>

      {/* System Stats */}
      {stats?.pdf_rag && (
        <div className="card kb-stats-card">
          <div className="kb-stats">
            <div className="stat-badge">
              <div className="stat-icon">📚</div>
              <div className="stat-info">
                <div className="stat-value">{stats.pdf_rag.total_chunks?.toLocaleString()}</div>
                <div className="stat-label">Chunks disponibili</div>
              </div>
            </div>
            <div className="stat-badge">
              <div className="stat-icon">🏷️</div>
              <div className="stat-info">
                <div className="stat-value">{Object.keys(stats.pdf_rag.categories || {}).length}</div>
                <div className="stat-label">Categorie</div>
              </div>
            </div>
            <div className="stat-badge">
              <div className="stat-icon">✅</div>
              <div className="stat-info">
                <div className="stat-value">{stats.pdf_rag.status}</div>
                <div className="stat-label">Stato</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Query Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="kb-form">
          <div className="form-group">
            <label htmlFor="question">Fai una domanda sulla PCOS</label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Es: Quali sono i benefici dell'esercizio fisico per la PCOS?"
              rows={4}
              disabled={loading}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Filtra per categoria</label>
              <select
                id="category"
                value={category || ''}
                onChange={(e) => setCategory(e.target.value || null)}
                disabled={loading}
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.value || 'all'} value={cat.value || ''}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="numSources">Numero di fonti</label>
              <select
                id="numSources"
                value={numSources}
                onChange={(e) => setNumSources(parseInt(e.target.value))}
                disabled={loading}
              >
                <option value={3}>3 fonti</option>
                <option value={5}>5 fonti</option>
                <option value={7}>7 fonti</option>
                <option value={10}>10 fonti</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
            {loading ? '🔍 Ricerca in corso...' : '🔍 Cerca'}
          </button>
        </form>

        {/* Suggested Questions */}
        {!result && !loading && (
          <div className="suggested-questions">
            <h4>Domande suggerite:</h4>
            <div className="suggestions-grid">
              {suggestedQuestions.map((q, index) => (
                <button
                  key={index}
                  onClick={() => setQuestion(q)}
                  className="suggestion-btn"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-error">
          <strong>Errore:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && result.success && (
        <div className="card result-card">
          <div className="result-header">
            <h3>Risultati della ricerca</h3>
            <div className="result-meta">
              <span className="badge badge-info">
                Sistema: {result.system === 'pdf_rag' ? 'PDF RAG' : 'Legacy'}
              </span>
              {result.confidence && (
                <span className={`badge ${result.confidence > 0.7 ? 'badge-success' : result.confidence > 0.4 ? 'badge-warning' : 'badge-error'}`}>
                  Confidence: {Math.round(result.confidence * 100)}%
                </span>
              )}
              {result.total_chunks_found && (
                <span className="badge badge-primary">
                  {result.total_chunks_found} chunks trovati
                </span>
              )}
            </div>
          </div>

          {/* Context/Answer */}
          <div className="result-context">
            <h4>📝 Informazioni trovate:</h4>
            <div className="context-text">
              {result.context || result.answer}
            </div>
          </div>

          {/* Sources */}
          {result.sources && result.sources.length > 0 && (
            <div className="result-sources">
              <h4>📚 Fonti consultate ({result.sources.length}):</h4>
              <div className="sources-list">
                {result.sources.map((source, index) => (
                  <div key={index} className="source-item">
                    <div className="source-header">
                      <div className="source-title">
                        <strong>{index + 1}. {source.title}</strong>
                        <span className="badge badge-primary">{source.category}</span>
                      </div>
                      <div className="source-relevance">
                        {source.relevance_score && (
                          <span className={`relevance-badge ${source.relevance_score > 0.7 ? 'high' : source.relevance_score > 0.4 ? 'medium' : 'low'}`}>
                            Rilevanza: {Math.round(source.relevance_score * 100)}%
                          </span>
                        )}
                      </div>
                    </div>
                    {source.page && (
                      <div className="source-meta">
                        📄 Pagina: ~{source.page}
                      </div>
                    )}
                    {source.chunk_preview && (
                      <div className="source-preview">
                        <em>"{source.chunk_preview}"</em>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="disclaimer">
            💡 <strong>Importante:</strong> Queste informazioni sono estratte da ricerca scientifica e hanno scopo informativo.
            Consulta sempre un medico per diagnosi e trattamenti personalizzati.
          </div>
        </div>
      )}
    </div>
  );
}

export default Knowledge;
