/**
 * Investment Goals Page - Shared Budgeting App
 * 
 * Create, edit, and manage investment and savings goals with
 * detailed analytics, progress tracking, and goal recommendations.
 */

import React, { useState, useEffect } from 'react';
import { 
  Target, 
  TrendingUp, 
  DollarSign,
  Calendar,
  Plus,
  Edit3,
  Trash2,
  CheckCircle,
  Clock,
  AlertTriangle,
  PieChart,
  BarChart3,
  Settings,
  Calculator,
  Lightbulb,
  Award,
  ArrowRight,
  TrendingDown,
  Home,
  Car,
  GraduationCap,
  Plane,
  Heart,
  Briefcase,
  Shield,
  Baby
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart as RechartsPieChart, 
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

const GOAL_CATEGORIES = [
  { id: 'emergency', name: 'Emergency Fund', icon: Shield, color: 'bg-red-100 text-red-600' },
  { id: 'home', name: 'Home & Real Estate', icon: Home, color: 'bg-blue-100 text-blue-600' },
  { id: 'vacation', name: 'Travel & Vacation', icon: Plane, color: 'bg-green-100 text-green-600' },
  { id: 'car', name: 'Vehicle', icon: Car, color: 'bg-yellow-100 text-yellow-600' },
  { id: 'education', name: 'Education', icon: GraduationCap, color: 'bg-purple-100 text-purple-600' },
  { id: 'retirement', name: 'Retirement', icon: Briefcase, color: 'bg-indigo-100 text-indigo-600' },
  { id: 'family', name: 'Family & Children', icon: Baby, color: 'bg-pink-100 text-pink-600' },
  { id: 'health', name: 'Health & Wellness', icon: Heart, color: 'bg-rose-100 text-rose-600' }
];

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('active');
  const [showAddGoal, setShowAddGoal] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [selectedGoal, setSelectedGoal] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Mock data - replace with actual API calls
      const goalsData = [
        {
          id: 1,
          name: 'Emergency Fund',
          category: 'emergency',
          target_amount: 15000,
          current_amount: 8750,
          monthly_contribution: 500,
          target_date: '2026-08-01',
          status: 'active',
          priority: 'high',
          description: 'Build 6 months of living expenses for emergencies',
          created_date: '2024-01-15',
          contributions: [
            { date: '2025-08-01', amount: 500 },
            { date: '2025-07-01', amount: 500 },
            { date: '2025-06-01', amount: 750 }
          ]
        },
        {
          id: 2,
          name: 'Home Down Payment',
          category: 'home',
          target_amount: 80000,
          current_amount: 25000,
          monthly_contribution: 1200,
          target_date: '2027-12-31',
          status: 'active',
          priority: 'high',
          description: '20% down payment for first home',
          created_date: '2024-03-01',
          contributions: []
        },
        {
          id: 3,
          name: 'Europe Vacation',
          category: 'vacation',
          target_amount: 8000,
          current_amount: 3200,
          monthly_contribution: 300,
          target_date: '2026-06-15',
          status: 'active',
          priority: 'medium',
          description: '2-week European vacation with partner',
          created_date: '2024-06-01',
          contributions: []
        },
        {
          id: 4,
          name: 'New Car',
          category: 'car',
          target_amount: 35000,
          current_amount: 12000,
          monthly_contribution: 400,
          target_date: '2026-03-01',
          status: 'active',
          priority: 'medium',
          description: 'Replace current car with electric vehicle',
          created_date: '2024-02-01',
          contributions: []
        },
        {
          id: 5,
          name: 'MBA Program',
          category: 'education',
          target_amount: 0,
          current_amount: 15000,
          monthly_contribution: 0,
          target_date: '2024-08-01',
          status: 'completed',
          priority: 'high',
          description: 'Master\'s degree in business administration',
          created_date: '2022-01-01',
          contributions: []
        }
      ];

      setGoals(goalsData);
    } catch (error) {
      console.error('Error loading goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGoalProgress = (goal) => {
    if (goal.target_amount === 0) return 100;
    return Math.min((goal.current_amount / goal.target_amount) * 100, 100);
  };

  const getGoalStatus = (goal) => {
    if (goal.status === 'completed') return 'completed';
    
    const progress = getGoalProgress(goal);
    const targetDate = new Date(goal.target_date);
    const today = new Date();
    const daysLeft = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
    
    if (progress >= 100) return 'completed';
    if (daysLeft < 0) return 'overdue';
    if (daysLeft < 30 && progress < 80) return 'at_risk';
    return 'on_track';
  };

  const getMonthlyTarget = (goal) => {
    const remaining = goal.target_amount - goal.current_amount;
    const targetDate = new Date(goal.target_date);
    const today = new Date();
    const monthsLeft = Math.max(1, Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24 * 30)));
    return remaining / monthsLeft;
  };

  const filteredGoals = goals.filter(goal => {
    if (activeTab === 'all') return true;
    if (activeTab === 'active') return goal.status === 'active';
    if (activeTab === 'completed') return goal.status === 'completed';
    if (activeTab === 'at_risk') return getGoalStatus(goal) === 'at_risk' || getGoalStatus(goal) === 'overdue';
    return true;
  });

  const totalGoalAmount = goals.filter(g => g.status === 'active').reduce((sum, goal) => sum + goal.target_amount, 0);
  const totalSaved = goals.filter(g => g.status === 'active').reduce((sum, goal) => sum + goal.current_amount, 0);
  const monthlyCommitment = goals.filter(g => g.status === 'active').reduce((sum, goal) => sum + goal.monthly_contribution, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'all', name: 'All Goals', count: goals.length },
    { id: 'active', name: 'Active', count: goals.filter(g => g.status === 'active').length },
    { id: 'completed', name: 'Completed', count: goals.filter(g => g.status === 'completed').length },
    { id: 'at_risk', name: 'At Risk', count: goals.filter(g => getGoalStatus(g) === 'at_risk' || getGoalStatus(g) === 'overdue').length }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Investment Goals</h2>
          <p className="text-gray-600">Track and manage your financial goals</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <Calculator className="h-4 w-4" />
            Calculator
          </button>
          <button 
            onClick={() => setShowAddGoal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Goal
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Goal Amount</p>
              <p className="text-2xl font-semibold text-gray-900">${totalGoalAmount.toLocaleString()}</p>
              <p className="text-sm text-blue-600 mt-1">{goals.filter(g => g.status === 'active').length} active goals</p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <Target className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Saved</p>
              <p className="text-2xl font-semibold text-gray-900">${totalSaved.toLocaleString()}</p>
              <p className="text-sm text-green-600 mt-1">{((totalSaved / totalGoalAmount) * 100).toFixed(1)}% of total</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Monthly Commitment</p>
              <p className="text-2xl font-semibold text-gray-900">${monthlyCommitment.toLocaleString()}</p>
              <p className="text-sm text-purple-600 mt-1">Across all goals</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Goals Completed</p>
              <p className="text-2xl font-semibold text-gray-900">{goals.filter(g => g.status === 'completed').length}</p>
              <p className="text-sm text-yellow-600 mt-1">This year</p>
            </div>
            <div className="bg-yellow-50 p-3 rounded-lg">
              <Award className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
              <span className="ml-2 bg-gray-100 text-gray-600 text-xs px-2 py-0.5 rounded-full">
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Goals Overview Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress Distribution */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Goals by Category</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPieChart>
                <Pie
                  data={GOAL_CATEGORIES.map(cat => ({
                    name: cat.name,
                    value: goals.filter(g => g.category === cat.id && g.status === 'active').reduce((sum, g) => sum + g.target_amount, 0)
                  })).filter(item => item.value > 0)}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                >
                  {COLORS.map((color, index) => (
                    <Cell key={`cell-${index}`} fill={color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
              </RechartsPieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Contributions */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Monthly Contributions</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={goals.filter(g => g.status === 'active')}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value) => `$${value}`} />
                <Bar dataKey="monthly_contribution" fill="#4F46E5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Goals List */}
      <div className="space-y-4">
        {filteredGoals.map((goal) => (
          <GoalCard 
            key={goal.id} 
            goal={goal} 
            onEdit={setEditingGoal}
            onSelect={setSelectedGoal}
          />
        ))}
        
        {filteredGoals.length === 0 && (
          <div className="text-center py-12">
            <Target className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No goals found</h3>
            <p className="text-gray-500 mb-6">Start by creating your first financial goal</p>
            <button 
              onClick={() => setShowAddGoal(true)}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Goal
            </button>
          </div>
        )}
      </div>

      {/* Goal Recommendations */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center mb-4">
          <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
          <h3 className="text-lg font-semibold">Recommendations</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RecommendationCard
            title="Emergency Fund Priority"
            description="Consider prioritizing your emergency fund to reach 6 months of expenses"
            action="Increase contribution"
            type="priority"
          />
          <RecommendationCard
            title="Goal Diversification"
            description="Balance short-term and long-term goals for better financial health"
            action="Add retirement goal"
            type="diversification"
          />
          <RecommendationCard
            title="Optimize Contributions"
            description="You could reach your vacation goal 3 months earlier with $50 more monthly"
            action="Increase by $50"
            type="optimization"
          />
        </div>
      </div>
    </div>
  );
}

// Helper Components
function GoalCard({ goal, onEdit, onSelect }) {
  const progress = goal.target_amount === 0 ? 100 : Math.min((goal.current_amount / goal.target_amount) * 100, 100);
  const status = goal.status === 'completed' ? 'completed' : 
    progress >= 100 ? 'completed' : 
    new Date(goal.target_date) < new Date() ? 'overdue' : 'active';
  
  const category = GOAL_CATEGORIES.find(cat => cat.id === goal.category) || GOAL_CATEGORIES[0];
  const Icon = category.icon;
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      case 'active': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const monthlyTarget = goal.target_amount === 0 ? 0 : Math.max(0, (goal.target_amount - goal.current_amount) / Math.max(1, Math.ceil((new Date(goal.target_date) - new Date()) / (1000 * 60 * 60 * 24 * 30))));

  return (
    <div 
      onClick={() => onSelect(goal)}
      className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center">
          <div className={`w-12 h-12 rounded-lg flex items-center justify-center mr-4 ${category.color}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-lg">{goal.name}</h3>
            <p className="text-sm text-gray-600">{goal.description}</p>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${getStatusColor(status)}`}>
              {status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
              {status === 'overdue' && <AlertTriangle className="w-3 h-3 mr-1" />}
              {status === 'active' && <Clock className="w-3 h-3 mr-1" />}
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(goal);
            }}
            className="p-2 text-gray-400 hover:text-indigo-600"
          >
            <Edit3 className="h-4 w-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-red-600">
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium text-gray-700">Progress</span>
            <span className="text-gray-500">{progress.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className={`h-3 rounded-full transition-all duration-300 ${
                status === 'completed' ? 'bg-green-500' :
                status === 'overdue' ? 'bg-red-500' : 'bg-indigo-500'
              }`}
              style={{ width: `${Math.min(progress, 100)}%` }}
            />
          </div>
        </div>

        {/* Financial Details */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Current</p>
            <p className="font-semibold text-gray-900">${goal.current_amount.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Target</p>
            <p className="font-semibold text-gray-900">${goal.target_amount.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Monthly</p>
            <p className="font-semibold text-gray-900">${goal.monthly_contribution.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">Target Date</p>
            <p className="font-semibold text-gray-900">{new Date(goal.target_date).toLocaleDateString()}</p>
          </div>
        </div>

        {/* Insights */}
        {status === 'active' && monthlyTarget > goal.monthly_contribution && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <div className="flex items-center">
              <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2" />
              <p className="text-sm text-yellow-800">
                Consider increasing monthly contribution to ${monthlyTarget.toFixed(0)} to reach your goal on time
              </p>
            </div>
          </div>
        )}
        
        {status === 'active' && monthlyTarget < goal.monthly_contribution && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
              <p className="text-sm text-green-800">
                Great! You're on track to reach this goal ahead of schedule
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RecommendationCard({ title, description, action, type }) {
  const getIcon = (type) => {
    switch (type) {
      case 'priority': return AlertTriangle;
      case 'diversification': return PieChart;
      case 'optimization': return TrendingUp;
      default: return Lightbulb;
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'priority': return 'bg-red-50 border-red-200 text-red-800';
      case 'diversification': return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'optimization': return 'bg-green-50 border-green-200 text-green-800';
      default: return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    }
  };

  const Icon = getIcon(type);

  return (
    <div className={`border rounded-lg p-4 ${getColor(type)}`}>
      <div className="flex items-start">
        <Icon className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="font-medium mb-1">{title}</h4>
          <p className="text-sm mb-3 opacity-90">{description}</p>
          <button className="text-sm font-medium hover:underline flex items-center">
            {action}
            <ArrowRight className="h-3 w-3 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
}