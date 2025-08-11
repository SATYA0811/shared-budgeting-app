/**
 * Partners Page - Shared Budgeting App
 * 
 * Combined view showing both partner and personal analytics,
 * shared expenses, budget comparisons, and household insights.
 */

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart3,
  Target,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  User,
  UserPlus,
  Settings,
  ArrowRightLeft,
  Wallet,
  CreditCard,
  Home,
  Car,
  Coffee,
  ShoppingBag,
  Utensils,
  Zap
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart as RechartsPieChart, 
  Pie,
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import api from '../services/api';

const COLORS = ['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function Partners() {
  const [data, setData] = useState({
    partners: [],
    sharedExpenses: [],
    individualSpending: [],
    monthlyComparison: [],
    categoryBreakdown: [],
    goals: []
  });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [selectedPartner, setSelectedPartner] = useState('all');

  useEffect(() => {
    loadData();
  }, [selectedPeriod]);

  const loadData = async () => {
    try {
      // Mock data - replace with actual API calls
      const partnersData = [
        { id: 1, name: 'Alex Johnson', email: 'alex@example.com', avatar: 'AJ', totalSpent: 2450.30, role: 'Partner' },
        { id: 2, name: 'You', email: 'you@example.com', avatar: 'YO', totalSpent: 1850.75, role: 'Owner' }
      ];

      const sharedExpensesData = [
        { id: 1, description: 'Groceries', amount: 150.00, date: '2025-08-10', paidBy: 'Alex Johnson', category: 'Food' },
        { id: 2, description: 'Utilities', amount: 280.50, date: '2025-08-09', paidBy: 'You', category: 'Home' },
        { id: 3, description: 'Internet Bill', amount: 89.99, date: '2025-08-08', paidBy: 'Alex Johnson', category: 'Home' },
        { id: 4, description: 'Dinner Out', amount: 85.30, date: '2025-08-07', paidBy: 'You', category: 'Food' }
      ];

      const monthlyComparisonData = [
        { month: 'Jan', you: 1200, partner: 1400, shared: 800 },
        { month: 'Feb', you: 1350, partner: 1250, shared: 750 },
        { month: 'Mar', you: 1180, partner: 1600, shared: 900 },
        { month: 'Apr', you: 1420, partner: 1380, shared: 850 },
        { month: 'May', you: 1250, partner: 1450, shared: 920 },
        { month: 'Jun', you: 1380, partner: 1320, shared: 880 },
        { month: 'Jul', you: 1450, partner: 1500, shared: 950 },
        { month: 'Aug', you: 1850, partner: 2450, shared: 1100 }
      ];

      const categoryBreakdownData = [
        { name: 'Food & Dining', you: 450, partner: 620, shared: 380, total: 1450 },
        { name: 'Home & Utilities', you: 280, partner: 340, shared: 450, total: 1070 },
        { name: 'Transportation', you: 320, partner: 480, shared: 120, total: 920 },
        { name: 'Shopping', you: 250, partner: 380, shared: 80, total: 710 },
        { name: 'Entertainment', you: 180, partner: 220, shared: 150, total: 550 },
        { name: 'Health', you: 120, partner: 160, shared: 0, total: 280 }
      ];

      setData({
        partners: partnersData,
        sharedExpenses: sharedExpensesData,
        monthlyComparison: monthlyComparisonData,
        categoryBreakdown: categoryBreakdownData,
        individualSpending: [],
        goals: []
      });
    } catch (error) {
      console.error('Error loading partner data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'comparison', name: 'Comparison', icon: TrendingUp },
    { id: 'shared', name: 'Shared Expenses', icon: ArrowRightLeft },
    { id: 'goals', name: 'Joint Goals', icon: Target }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Partners & Analytics</h2>
          <p className="text-gray-600">Shared household financial overview</p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button className="btn-secondary flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button className="btn-primary flex items-center gap-2">
            <UserPlus className="h-4 w-4" />
            Invite Partner
          </button>
        </div>
      </div>

      {/* Partners Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Household</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${(data.partners.reduce((sum, p) => sum + p.totalSpent, 0)).toFixed(2)}
              </p>
              <p className="text-sm text-green-600 mt-1">+12% from last month</p>
            </div>
            <div className="bg-indigo-50 p-3 rounded-lg">
              <Users className="h-6 w-6 text-indigo-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Shared Expenses</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${data.sharedExpenses.reduce((sum, exp) => sum + exp.amount, 0).toFixed(2)}
              </p>
              <p className="text-sm text-blue-600 mt-1">{data.sharedExpenses.length} transactions</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <ArrowRightLeft className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Your Spending</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${data.partners.find(p => p.role === 'Owner')?.totalSpent?.toFixed(2) || '0.00'}
              </p>
              <p className="text-sm text-orange-600 mt-1">75% of budget</p>
            </div>
            <div className="bg-orange-50 p-3 rounded-lg">
              <Wallet className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Partner Spending</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${data.partners.find(p => p.role === 'Partner')?.totalSpent?.toFixed(2) || '0.00'}
              </p>
              <p className="text-sm text-red-600 mt-1">95% of budget</p>
            </div>
            <div className="bg-red-50 p-3 rounded-lg">
              <User className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <>
            {/* Monthly Spending Trends */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Monthly Spending Trends</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.monthlyComparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value}`, '']} />
                    <Area 
                      type="monotone" 
                      dataKey="you" 
                      stackId="1" 
                      stroke="#4F46E5" 
                      fill="#4F46E5" 
                      fillOpacity={0.6}
                      name="Your Spending"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="partner" 
                      stackId="1" 
                      stroke="#06B6D4" 
                      fill="#06B6D4" 
                      fillOpacity={0.6}
                      name="Partner Spending"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="shared" 
                      stackId="1" 
                      stroke="#10B981" 
                      fill="#10B981" 
                      fillOpacity={0.6}
                      name="Shared Expenses"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Breakdown */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Category Breakdown</h3>
              <div className="space-y-4">
                {data.categoryBreakdown.map((category, index) => (
                  <CategoryBreakdownBar key={index} category={category} />
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'comparison' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Individual vs Shared Spending */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Individual vs Shared</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.monthlyComparison.slice(-6)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="you" fill="#4F46E5" name="You" />
                    <Bar dataKey="partner" fill="#06B6D4" name="Partner" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Spending Ratio */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Spending Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={[
                        { name: 'Your Spending', value: data.partners.find(p => p.role === 'Owner')?.totalSpent || 0 },
                        { name: 'Partner Spending', value: data.partners.find(p => p.role === 'Partner')?.totalSpent || 0 },
                        { name: 'Shared Expenses', value: data.sharedExpenses.reduce((sum, exp) => sum + exp.amount, 0) }
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                    >
                      {COLORS.map((color, index) => (
                        <Cell key={`cell-${index}`} fill={color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'shared' && (
          <div className="bg-white rounded-xl shadow-sm">
            <div className="p-6 border-b">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Recent Shared Expenses</h3>
                <div className="flex items-center gap-2">
                  <button className="btn-secondary text-sm">
                    <Filter className="h-4 w-4 mr-1" />
                    Filter
                  </button>
                  <button className="btn-secondary text-sm">
                    <Download className="h-4 w-4 mr-1" />
                    Export
                  </button>
                </div>
              </div>
            </div>
            <div className="divide-y divide-gray-200">
              {data.sharedExpenses.map((expense) => (
                <SharedExpenseRow key={expense.id} expense={expense} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'goals' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Joint Savings Goals</h3>
              <div className="space-y-4">
                <GoalProgress
                  title="Emergency Fund"
                  current={8500}
                  target={15000}
                  contributors={['You: $4,200', 'Alex: $4,300']}
                />
                <GoalProgress
                  title="Vacation Fund"
                  current={2300}
                  target={5000}
                  contributors={['You: $1,200', 'Alex: $1,100']}
                />
                <GoalProgress
                  title="Home Down Payment"
                  current={25000}
                  target={80000}
                  contributors={['You: $12,000', 'Alex: $13,000']}
                />
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Goal Contributions</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={[
                      { name: 'Emergency Fund', you: 4200, partner: 4300 },
                      { name: 'Vacation', you: 1200, partner: 1100 },
                      { name: 'Home Fund', you: 12000, partner: 13000 }
                    ]}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="you" fill="#4F46E5" name="You" />
                    <Bar dataKey="partner" fill="#06B6D4" name="Partner" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper Components
function CategoryBreakdownBar({ category }) {
  const total = category.total;
  const youPercentage = (category.you / total) * 100;
  const partnerPercentage = (category.partner / total) * 100;
  const sharedPercentage = (category.shared / total) * 100;

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="font-medium text-gray-700">{category.name}</span>
        <span className="text-sm text-gray-500">${total.toFixed(0)}</span>
      </div>
      <div className="flex w-full h-3 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="bg-indigo-500" 
          style={{ width: `${youPercentage}%` }}
          title={`You: $${category.you}`}
        />
        <div 
          className="bg-cyan-500" 
          style={{ width: `${partnerPercentage}%` }}
          title={`Partner: $${category.partner}`}
        />
        <div 
          className="bg-emerald-500" 
          style={{ width: `${sharedPercentage}%` }}
          title={`Shared: $${category.shared}`}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-500">
        <span>You: ${category.you}</span>
        <span>Partner: ${category.partner}</span>
        <span>Shared: ${category.shared}</span>
      </div>
    </div>
  );
}

function SharedExpenseRow({ expense }) {
  const getCategoryIcon = (category) => {
    const icons = {
      'Food': Utensils,
      'Home': Home,
      'Transportation': Car,
      'Entertainment': Coffee,
      'Shopping': ShoppingBag,
      'Utilities': Zap
    };
    return icons[category] || DollarSign;
  };

  const Icon = getCategoryIcon(expense.category);

  return (
    <div className="p-6 hover:bg-gray-50">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-indigo-50 rounded-full flex items-center justify-center">
            <Icon className="h-5 w-5 text-indigo-600" />
          </div>
          <div className="ml-4">
            <h4 className="text-sm font-medium text-gray-900">{expense.description}</h4>
            <div className="flex items-center text-xs text-gray-500 mt-1">
              <span>Paid by {expense.paidBy}</span>
              <span className="mx-2">•</span>
              <span>{new Date(expense.date).toLocaleDateString()}</span>
              <span className="mx-2">•</span>
              <span>{expense.category}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-gray-900">${expense.amount.toFixed(2)}</div>
          <div className="text-xs text-gray-500">Split equally</div>
        </div>
      </div>
    </div>
  );
}

function GoalProgress({ title, current, target, contributors }) {
  const progress = (current / target) * 100;

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h4 className="font-medium text-gray-900">{title}</h4>
        <span className="text-sm text-gray-500">{progress.toFixed(0)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div 
          className="bg-gradient-to-r from-indigo-500 to-cyan-500 h-3 rounded-full transition-all duration-300"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">${current.toLocaleString()} raised</span>
        <span className="text-gray-600">${target.toLocaleString()} goal</span>
      </div>
      {contributors && (
        <div className="text-xs text-gray-500">
          {contributors.join(' • ')}
        </div>
      )}
    </div>
  );
}