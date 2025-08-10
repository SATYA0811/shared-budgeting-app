import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './components/auth/AuthPage';
import DashboardMockup from './components/DashboardMockup';

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

  // Show main dashboard for authenticated users
  return <DashboardMockup />;
}

// Root App Component
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
