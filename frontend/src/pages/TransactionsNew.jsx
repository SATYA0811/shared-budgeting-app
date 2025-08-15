/**
 * Modern Transactions Page - Matching the provided design
 * Features: Monthly grouping, advanced filtering, bulk selection, export
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, 
  ChevronDown,
  Download, 
  Upload,
  RotateCcw,
  Check,
  Calendar,
  Building2,
  Tag as TagIcon,
  Store,
  Filter,
  SlidersHorizontal,
  TrendingUp,
  TrendingDown,
  MoreHorizontal,
  Plus,
  X,
  Loader,
  Wallet,
  PlusCircle
} from 'lucide-react';
import api from '../services/api';
import PDFUpload from '../components/PDFUpload';
import QuickAddTransaction from '../components/QuickAddTransaction';

// Utility function for Canadian currency formatting
const formatCAD = (amount) => {
  const absAmount = Math.abs(amount);
  return `$${absAmount.toLocaleString('en-CA', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })}`;
};

export default function TransactionsNew() {
  // State management
  const [monthlyGroups, setMonthlyGroups] = useState([]);
  const [filterStats, setFilterStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [selectedTransactions, setSelectedTransactions] = useState([]);
  const [showPDFUpload, setShowPDFUpload] = useState(false);
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [accountBalance, setAccountBalance] = useState(0);
  const [accounts, setAccounts] = useState([]);
  
  // Filter states
  const [filters, setFilters] = useState({
    sortBy: 'date',
    sortOrder: 'desc',
    timeFilter: 'all',
    bankFilter: 'all',
    hasCategory: null,
    merchantFilter: null,
    year: new Date().getFullYear()
  });

  // Load data on component mount and filter changes
  useEffect(() => {
    loadTransactionData();
    loadFilterStats();
  }, [filters.year]);

  // Debounced search
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchQuery.trim()) {
        performSearch();
      } else {
        clearSearch();
      }
    }, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const loadTransactionData = async () => {
    try {
      setLoading(true);
      const params = {
        year: filters.year,
        search: searchQuery || undefined,
        bank_filter: filters.bankFilter !== 'all' ? filters.bankFilter : undefined,
        has_category: filters.hasCategory,
        merchant_filter: filters.merchantFilter,
        sort_by: filters.sortBy || 'date',
        sort_order: filters.sortOrder || 'desc',
        time_filter: filters.timeFilter !== 'all' ? filters.timeFilter : undefined
      };

      const response = await api.transactions.getGroupedByMonth(params);
      let monthlyGroups = response.monthly_groups || [];
      
      // Apply client-side sorting if needed
      if (filters.sortOrder === 'asc') {
        monthlyGroups = monthlyGroups.reverse();
        monthlyGroups.forEach(group => {
          group.transactions = group.transactions.reverse();
        });
      }
      
      setMonthlyGroups(monthlyGroups);
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFilterStats = async () => {
    try {
      const response = await api.transactions.getFilterStats({ year: filters.year });
      setFilterStats(response);
    } catch (error) {
      console.error('Error loading filter stats:', error);
    }
  };

  const calculateBalance = () => {
    // Calculate balance from all transactions
    let balance = 0;
    monthlyGroups.forEach(monthGroup => {
      monthGroup.transactions.forEach(transaction => {
        balance += transaction.amount;
      });
    });
    setAccountBalance(balance);
  };

  // Calculate balance when monthly groups change
  useEffect(() => {
    calculateBalance();
  }, [monthlyGroups]);

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setIsSearching(true);
      setShowSearchResults(true);
      
      // Search using the regular transactions endpoint with search parameter
      const response = await api.transactions.getTransactions({
        search: searchQuery.trim(),
        limit: 100, // Get more results for search
        sort_by: 'date',
        sort_order: 'desc'
      });
      
      setSearchResults(response || []);
    } catch (error) {
      console.error('Error performing search:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
    setIsSearching(false);
    // Reload main transaction data
    loadTransactionData();
  };

  const handleSearchInputChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    
    // If input is cleared, immediately show main transactions
    if (!value.trim()) {
      clearSearch();
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    loadTransactionData();
  };

  const resetFilters = () => {
    setFilters({
      sortBy: 'date',
      sortOrder: 'desc',
      timeFilter: 'all',
      bankFilter: 'all',
      hasCategory: null,
      merchantFilter: null,
      year: new Date().getFullYear()
    });
    setSearchQuery('');
  };

  const toggleTransactionSelection = (transactionId) => {
    setSelectedTransactions(prev => 
      prev.includes(transactionId)
        ? prev.filter(id => id !== transactionId)
        : [...prev, transactionId]
    );
  };

  const handleBulkExport = async () => {
    if (selectedTransactions.length === 0) return;
    
    try {
      const response = await api.transactions.exportSelected(selectedTransactions, 'csv');
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting transactions:', error);
    }
  };

  const handlePDFUploadSuccess = (result) => {
    console.log('PDF Upload successful:', result);
    setShowPDFUpload(false);
    // Reload data to show new transactions
    loadTransactionData();
    loadFilterStats();
  };

  const handleQuickAddSuccess = (transactionData) => {
    console.log('Transaction added successfully:', transactionData);
    setShowQuickAdd(false);
    // Reload data to show new transaction
    loadTransactionData();
    loadFilterStats();
  };

  const getTimeFilterLabel = () => {
    switch (filters.timeFilter) {
      case '7days': return 'Last 7 days';
      case '30days': return 'Last 30 days';
      case '90days': return 'Last 90 days';
      case '6months': return 'Last 6 months';
      case '1year': return 'Last year';
      default: return 'All time';
    }
  };

  const handleTimeFilterClick = () => {
    const timeFilterOptions = ['all', '7days', '30days', '90days', '6months', '1year'];
    const currentIndex = timeFilterOptions.indexOf(filters.timeFilter);
    const nextIndex = (currentIndex + 1) % timeFilterOptions.length;
    handleFilterChange('timeFilter', timeFilterOptions[nextIndex]);
  };

  const getBankFilterLabel = () => {
    switch (filters.bankFilter) {
      case 'CIBC': return 'CIBC';
      case 'RBC': return 'RBC';
      case 'AMEX': return 'AMEX';
      case 'TD': return 'TD Bank';
      case 'Scotiabank': return 'Scotiabank';
      default: return 'All banks';
    }
  };

  const handleBankFilterClick = () => {
    const bankFilterOptions = ['all', 'CIBC', 'RBC', 'AMEX', 'TD', 'Scotiabank'];
    const currentIndex = bankFilterOptions.indexOf(filters.bankFilter);
    const nextIndex = (currentIndex + 1) % bankFilterOptions.length;
    handleFilterChange('bankFilter', bankFilterOptions[nextIndex]);
  };


  if (loading && monthlyGroups.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Section */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Transactions</h1>
        </div>
        
        {/* Top Right Buttons */}
        <div className="flex items-center gap-4">
          {/* Balance Display */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 px-6 py-3 flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <Wallet className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Account Balance</p>
              <p className={`text-lg font-semibold ${
                accountBalance >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {accountBalance >= 0 ? '+' : ''}{formatCAD(accountBalance)}
              </p>
            </div>
          </div>

          {/* Quick Add Transaction Button */}
          <button
            onClick={() => setShowQuickAdd(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl shadow-sm flex items-center gap-3 transition-colors"
          >
            <PlusCircle className="h-5 w-5" />
            <span className="font-medium">Quick Add</span>
          </button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
        <div className="p-6">
          {/* Search Bar */}
          <div className="relative mb-6">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Search transactions"
              value={searchQuery}
              onChange={handleSearchInputChange}
              className="w-full pl-12 pr-12 py-3 border border-gray-300 rounded-lg text-lg placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            
            {/* Search Loading/Clear Button */}
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              {isSearching ? (
                <Loader className="h-5 w-5 text-gray-400 animate-spin" />
              ) : searchQuery.trim() ? (
                <button
                  onClick={clearSearch}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                  title="Clear search"
                >
                  <X className="h-4 w-4" />
                </button>
              ) : null}
            </div>
          </div>

          {/* Filter Controls */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Sort Controls */}
            <FilterButton
              icon={<SlidersHorizontal className="h-4 w-4" />}
              label={filters.sortOrder === 'desc' ? 'Newest first' : 'Oldest first'}
              active={filters.sortOrder !== 'desc'}
              onClick={() => handleFilterChange('sortOrder', filters.sortOrder === 'desc' ? 'asc' : 'desc')}
            />

            {/* Time Filter */}
            <FilterButton
              icon={<Calendar className="h-4 w-4" />}
              label={getTimeFilterLabel()}
              active={filters.timeFilter !== 'all'}
              onClick={handleTimeFilterClick}
            />

            {/* Bank Filter */}
            <FilterButton
              icon={<Building2 className="h-4 w-4" />}
              label={getBankFilterLabel()}
              active={filters.bankFilter !== 'all'}
              onClick={handleBankFilterClick}
            />

            {/* Category Filter */}
            <FilterBadge
              icon={<TagIcon className="h-4 w-4" />}
              label="Untagged"
              count={filterStats?.categorization?.untagged || 0}
              active={filters.hasCategory === false}
              onClick={() => handleFilterChange('hasCategory', filters.hasCategory === false ? null : false)}
            />

            {/* Merchant Filter */}
            <FilterBadge
              icon={<Store className="h-4 w-4" />}
              label="No Merchant"
              count={0}
              active={filters.merchantFilter === 'unknown'}
              onClick={() => handleFilterChange('merchantFilter', filters.merchantFilter === 'unknown' ? null : 'unknown')}
            />

            {/* Reset Filters */}
            <button
              onClick={resetFilters}
              className="ml-auto flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              Reset filters
            </button>

            {/* Upload Button */}
            <button
              onClick={() => setShowPDFUpload(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Upload className="h-4 w-4" />
              Upload PDF
            </button>

            {/* Export Button */}
            <button
              onClick={handleBulkExport}
              disabled={selectedTransactions.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Download className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Search Results */}
      {showSearchResults && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6">
          <div className="p-4 border-b border-gray-200 bg-blue-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Search className="h-5 w-5 text-blue-600" />
                <div>
                  <h3 className="text-lg font-semibold text-blue-900">
                    Search Results for "{searchQuery}"
                  </h3>
                  <p className="text-sm text-blue-700">
                    {searchResults.length} transaction{searchResults.length !== 1 ? 's' : ''} found
                  </p>
                </div>
              </div>
              <button
                onClick={clearSearch}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-blue-700 hover:text-blue-800 hover:bg-blue-100 rounded-lg transition-colors"
              >
                <X className="h-4 w-4" />
                Clear Search
              </button>
            </div>
          </div>

          {/* Search Results List */}
          <div className="divide-y divide-gray-100">
            {searchResults.length > 0 ? (
              searchResults.map((transaction) => (
                <SearchResultRow
                  key={transaction.id}
                  transaction={transaction}
                  selected={selectedTransactions.includes(transaction.id)}
                  onToggleSelect={() => toggleTransactionSelection(transaction.id)}
                />
              ))
            ) : (
              <div className="p-8 text-center">
                <Search className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
                <p className="text-gray-500">Try searching with different keywords</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Monthly Groups - Only show when not searching */}
      {!showSearchResults && (
        <div className="space-y-8">
          {monthlyGroups.map((monthGroup) => (
            <MonthlyGroup
              key={`${monthGroup.year}-${monthGroup.month}`}
              monthGroup={monthGroup}
              selectedTransactions={selectedTransactions}
              onToggleTransaction={toggleTransactionSelection}
            />
          ))}

          {monthlyGroups.length === 0 && !loading && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <div className="text-gray-400 mb-4">
                <Search className="h-12 w-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
              <p className="text-gray-500">Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      )}

      {/* PDF Upload Modal */}
      {showPDFUpload && (
        <PDFUpload
          onUploadSuccess={handlePDFUploadSuccess}
          onClose={() => setShowPDFUpload(false)}
        />
      )}

      {/* Quick Add Transaction Modal */}
      {showQuickAdd && (
        <QuickAddTransaction
          onSuccess={handleQuickAddSuccess}
          onClose={() => setShowQuickAdd(false)}
        />
      )}
    </div>
  );
}

// Filter Button Component
function FilterButton({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
        active 
          ? 'bg-blue-50 border-blue-200 text-blue-700' 
          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
      <ChevronDown className="h-4 w-4" />
    </button>
  );
}

// Filter Badge Component (with count)
function FilterBadge({ icon, label, count, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
        active 
          ? 'bg-orange-50 border-orange-200 text-orange-700' 
          : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
      }`}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
      {count > 0 && (
        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
          active ? 'bg-orange-200 text-orange-800' : 'bg-gray-200 text-gray-800'
        }`}>
          {count}
        </span>
      )}
    </button>
  );
}

// Monthly Group Component
function MonthlyGroup({ monthGroup, selectedTransactions, onToggleTransaction }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Month Header */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {monthGroup.month_name}
          </h3>
          <div className="text-sm text-gray-600">
            <span className="font-medium">{monthGroup.transaction_count} transaction{monthGroup.transaction_count !== 1 ? 's' : ''}</span>
            <span className="mx-2">•</span>
            <span>{monthGroup.formatted_totals}</span>
          </div>
        </div>
      </div>

      {/* Column Headers */}
      <div className="bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-12 gap-4 px-6 py-3">
          <div className="col-span-1 text-xs font-medium text-gray-500 uppercase tracking-wider">
          </div>
          <div className="col-span-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
            Date
          </div>
          <div className="col-span-4 text-xs font-medium text-gray-500 uppercase tracking-wider">
            Description
          </div>
          <div className="col-span-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">
            Amount
          </div>
          <div className="col-span-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
            Category
          </div>
        </div>
      </div>

      {/* Transactions List */}
      <div className="divide-y divide-gray-100">
        {monthGroup.transactions.map((transaction) => (
          <TransactionRow
            key={transaction.id}
            transaction={transaction}
            selected={selectedTransactions.includes(transaction.id)}
            onToggleSelect={() => onToggleTransaction(transaction.id)}
          />
        ))}
      </div>
    </div>
  );
}

// Search Result Row Component
function SearchResultRow({ transaction, selected, onToggleSelect }) {
  const isCredit = transaction.amount > 0;
  const [showActions, setShowActions] = useState(false);

  const getCategoryStyle = (categoryName) => {
    const styles = {
      'INVESTMENT': 'bg-blue-100 text-blue-800 border-blue-200',
      'FOOD & DRINKS': 'bg-green-100 text-green-800 border-green-200',
      'PERSONAL': 'bg-purple-100 text-purple-800 border-purple-200',
      'CREDIT BILL': 'bg-gray-100 text-gray-800 border-gray-200',
      'MEDICAL': 'bg-red-100 text-red-800 border-red-200',
      'Untagged': 'bg-gray-50 text-gray-600 border-gray-200'
    };
    return styles[categoryName] || styles['Untagged'];
  };

  return (
    <div 
      className={`flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors ${
        selected ? 'bg-blue-50' : ''
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Checkbox */}
      <div className="flex-shrink-0">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggleSelect}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
      </div>

      {/* Date */}
      <div className="flex-shrink-0 text-right min-w-[100px]">
        <div className="text-sm font-medium text-gray-900">
          {new Date(transaction.date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
          })}
        </div>
      </div>

      {/* Amount */}
      <div className="flex-shrink-0 text-right min-w-[120px]">
        <div className={`text-lg font-semibold ${
          isCredit ? 'text-green-600' : 'text-gray-900'
        }`}>
          {isCredit ? '+' : '-'}{formatCAD(transaction.amount)}
        </div>
      </div>

      {/* Description */}
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-900 truncate">
          {transaction.description}
        </div>
      </div>

      {/* Category */}
      <div className="flex-shrink-0">
        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${
          getCategoryStyle(transaction.category_name)
        }`}>
          <div className="w-2 h-2 rounded-full bg-current opacity-60"></div>
          {transaction.category_name || 'Untagged'}
        </span>
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 w-8">
        {showActions && (
          <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}


// Transaction Row Component
function TransactionRow({ transaction, selected, onToggleSelect }) {
  const isCredit = transaction.is_credit;
  const [showActions, setShowActions] = useState(false);

  const getCategoryStyle = (categoryName) => {
    const styles = {
      'INVESTMENT': 'bg-blue-100 text-blue-800 border-blue-200',
      'FOOD & DRINKS': 'bg-green-100 text-green-800 border-green-200',
      'PERSONAL': 'bg-purple-100 text-purple-800 border-purple-200',
      'CREDIT BILL': 'bg-gray-100 text-gray-800 border-gray-200',
      'MEDICAL': 'bg-red-100 text-red-800 border-red-200',
      'Untagged': 'bg-gray-50 text-gray-600 border-gray-200'
    };
    return styles[categoryName] || styles['Untagged'];
  };

  return (
    <div 
      className={`grid grid-cols-12 gap-4 px-6 py-4 hover:bg-gray-50 transition-colors ${
        selected ? 'bg-blue-50' : ''
      }`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Checkbox */}
      <div className="col-span-1 flex items-center">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggleSelect}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
      </div>

      {/* Date */}
      <div className="col-span-2 flex items-center">
        <div className="text-sm font-medium text-gray-900">
          {new Date(transaction.date).toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
          })}
        </div>
      </div>

      {/* Name/Description */}
      <div className="col-span-4 flex items-center min-w-0">
        <div className="truncate">
          <div className="text-sm font-medium text-gray-900 truncate">
            {transaction.description}
          </div>
          {transaction.merchant && transaction.merchant !== transaction.description && (
            <div className="text-xs text-gray-500 truncate">
              {transaction.merchant}
            </div>
          )}
        </div>
      </div>

      {/* Amount */}
      <div className="col-span-3 flex items-center justify-end">
        <div className={`text-sm font-semibold ${
          isCredit ? 'text-green-600' : 'text-red-600'
        }`}>
          {isCredit ? '+' : '-'}{formatCAD(transaction.amount)}
        </div>
      </div>

      {/* Category */}
      <div className="col-span-2 flex items-center">
        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${
          getCategoryStyle(transaction.category_name)
        }`}>
          <div className="w-2 h-2 rounded-full bg-current opacity-60"></div>
          {transaction.category_name || 'Untagged'}
        </span>
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 w-8">
        {showActions && (
          <button className="p-1 text-gray-400 hover:text-gray-600 rounded">
            <MoreHorizontal className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}