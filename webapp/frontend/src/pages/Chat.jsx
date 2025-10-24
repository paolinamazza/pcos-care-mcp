import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { sendChatMessage } from '../services/api';
import './Chat.css';

const CATEGORIES = [
  { value: null, label: '🌟 Tutte', color: '#6366f1' },
  { value: 'guidelines', label: '📋 Linee Guida', color: '#3b82f6' },
  { value: 'nutrition', label: '🥗 Nutrizione', color: '#10b981' },
  { value: 'exercise', label: '💪 Esercizio', color: '#f59e0b' },
  { value: 'mental_health', label: '🧘 Salute Mentale', color: '#ec4899' },
  { value: 'clinical', label: '⚕️ Clinica', color: '#8b5cf6' },
];

const SUGGESTED_QUESTIONS = [
  "Quali sono i criteri diagnostici per la PCOS?",
  "Come posso gestire l'aumento di peso con la PCOS?",
  "Che tipo di esercizio fisico è migliore per la PCOS?",
  "La PCOS influisce sulla salute mentale?",
  "Quali sono le opzioni di trattamento per la PCOS?"
];

function Chat() {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [useRAG, setUseRAG] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: `Ciao ${user?.full_name || user?.username}! 👋

Sono il tuo assistente AI personalizzato per la PCOS. Posso aiutarti con:

🔬 Informazioni mediche evidence-based
🥗 Consigli su nutrizione e dieta
💪 Suggerimenti per l'esercizio fisico
🧘 Supporto per la salute mentale
💊 Informazioni su trattamenti e terapie

**Come funziono:**
- Ho accesso a 28 ricerche scientifiche sulla PCOS (8,978 chunks di informazioni!)
- Posso filtrare per categoria specifica
- Mantengo la conversazione per darti risposte contestuali

Fai pure la tua domanda! 💬`,
        timestamp: new Date()
      }]);
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    // Check if user has API keys
    if (!user?.has_anthropic_key && !user?.has_openai_key) {
      alert('Devi configurare almeno una API key (Anthropic o OpenAI) nelle Impostazioni per usare il chatbot!');
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Prepare conversation history (exclude timestamps for API)
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await sendChatMessage(token, {
        message: inputMessage,
        conversation_history: conversationHistory,
        use_rag: useRAG,
        category_filter: categoryFilter
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        model: response.model,
        provider: response.provider,
        used_rag: response.used_rag
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ **Errore**: ${error.response?.data?.detail || 'Si è verificato un errore. Riprova.'}`,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSuggestedQuestion = (question) => {
    setInputMessage(question);
    inputRef.current?.focus();
  };

  const clearChat = () => {
    if (confirm('Vuoi davvero cancellare tutta la conversazione?')) {
      setMessages([]);
    }
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-title">
            <h2>💬 PCOS Care AI Chat</h2>
            <span className="chat-subtitle">
              {user?.has_anthropic_key ? '🤖 Claude' : user?.has_openai_key ? '🤖 GPT' : '⚠️ No API Key'}
              {useRAG && ' + 📚 RAG'}
            </span>
          </div>
          <div className="chat-actions">
            <button onClick={clearChat} className="btn btn-outline btn-sm">
              🗑️ Pulisci
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="chat-filters">
          <label className="filter-toggle">
            <input
              type="checkbox"
              checked={useRAG}
              onChange={(e) => setUseRAG(e.target.checked)}
            />
            <span>📚 Usa Knowledge Base (RAG)</span>
          </label>

          {useRAG && (
            <div className="category-filters">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat.value || 'all'}
                  onClick={() => setCategoryFilter(cat.value)}
                  className={`category-btn ${categoryFilter === cat.value ? 'active' : ''}`}
                  style={{
                    borderColor: categoryFilter === cat.value ? cat.color : 'transparent',
                    color: categoryFilter === cat.value ? cat.color : 'inherit'
                  }}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}
          >
            <div className="message-avatar">
              {msg.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div className="message-text">
                {msg.content.split('\n').map((line, i) => (
                  <React.Fragment key={i}>
                    {formatMessage(line)}
                    {i < msg.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
              <div className="message-meta">
                {msg.timestamp?.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                {msg.model && ` · ${msg.provider}`}
                {msg.used_rag && ' · 📚 RAG'}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant loading-message">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (show only when no messages or just welcome) */}
      {messages.length <= 1 && !loading && (
        <div className="suggested-questions-chat">
          <p>💡 <strong>Domande suggerite:</strong></p>
          <div className="suggestions-list">
            {SUGGESTED_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSuggestedQuestion(q)}
                className="suggestion-chip"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Scrivi la tua domanda sulla PCOS..."
            rows={1}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || loading}
            className="send-btn"
          >
            {loading ? '⏳' : '📤'}
          </button>
        </div>
        <div className="input-hint">
          <kbd>Enter</kbd> per inviare · <kbd>Shift+Enter</kbd> per andare a capo
        </div>
      </form>
    </div>
  );
}

// Helper to format message text (basic markdown-like)
function formatMessage(text) {
  // Bold
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Code
  text = text.replace(/`(.*?)`/g, '<code>$1</code>');

  return <span dangerouslySetInnerHTML={{ __html: text }} />;
}

export default Chat;
