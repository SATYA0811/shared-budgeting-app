import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './components/auth/AuthPage';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import TransactionsNew from './pages/TransactionsNew';
import Analytics from './pages/Analytics';
import Goals from './pages/Goals';
import Banks from './pages/Banks';
import Partners from './pages/Partners';

// Main App Content (authenticated vs unauthenticated)
function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  // Show loading spinner during initialization
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication page for unauthenticated users
  if (!isAuthenticated) {
    return <AuthPage />;
  }

  // Show main application with routing for authenticated users
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transactions" element={<TransactionsNew />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/goals" element={<Goals />} />
        <Route path="/banks" element={<Banks />} />
        <Route path="/partners" element={<Partners />} />
      </Routes>
    </Layout>
  );
}

// Root App Component
export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}
