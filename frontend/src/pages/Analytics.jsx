/**
 * Analytics Page - Shared Budgeting App
 * 
 * Comprehensive financial analytics with advanced charts,
 * insights, trends, and detailed breakdowns.
 */

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  PieChart,
  BarChart3,
  LineChart as LineChartIcon,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Target,
  CreditCard,
  Wallet,
  Home,
  Car,
  Coffee,
  ShoppingBag,
  Utensils,
  Zap,
  Heart,
  GraduationCap,
  Briefcase,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  CheckCircle,
  Info,
  Eye,
  Settings
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
  AreaChart,
  ComposedChart,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Treemap
} from 'recharts';
import api from '../services/api';

const COLORS = ['#4F46E5', '#06B6D4', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#84CC16'];

export default function Analytics() {
  const [data, setData] = useState({
    overview: {},
    monthlyTrends: [],
    categoryBreakdown: [],
    incomeVsExpenses: [],
    cashFlow: [],
    budgetPerformance: [],
    savingsRate: [],
    insights: []
  });
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('12months');
  const [selectedChart, setSelectedChart] = useState('trends');
  const [compareMode, setCompareMode] = useState(false);

  useEffect(() => {
    loadData();
  }, [selectedPeriod]);

  const loadData = async () => {
    try {
      // Mock comprehensive analytics data
      const overviewData = {
        totalIncome: 125000,
        totalExpenses: 95000,
        netSavings: 30000,
        savingsRate: 24,
        budgetVariance: -5.2,
        topCategory: 'Housing',
        avgMonthlySpending: 7916,
        transactionCount: 1247
      };

      const monthlyTrendsData = [
        { month: 'Jan 2025', income: 10500, expenses: 7800, savings: 2700, savingsRate: 25.7 },
        { month: 'Feb 2025', income: 10200, expenses: 8100, savings: 2100, savingsRate: 20.6 },
        { month: 'Mar 2025', income: 10800, expenses: 8400, savings: 2400, savingsRate: 22.2 },
        { month: 'Apr 2025', income: 10300, expenses: 7600, savings: 2700, savingsRate: 26.2 },
        { month: 'May 2025', income: 11200, expenses: 8200, savings: 3000, savingsRate: 26.8 },
        { month: 'Jun 2025', income: 10600, expenses: 7900, savings: 2700, savingsRate: 25.5 },
        { month: 'Jul 2025', income: 10900, expenses: 8300, savings: 2600, savingsRate: 23.9 },
        { month: 'Aug 2025', income: 10400, expenses: 7950, savings: 2450, savingsRate: 23.6 }
      ];

      const categoryBreakdownData = [
        { name: 'Housing', amount: 28500, budget: 30000, percentage: 30.0, transactions: 24, trend: 'down', icon: Home },
        { name: 'Food & Dining', amount: 18200, budget: 15000, percentage: 19.2, transactions: 156, trend: 'up', icon: Utensils },
        { name: 'Transportation', amount: 12800, budget: 12000, percentage: 13.5, transactions: 89, trend: 'up', icon: Car },
        { name: 'Shopping', amount: 9500, budget: 8000, percentage: 10.0, transactions: 67, trend: 'up', icon: ShoppingBag },
        { name: 'Entertainment', amount: 7200, budget: 6000, percentage: 7.6, transactions: 43, trend: 'stable', icon: Coffee },
        { name: 'Utilities', amount: 6800, budget: 7000, percentage: 7.2, transactions: 18, trend: 'down', icon: Zap },
        { name: 'Health', amount: 5900, budget: 6000, percentage: 6.2, transactions: 25, trend: 'stable', icon: Heart },
        { name: 'Education', amount: 3200, budget: 4000, percentage: 3.4, transactions: 8, trend: 'down', icon: GraduationCap },
        { name: 'Investments', amount: 2900, budget: 3000, percentage: 3.1, transactions: 12, trend: 'stable', icon: Briefcase }
      ];

      const cashFlowData = [
        { date: '2025-08-01', income: 3200, expenses: -2100, net: 1100 },
        { date: '2025-08-02', income: 0, expenses: -45, net: -45 },
        { date: '2025-08-03', income: 150, expenses: -230, net: -80 },
        { date: '2025-08-04', income: 0, expenses: -120, net: -120 },
        { date: '2025-08-05', income: 2800, expenses: -890, net: 1910 },
        { date: '2025-08-06', income: 0, expenses: -67, net: -67 },
        { date: '2025-08-07', income: 450, expenses: -340, net: 110 },
        { date: '2025-08-08', income: 0, expenses: -180, net: -180 },
        { date: '2025-08-09', income: 1200, expenses: -520, net: 680 },
        { date: '2025-08-10', income: 0, expenses: -95, net: -95 }
      ];

      const budgetPerformanceData = categoryBreakdownData.map(cat => ({
        category: cat.name,
        spent: cat.amount,
        budget: cat.budget,
        variance: ((cat.amount - cat.budget) / cat.budget * 100).toFixed(1),
        remaining: Math.max(0, cat.budget - cat.amount)
      }));

      const savingsRateData = monthlyTrendsData.map(month => ({
        month: month.month.split(' ')[0],
        rate: month.savingsRate,
        target: 25,
        amount: month.savings
      }));

      const insightsData = [
        {
          type: 'warning',
          title: 'Food Spending Above Budget',
          description: 'You\'ve spent 21% more on food than budgeted this month',
          amount: 3200,
          action: 'Review dining expenses'
        },
        {
          type: 'positive',
          title: 'Housing Costs Under Budget',
          description: 'Housing expenses are 5% under budget, saving you $1,500',
          amount: 1500,
          action: 'Consider increasing savings'
        },
        {
          type: 'info',
          title: 'Consistent Savings Rate',
          description: 'Your savings rate has been stable at 24% for 3 months',
          amount: 2400,
          action: 'Great consistency!'
        },
        {
          type: 'warning',
          title: 'Weekend Spending Spike',
          description: 'Weekend expenses are 40% higher than weekdays',
          amount: 850,
          action: 'Plan weekend budget'
        }
      ];

      setData({
        overview: overviewData,
        monthlyTrends: monthlyTrendsData,
        categoryBreakdown: categoryBreakdownData,
        incomeVsExpenses: monthlyTrendsData,
        cashFlow: cashFlowData,
        budgetPerformance: budgetPerformanceData,
        savingsRate: savingsRateData,
        insights: insightsData
      });
    } catch (error) {
      console.error('Error loading analytics data:', error);
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

  const chartTypes = [
    { id: 'trends', name: 'Trends', icon: LineChartIcon },
    { id: 'categories', name: 'Categories', icon: PieChart },
    { id: 'budget', name: 'Budget vs Actual', icon: BarChart3 },
    { id: 'cashflow', name: 'Cash Flow', icon: TrendingUp }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Financial Analytics</h2>
          <p className="text-gray-600">Comprehensive insights into your spending patterns and trends</p>
        </div>
        
        <div className="flex items-center gap-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
          >
            <option value="3months">Last 3 Months</option>
            <option value="6months">Last 6 Months</option>
            <option value="12months">Last 12 Months</option>
            <option value="ytd">Year to Date</option>
          </select>
          <button className="btn-secondary flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <MetricCard
          title="Total Income"
          value={`$${data.overview.totalIncome?.toLocaleString()}`}
          change="+8.2%"
          changeType="positive"
          icon={TrendingUp}
          color="green"
        />
        <MetricCard
          title="Total Expenses"
          value={`$${data.overview.totalExpenses?.toLocaleString()}`}
          change="+3.1%"
          changeType="negative"
          icon={TrendingDown}
          color="red"
        />
        <MetricCard
          title="Net Savings"
          value={`$${data.overview.netSavings?.toLocaleString()}`}
          change="+15.4%"
          changeType="positive"
          icon={Target}
          color="blue"
        />
        <MetricCard
          title="Savings Rate"
          value={`${data.overview.savingsRate}%`}
          change="+2.1%"
          changeType="positive"
          icon={PieChart}
          color="purple"
        />
      </div>

      {/* Chart Selector */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-1">
            {chartTypes.map((chart) => {
              const Icon = chart.icon;
              return (
                <button
                  key={chart.id}
                  onClick={() => setSelectedChart(chart.id)}
                  className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedChart === chart.id
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {chart.name}
                </button>
              );
            })}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCompareMode(!compareMode)}
              className={`px-3 py-1 text-sm rounded-md ${
                compareMode ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700'
              }`}
            >
              Compare
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600">
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Chart Content */}
        <div className="h-96">
          {selectedChart === 'trends' && (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={data.monthlyTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Area 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="income" 
                  fill="#10B981" 
                  fillOpacity={0.3}
                  stroke="#10B981"
                  name="Income"
                />
                <Area 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="expenses" 
                  fill="#EF4444" 
                  fillOpacity={0.3}
                  stroke="#EF4444"
                  name="Expenses"
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="savingsRate" 
                  stroke="#4F46E5" 
                  strokeWidth={3}
                  name="Savings Rate (%)"
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}

          {selectedChart === 'categories' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPieChart>
                  <Pie
                    data={data.categoryBreakdown}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    dataKey="amount"
                    nameKey="name"
                  >
                    {data.categoryBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
              
              <div className="space-y-3">
                <h4 className="font-semibold text-gray-900">Category Breakdown</h4>
                {data.categoryBreakdown.map((category, index) => (
                  <CategoryBreakdownItem key={index} category={category} color={COLORS[index % COLORS.length]} />
                ))}
              </div>
            </div>
          )}

          {selectedChart === 'budget' && (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.budgetPerformance} margin={{ bottom: 80 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="budget" fill="#E5E7EB" name="Budget" />
                <Bar dataKey="spent" fill="#4F46E5" name="Actual Spending" />
              </BarChart>
            </ResponsiveContainer>
          )}

          {selectedChart === 'cashflow' && (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.cashFlow}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area 
                  type="monotone" 
                  dataKey="net" 
                  stroke="#4F46E5" 
                  fill="#4F46E5" 
                  fillOpacity={0.6}
                  name="Net Cash Flow"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Detailed Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Savings Rate Trend */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Savings Rate Trend</h3>
          <div className="h-48 mb-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.savingsRate}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="rate" 
                  stroke="#10B981" 
                  strokeWidth={3}
                  name="Actual"
                />
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke="#EF4444" 
                  strokeDasharray="5 5"
                  name="Target"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="text-sm text-gray-600">
            <p>Current: <span className="font-semibold text-green-600">24%</span></p>
            <p>Target: <span className="font-semibold text-gray-900">25%</span></p>
            <p>You're <span className="font-semibold text-yellow-600">1%</span> below target</p>
          </div>
        </div>

        {/* Budget Performance */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Budget Performance</h3>
          <div className="space-y-3">
            {data.budgetPerformance.slice(0, 5).map((item, index) => (
              <BudgetPerformanceBar key={index} item={item} />
            ))}
          </div>
          <button className="text-indigo-600 hover:text-indigo-700 text-sm font-medium mt-4">
            View all categories →
          </button>
        </div>

        {/* Top Insights */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Key Insights</h3>
          <div className="space-y-4">
            {data.insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} />
            ))}
          </div>
        </div>
      </div>

      {/* Financial Health Score */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Financial Health Score</h3>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-green-600">78</span>
            <span className="text-sm text-gray-500">/100</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <HealthScoreItem title="Emergency Fund" score={85} status="good" />
          <HealthScoreItem title="Debt-to-Income" score={65} status="fair" />
          <HealthScoreItem title="Savings Rate" score={80} status="good" />
          <HealthScoreItem title="Budget Adherence" score={72} status="fair" />
        </div>
      </div>
    </div>
  );
}

// Helper Components
function MetricCard({ title, value, change, changeType, icon: Icon, color }) {
  const colorClasses = {
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600'
  };

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
              <ArrowUpRight className="h-4 w-4 mr-1" /> : 
              <ArrowDownRight className="h-4 w-4 mr-1" />
            }
            {change}
          </div>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function CategoryBreakdownItem({ category, color }) {
  const Icon = category.icon;
  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-3 w-3 text-red-500" />;
      case 'down': return <TrendingDown className="h-3 w-3 text-green-500" />;
      default: return <div className="w-3 h-0.5 bg-gray-400" />;
    }
  };

  return (
    <div className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg">
      <div className="flex items-center">
        <div className="w-4 h-4 rounded-full mr-3" style={{ backgroundColor: color }} />
        <Icon className="h-4 w-4 text-gray-600 mr-2" />
        <span className="text-sm font-medium text-gray-900">{category.name}</span>
      </div>
      <div className="flex items-center gap-2">
        {getTrendIcon(category.trend)}
        <span className="text-sm text-gray-600">${category.amount.toLocaleString()}</span>
      </div>
    </div>
  );
}

function BudgetPerformanceBar({ item }) {
  const variance = parseFloat(item.variance);
  const isOverBudget = variance > 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-gray-700">{item.category}</span>
        <span className={`font-semibold ${isOverBudget ? 'text-red-600' : 'text-green-600'}`}>
          {isOverBudget ? '+' : ''}{variance}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full ${isOverBudget ? 'bg-red-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(Math.abs(variance) / 50 * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}

function InsightCard({ insight }) {
  const getIcon = (type) => {
    switch (type) {
      case 'warning': return AlertTriangle;
      case 'positive': return CheckCircle;
      default: return Info;
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'positive': return 'text-green-600 bg-green-50';
      default: return 'text-blue-600 bg-blue-50';
    }
  };

  const Icon = getIcon(insight.type);

  return (
    <div className="flex items-start space-x-3">
      <div className={`p-1 rounded ${getColor(insight.type)}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{insight.title}</p>
        <p className="text-xs text-gray-600 mt-1">{insight.description}</p>
        <button className="text-xs text-indigo-600 hover:text-indigo-700 mt-1">
          {insight.action}
        </button>
      </div>
    </div>
  );
}

function HealthScoreItem({ title, score, status }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-50';
      case 'good': return 'text-green-600 bg-green-50';
      case 'fair': return 'text-yellow-600 bg-yellow-50';
      case 'poor': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="text-center">
      <div className="relative">
        <svg className="w-16 h-16 mx-auto" viewBox="0 0 36 36">
          <path
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="3"
          />
          <path
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke={status === 'good' ? '#10B981' : status === 'fair' ? '#F59E0B' : '#EF4444'}
            strokeWidth="3"
            strokeDasharray={`${score}, 100`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-semibold text-gray-900">{score}</span>
        </div>
      </div>
      <h4 className="font-medium text-gray-900 mt-2">{title}</h4>
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mt-1 ${getStatusColor(status)}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    </div>
  );
}