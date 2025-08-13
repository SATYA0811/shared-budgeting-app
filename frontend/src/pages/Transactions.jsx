/**
 * Transactions Page - Shared Budgeting App
 * 
 * Comprehensive transaction management with filtering, searching,
 * categorization, and bulk operations.
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Download, 
  Upload, 
  Plus,
  Edit3,
  Trash2,
  Calendar,
  DollarSign,
  Tag,
  TrendingUp,
  TrendingDown,
  ArrowUpDown,
  MoreHorizontal,
  CheckCircle2,
  X
} from 'lucide-react';
import api from '../services/api';
import FileUpload from '../components/FileUpload';

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [filteredTransactions, setFilteredTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    dateRange: '',
    amountRange: '',
    type: 'all' // all, income, expense
  });
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [showFileUpload, setShowFileUpload] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [transactions, searchTerm, filters, sortBy, sortOrder]);

  const loadData = async () => {
    try {
      const [transactionData, categoryData] = await Promise.all([
        api.transactions.getTransactions({ limit: 1000 }),
        api.categories.getCategories()
      ]);
      
      setTransactions(transactionData || []);
      setCategories(categoryData || []);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...transactions];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(transaction => 
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.category_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (filters.category) {
      filtered = filtered.filter(transaction => 
        transaction.category_id === parseInt(filters.category)
      );
    }

    // Type filter
    if (filters.type !== 'all') {
      if (filters.type === 'income') {
        filtered = filtered.filter(transaction => transaction.amount > 0);
      } else if (filters.type === 'expense') {
        filtered = filtered.filter(transaction => transaction.amount < 0);
      }
    }

    // Date range filter
    if (filters.dateRange) {
      const now = new Date();
      let startDate;
      
      switch (filters.dateRange) {
        case '7days':
          startDate = new Date(now.setDate(now.getDate() - 7));
          break;
        case '30days':
          startDate = new Date(now.setDate(now.getDate() - 30));
          break;
        case '90days':
          startDate = new Date(now.setDate(now.getDate() - 90));
          break;
        default:
          startDate = null;
      }
      
      if (startDate) {
        filtered = filtered.filter(transaction => 
          new Date(transaction.date) >= startDate
        );
      }
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'amount':
          aVal = Math.abs(a.amount);
          bVal = Math.abs(b.amount);
          break;
        case 'description':
          aVal = a.description?.toLowerCase() || '';
          bVal = b.description?.toLowerCase() || '';
          break;
        case 'category':
          aVal = a.category_name?.toLowerCase() || '';
          bVal = b.category_name?.toLowerCase() || '';
          break;
        default: // date
          aVal = new Date(a.date);
          bVal = new Date(b.date);
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

    setFilteredTransactions(filtered);
  };

  const toggleTransactionSelection = (transactionId) => {
    setSelectedTransactions(prev => 
      prev.includes(transactionId)
        ? prev.filter(id => id !== transactionId)
        : [...prev, transactionId]
    );
  };

  const selectAllTransactions = () => {
    if (selectedTransactions.length === filteredTransactions.length) {
      setSelectedTransactions([]);
    } else {
      setSelectedTransactions(filteredTransactions.map(t => t.id));
    }
  };

  const exportTransactions = () => {
    // Export logic here
    console.log('Exporting transactions...');
  };

  const deleteSelectedTransactions = async () => {
    if (confirm(`Delete ${selectedTransactions.length} selected transactions?`)) {
      try {
        await Promise.all(
          selectedTransactions.map(id => api.transactions.deleteTransaction(id))
        );
        await loadData();
        setSelectedTransactions([]);
      } catch (error) {
        console.error('Error deleting transactions:', error);
      }
    }
  };

  const handleUploadSuccess = (result) => {
    console.log('Upload successful:', result);
    loadData(); // Reload transactions after successful upload
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Transactions</h2>
          <p className="text-gray-600">
            {filteredTransactions.length} of {transactions.length} transactions
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={exportTransactions}
            className="btn-secondary flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Export
          </button>
          <button 
            onClick={() => setShowFileUpload(true)}
            className="btn-secondary flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            Import
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Transaction
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {/* Quick Filters */}
          <div className="flex items-center gap-2">
            <select
              value={filters.type}
              onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Types</option>
              <option value="income">Income</option>
              <option value="expense">Expenses</option>
            </select>

            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg border ${showFilters ? 'bg-indigo-50 border-indigo-200' : 'border-gray-300'}`}
            >
              <Filter className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
              <select
                value={filters.dateRange}
                onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Time</option>
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="date">Date</option>
                <option value="amount">Amount</option>
                <option value="description">Description</option>
                <option value="category">Category</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Order</label>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center justify-center gap-2"
              >
                <ArrowUpDown className="h-4 w-4" />
                {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {selectedTransactions.length > 0 && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="font-medium text-indigo-900">
                {selectedTransactions.length} transactions selected
              </span>
              <button
                onClick={() => setSelectedTransactions([])}
                className="text-indigo-700 hover:text-indigo-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button className="btn-secondary text-sm">Categorize</button>
              <button className="btn-secondary text-sm">Export</button>
              <button 
                onClick={deleteSelectedTransactions}
                className="btn-danger text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedTransactions.length === filteredTransactions.length && filteredTransactions.length > 0}
                    onChange={selectAllTransactions}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Description
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredTransactions.map((transaction) => (
                <TransactionRow
                  key={transaction.id}
                  transaction={transaction}
                  categories={categories}
                  selected={selectedTransactions.includes(transaction.id)}
                  onToggleSelect={() => toggleTransactionSelection(transaction.id)}
                  onEdit={(transaction) => setEditingTransaction(transaction)}
                />
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredTransactions.length === 0 && (
          <div className="text-center py-12">
            <DollarSign className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
            <p className="text-gray-500">Try adjusting your search or filters</p>
          </div>
        )}
      </div>

      {/* File Upload Modal */}
      {showFileUpload && (
        <FileUpload
          onUploadSuccess={handleUploadSuccess}
          onClose={() => setShowFileUpload(false)}
        />
      )}
    </div>
  );
}

// Transaction Row Component
function TransactionRow({ transaction, categories, selected, onToggleSelect, onEdit }) {
  const [showActions, setShowActions] = useState(false);
  const isExpense = transaction.amount < 0;
  
  return (
    <tr 
      className={`hover:bg-gray-50 ${selected ? 'bg-indigo-50' : ''}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <td className="px-6 py-4">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggleSelect}
          className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
      </td>
      <td className="px-6 py-4 text-sm text-gray-900">
        {new Date(transaction.date).toLocaleDateString('en-CA', { 
          year: 'numeric', 
          month: '2-digit', 
          day: '2-digit' 
        })}
      </td>
      <td className="px-6 py-4">
        <div className="flex items-center">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
            isExpense ? 'bg-red-50' : 'bg-green-50'
          }`}>
            {isExpense ? 
              <TrendingDown className="h-4 w-4 text-red-600" /> :
              <TrendingUp className="h-4 w-4 text-green-600" />
            }
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900">
              {transaction.description}
            </div>
            {transaction.bank_name && (
              <div className="text-xs text-gray-500">
                {transaction.bank_name}
              </div>
            )}
          </div>
        </div>
      </td>
      <td className="px-6 py-4">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <Tag className="h-3 w-3 mr-1" />
          {transaction.category_name || 'Uncategorized'}
        </span>
      </td>
      <td className="px-6 py-4 text-right">
        <span className={`text-sm font-semibold ${
          isExpense ? 'text-red-600' : 'text-green-600'
        }`}>
          {isExpense ? '-' : '+'}${Math.abs(transaction.amount).toLocaleString('en-CA', { minimumFractionDigits: 2 })} CAD
        </span>
      </td>
      <td className="px-6 py-4 text-right">
        {showActions && (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => onEdit(transaction)}
              className="p-1 text-gray-400 hover:text-indigo-600"
            >
              <Edit3 className="h-4 w-4" />
            </button>
            <button className="p-1 text-gray-400 hover:text-red-600">
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        )}
      </td>
    </tr>
  );
}