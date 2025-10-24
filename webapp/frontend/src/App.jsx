import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Symptoms from './pages/Symptoms';
import Cycles from './pages/Cycles';
import Analytics from './pages/Analytics';
import Chat from './pages/Chat';
import Settings from './pages/Settings';
import Knowledge from './pages/Knowledge';

import './App.css';

function AppContent() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <div className="app">
      {isAuthenticated && (
        <header className="app-header">
          <div className="container">
            <div className="header-content">
              <div className="logo">
                <h1>🌸 PCOS Care</h1>
                <span className="version">v2.0</span>
              </div>

              <nav className="main-nav">
                <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  Dashboard
                </NavLink>
                <NavLink to="/chat" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  💬 AI Chat
                </NavLink>
                <NavLink to="/symptoms" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  Sintomi
                </NavLink>
                <NavLink to="/cycles" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  Cicli
                </NavLink>
                <NavLink to="/analytics" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  Analytics
                </NavLink>
                <NavLink to="/knowledge" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                  Knowledge
                </NavLink>
              </nav>

              <div className="header-user">
                <NavLink to="/settings" className="user-btn">
                  <span className="user-avatar">
                    {user?.full_name?.[0] || user?.username?.[0] || '👤'}
                  </span>
                  <span className="user-name">{user?.username}</span>
                </NavLink>
                <button onClick={logout} className="btn btn-outline btn-sm logout-btn">
                  Esci
                </button>
              </div>
            </div>
          </div>
        </header>
      )}

      <main className={isAuthenticated ? "app-main" : "app-main-auth"}>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Login />
          } />
          <Route path="/register" element={
            isAuthenticated ? <Navigate to="/" replace /> : <Register />
          } />

          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/chat" element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          } />
          <Route path="/symptoms" element={
            <ProtectedRoute>
              <Symptoms />
            </ProtectedRoute>
          } />
          <Route path="/cycles" element={
            <ProtectedRoute>
              <Cycles />
            </ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          } />
          <Route path="/knowledge" element={
            <ProtectedRoute>
              <Knowledge />
            </ProtectedRoute>
          } />
          <Route path="/settings" element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {isAuthenticated && (
        <footer className="app-footer">
          <div className="container">
            <p>PCOS Care - Gestione personalizzata PCOS con AI Chatbot e RAG evidence-based</p>
            <p className="text-muted">Consulta sempre un medico per diagnosi e trattamenti</p>
          </div>
        </footer>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
