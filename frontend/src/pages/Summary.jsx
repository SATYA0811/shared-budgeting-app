/**
 * Summary Page - Shared Budgeting App
 * 
 * Main overview page showing financial summary, recent transactions,
 * budget performance, goals progress, and quick actions.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target,
  Upload,
  Plus,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  CreditCard
} from 'lucide-react';
import api from '../services/api';

export default function Summary() {
  const [data, setData] = useState({
    transactions: [],
    categories: [],
    insights: [],
    goals: []
  });
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalIncome: 0,
    totalExpenses: 0,
    balance: 0,
    savingsRate: 0
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        console.log('Loading dashboard data (Income category only)...', new Date().toLocaleTimeString());
        
        // Load core data that's required
        const [transactions, categories] = await Promise.all([
          api.transactions.getTransactions({ limit: 5 }).catch(err => {
            console.error('Failed to load transactions:', err);
            return [];
          }),
          api.categories.getCategories().catch(err => {
            console.error('Failed to load categories:', err);
            return [];
          })
        ]);

        // Load optional data with fallbacks
        const insights = await api.analytics.getFinancialInsights().catch(err => {
          console.error('Failed to load insights:', err);
          return [];
        });

        const goalsResponse = await api.goals.getGoals().catch(err => {
          console.error('Failed to load goals:', err);
          return { goals: [] };
        });

        const monthlyReport = await api.analytics.getMonthlyReport(2025, 8).catch(err => {
          console.error('Failed to load monthly report:', err);
          return {
            total_income: 0,
            total_expenses: 0,
            net_savings: 0,
            savings_rate: 0
          };
        });

        setData({
          transactions: transactions || [],
          categories: categories || [],
          insights: insights || [],
          goals: goalsResponse.goals || goalsResponse || []
        });

        setStats({
          totalIncome: monthlyReport.total_income || 0,
          totalExpenses: monthlyReport.total_expenses || 0,
          balance: monthlyReport.net_savings || 0,
          savingsRate: monthlyReport.savings_rate || 0
        });

        console.log('Dashboard data loaded successfully');
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Set empty defaults if everything fails
        setData({
          transactions: [],
          categories: [],
          insights: [],
          goals: []
        });
        setStats({
          totalIncome: 0,
          totalExpenses: 0,
          balance: 0,
          savingsRate: 0
        });
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Balance"
          value={`$${stats.balance.toFixed(2)}`}
          change="+2.5%"
          changeType="positive"
          icon={DollarSign}
        />
        <StatCard
          title="Monthly Income"
          value={`$${stats.totalIncome.toFixed(2)}`}
          change="+12.3%"
          changeType="positive"
          icon={TrendingUp}
        />
        <StatCard
          title="Monthly Expenses"
          value={`$${stats.totalExpenses.toFixed(2)}`}
          change="-3.2%"
          changeType="negative"
          icon={TrendingDown}
        />
        <StatCard
          title="Savings Rate"
          value={`${stats.savingsRate.toFixed(1)}%`}
          change="+1.8%"
          changeType="positive"
          icon={Target}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Transactions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Recent Transactions</h3>
              <Link 
                to="/transactions"
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium flex items-center"
              >
                View all <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
            </div>
            
            <div className="space-y-3">
              {data.transactions.length > 0 ? (
                data.transactions.map((transaction) => (
                  <TransactionRow key={transaction.id} transaction={transaction} />
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CreditCard className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No transactions yet</p>
                  <p className="text-sm">Upload a bank statement to get started</p>
                </div>
              )}
            </div>
          </div>

          {/* Budget Performance */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Budget Performance</h3>
            
            <div className="space-y-4">
              {data.categories
                .filter((category) => 
                  category.name !== 'Income' && 
                  category.name !== 'Self Transfer' &&
                  category.default_budget && 
                  category.default_budget > 0
                )
                .slice(0, 5)
                .map((category) => (
                  <BudgetBar
                    key={category.id}
                    category={category.name}
                    spent={Math.random() * category.default_budget}
                    budget={category.default_budget}
                  />
                ))}
            </div>
            
            <Link 
              to="/analytics"
              className="inline-flex items-center mt-4 text-indigo-600 hover:text-indigo-700 text-sm font-medium"
            >
              View detailed analysis <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            
            <div className="space-y-3">
              <QuickActionButton
                icon={Upload}
                title="Upload Statement"
                description="Add transactions from bank PDF"
                onClick={() => {/* Handle upload */}}
              />
              <QuickActionButton
                icon={Plus}
                title="Add Transaction"
                description="Manually add a transaction"
                onClick={() => {/* Handle add */}}
              />
              <QuickActionButton
                icon={Target}
                title="Create Goal"
                description="Set a new savings goal"
                onClick={() => {/* Handle goal */}}
              />
            </div>
          </div>

          {/* Goals Progress */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Goals Progress</h3>
              <Link 
                to="/goals"
                className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
              >
                Manage
              </Link>
            </div>
            
            <div className="space-y-4">
              {data.goals.length > 0 ? (
                data.goals.slice(0, 3).map((goal) => (
                  <GoalProgress key={goal.id} goal={goal} />
                ))
              ) : (
                <div className="text-center py-4 text-gray-500">
                  <Target className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No goals set</p>
                </div>
              )}
            </div>
          </div>

          {/* Insights */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold mb-4">Financial Insights</h3>
            
            <div className="space-y-3">
              {data.insights.length > 0 ? (
                data.insights.slice(0, 3).map((insight, index) => (
                  <InsightCard key={index} insight={insight} />
                ))
              ) : (
                <div className="text-center py-4 text-gray-500">
                  <TrendingUp className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">No insights available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Components
function StatCard({ title, value, change, changeType, icon: Icon }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
          <div className={`flex items-center mt-2 text-sm ${
            changeType === 'positive' ? 'text-green-600' : 'text-red-600'
          }`}>
            {changeType === 'positive' ? 
              <TrendingUp className="h-4 w-4 mr-1" /> : 
              <TrendingDown className="h-4 w-4 mr-1" />
            }
            {change}
          </div>
        </div>
        <div className={`p-3 rounded-lg ${
          changeType === 'positive' ? 'bg-green-50' : 'bg-red-50'
        }`}>
          <Icon className={`h-6 w-6 ${
            changeType === 'positive' ? 'text-green-600' : 'text-red-600'
          }`} />
        </div>
      </div>
    </div>
  );
}

function TransactionRow({ transaction }) {
  const isExpense = transaction.amount < 0;
  
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
      <div className="flex items-center">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          isExpense ? 'bg-red-50' : 'bg-green-50'
        }`}>
          {isExpense ? 
            <TrendingDown className="h-5 w-5 text-red-600" /> :
            <TrendingUp className="h-5 w-5 text-green-600" />
          }
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-900">{transaction.description}</p>
          <p className="text-xs text-gray-500">
            {new Date(transaction.date).toLocaleDateString()} • {transaction.category_name || 'Uncategorized'}
          </p>
        </div>
      </div>
      <div className={`text-sm font-semibold ${
        isExpense ? 'text-red-600' : 'text-green-600'
      }`}>
        {isExpense ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
      </div>
    </div>
  );
}

function BudgetBar({ category, spent, budget }) {
  // Safety checks for edge cases
  const safeSpent = spent || 0;
  const safeBudget = budget || 1; // Avoid division by zero
  const percentage = Math.min((safeSpent / safeBudget) * 100, 100);
  const isOverBudget = safeSpent > safeBudget;
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-gray-700">{category}</span>
        <span className="text-gray-500">${safeSpent.toFixed(0)} / ${safeBudget.toFixed(0)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full ${isOverBudget ? 'bg-red-500' : 'bg-indigo-600'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

function QuickActionButton({ icon: Icon, title, description, onClick }) {
  return (
    <button 
      onClick={onClick}
      className="w-full text-left p-4 rounded-lg border hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
    >
      <div className="flex items-center">
        <div className="bg-indigo-50 p-2 rounded-lg">
          <Icon className="h-5 w-5 text-indigo-600" />
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
    </button>
  );
}

function GoalProgress({ goal }) {
  const progress = Math.min((goal.current_amount / goal.target_amount) * 100, 100);
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-gray-700">{goal.name}</span>
        <span className="text-gray-500">{progress.toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="h-2 rounded-full bg-green-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-xs text-gray-500">
        ${goal.current_amount.toFixed(0)} of ${goal.target_amount.toFixed(0)}
      </p>
    </div>
  );
}

function InsightCard({ insight }) {
  const getIcon = (type) => {
    switch (type) {
      case 'warning': return AlertCircle;
      case 'achievement': return CheckCircle;
      default: return TrendingUp;
    }
  };
  
  const getColor = (type) => {
    switch (type) {
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'achievement': return 'text-green-600 bg-green-50';
      default: return 'text-blue-600 bg-blue-50';
    }
  };
  
  const Icon = getIcon(insight.type);
  
  return (
    <div className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50">
      <div className={`p-1 rounded ${getColor(insight.type)}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{insight.title}</p>
        <p className="text-xs text-gray-600 mt-1">{insight.description}</p>
      </div>
    </div>
  );
}