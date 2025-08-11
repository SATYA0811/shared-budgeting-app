/**
 * Main Layout Component - Shared Budgeting App
 * 
 * Provides the main application layout with navigation sidebar,
 * header, and content area. Handles navigation between different
 * sections of the application.
 */

import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  CreditCard,
  TrendingUp,
  Target,
  Building2,
  Users,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';

const navigationItems = [
  {
    name: 'Dashboard',
    path: '/',
    icon: LayoutDashboard,
    description: 'Overview and summary'
  },
  {
    name: 'Transactions',
    path: '/transactions',
    icon: CreditCard,
    description: 'Manage all transactions'
  },
  {
    name: 'Analytics',
    path: '/analytics',
    icon: TrendingUp,
    description: 'Financial insights & charts'
  },
  {
    name: 'Goals',
    path: '/goals',
    icon: Target,
    description: 'Investment & saving goals'
  },
  {
    name: 'Banks & Files',
    path: '/banks',
    icon: Building2,
    description: 'Upload statements & manage accounts'
  },
  {
    name: 'Partners',
    path: '/partners',
    icon: Users,
    description: 'Shared household view'
  },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const currentPage = navigationItems.find(item => item.path === location.pathname);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">💰</span>
              </div>
              <span className="ml-3 text-xl font-semibold text-gray-900">Budget App</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <NavLink
                  key={item.name}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors
                    ${isActive
                      ? 'bg-indigo-50 text-indigo-700 border-r-2 border-indigo-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className={`h-5 w-5 mr-3 ${isActive ? 'text-indigo-700' : 'text-gray-400'}`} />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    <div className={`text-xs ${isActive ? 'text-indigo-600' : 'text-gray-500'}`}>
                      {item.description}
                    </div>
                  </div>
                </NavLink>
              );
            })}
          </nav>

          {/* User Profile & Logout */}
          <div className="border-t p-4">
            <div className="flex items-center mb-4">
              <img 
                src="https://avatars.dicebear.com/api/micah/user.svg" 
                alt="avatar" 
                className="w-10 h-10 rounded-full"
              />
              <div className="ml-3">
                <div className="text-sm font-medium text-gray-900">
                  {user?.user_email || user?.email || 'User'}
                </div>
                <div className="text-xs text-gray-500">Premium Plan</div>
              </div>
            </div>
            
            <div className="space-y-1">
              <button className="flex items-center w-full px-3 py-2 text-sm text-gray-700 rounded-md hover:bg-gray-50">
                <Settings className="h-4 w-4 mr-3 text-gray-400" />
                Settings
              </button>
              <button 
                onClick={logout}
                className="flex items-center w-full px-3 py-2 text-sm text-red-700 rounded-md hover:bg-red-50"
              >
                <LogOut className="h-4 w-4 mr-3 text-red-400" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
        {/* Header */}
        <header className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                <Menu className="h-5 w-5" />
              </button>
              
              <div className="ml-4 lg:ml-0">
                <h1 className="text-2xl font-semibold text-gray-900">
                  {currentPage?.name || 'Dashboard'}
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                  {currentPage?.description || 'Overview and summary'}
                </p>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">Balance</div>
                <div className="text-lg font-semibold text-green-600">$2,730.50</div>
              </div>
              
              <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
                Quick Add
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}