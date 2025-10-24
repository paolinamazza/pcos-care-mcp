import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { updateAPIKeys } from '../services/api';
import './Settings.css';

function Settings() {
  const { user, token, logout, updateUser } = useAuth();
  const [apiKeys, setApiKeys] = useState({
    anthropic_api_key: '',
    openai_api_key: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [showAnthropicKey, setShowAnthropicKey] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess('');
    setError('');

    try {
      const result = await updateAPIKeys(token, apiKeys);

      if (result.success) {
        setSuccess('API keys aggiornate con successo!');
        // Update user state
        updateUser({
          ...user,
          has_anthropic_key: result.has_anthropic_key,
          has_openai_key: result.has_openai_key
        });
        // Clear input fields
        setApiKeys({ anthropic_api_key: '', openai_api_key: '' });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Errore durante l\'aggiornamento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Impostazioni</h1>
        <p className="page-subtitle">Gestisci il tuo account e le API keys</p>
      </div>

      <div className="settings-grid">
        {/* User Info */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">👤 Informazioni Account</h3>
          </div>

          <div className="user-info">
            <div className="info-item">
              <span className="info-label">Email</span>
              <span className="info-value">{user?.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Username</span>
              <span className="info-value">{user?.username}</span>
            </div>
            {user?.full_name && (
              <div className="info-item">
                <span className="info-label">Nome</span>
                <span className="info-value">{user.full_name}</span>
              </div>
            )}
          </div>

          <button onClick={logout} className="btn btn-outline btn-block mt-3">
            🚪 Esci dall'account
          </button>
        </div>

        {/* API Keys */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">🔑 API Keys per Chatbot AI</h3>
            <p className="card-subtitle">Configura le tue API keys per usare il chatbot AI</p>
          </div>

          {success && <div className="alert alert-success">{success}</div>}
          {error && <div className="alert alert-error">{error}</div>}

          <div className="api-keys-status">
            <div className="status-item">
              <span className="status-label">Anthropic Claude</span>
              {user?.has_anthropic_key ? (
                <span className="badge badge-success">✓ Configurata</span>
              ) : (
                <span className="badge badge-warning">Non configurata</span>
              )}
            </div>
            <div className="status-item">
              <span className="status-label">OpenAI GPT</span>
              {user?.has_openai_key ? (
                <span className="badge badge-success">✓ Configurata</span>
              ) : (
                <span className="badge badge-warning">Non configurata</span>
              )}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="api-keys-form">
            <div className="form-group">
              <label htmlFor="anthropic_api_key">
                Anthropic API Key
                <a
                  href="https://console.anthropic.com/settings/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="help-link"
                >
                  Ottieni la tua key →
                </a>
              </label>
              <div className="key-input-wrapper">
                <input
                  type={showAnthropicKey ? 'text' : 'password'}
                  id="anthropic_api_key"
                  value={apiKeys.anthropic_api_key}
                  onChange={(e) => setApiKeys({ ...apiKeys, anthropic_api_key: e.target.value })}
                  placeholder="sk-ant-..."
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowAnthropicKey(!showAnthropicKey)}
                  className="toggle-visibility-btn"
                >
                  {showAnthropicKey ? '🙈' : '👁️'}
                </button>
              </div>
              <small className="form-hint">
                Lascia vuoto per mantenere la key esistente
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="openai_api_key">
                OpenAI API Key
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="help-link"
                >
                  Ottieni la tua key →
                </a>
              </label>
              <div className="key-input-wrapper">
                <input
                  type={showOpenAIKey ? 'text' : 'password'}
                  id="openai_api_key"
                  value={apiKeys.openai_api_key}
                  onChange={(e) => setApiKeys({ ...apiKeys, openai_api_key: e.target.value })}
                  placeholder="sk-..."
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                  className="toggle-visibility-btn"
                >
                  {showOpenAIKey ? '🙈' : '👁️'}
                </button>
              </div>
              <small className="form-hint">
                Lascia vuoto per mantenere la key esistente
              </small>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? 'Salvataggio...' : '💾 Salva API Keys'}
            </button>
          </form>

          <div className="info-box mt-3">
            <strong>ℹ️ Privacy e Sicurezza</strong>
            <p>
              Le tue API keys sono criptate e salvate in modo sicuro. Non vengono mai condivise con terzi.
              Vengono utilizzate solo per permetterti di usare il chatbot AI con il tuo account personale.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
