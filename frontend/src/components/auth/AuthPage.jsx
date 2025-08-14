/**
 * Authentication Page - Shared Budgeting App
 * 
 * Landing page for unauthenticated users. Provides login and registration
 * forms with smooth transitions between them.
 */

import React, { useState } from 'react';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

export default function AuthPage({ onAuthSuccess }) {
  const [showLogin, setShowLogin] = useState(true);

  const handleAuthSuccess = () => {
    if (onAuthSuccess) {
      onAuthSuccess();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            💰 Shared Budgeting
          </h1>
          <p className="text-gray-600">
            Manage your finances together with your partner
          </p>
        </div>

        {/* Auth Forms */}
        <div className="transition-all duration-300 ease-in-out">
          {showLogin ? (
            <LoginForm
              onSuccess={handleAuthSuccess}
              onSwitchToRegister={() => setShowLogin(false)}
            />
          ) : (
            <RegisterForm
              onSuccess={handleAuthSuccess}
              onSwitchToLogin={() => setShowLogin(true)}
            />
          )}
        </div>

        {/* Features */}
        <div className="mt-12 bg-white/50 backdrop-blur-sm rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">
            Features
          </h3>
          <div className="grid grid-cols-1 gap-3 text-sm text-gray-700">
            <div className="flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Upload bank statements (PDF, CSV, Excel)
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Automatic transaction categorization
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Financial analytics and insights
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Goal tracking and budgeting
            </div>
            <div className="flex items-center">
              <span className="text-green-600 mr-2">✓</span>
              Multi-user household support
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}