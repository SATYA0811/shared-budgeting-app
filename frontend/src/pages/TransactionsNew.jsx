/**
 * Modern Transactions Page - Matching the provided design
 * Features: Monthly grouping, advanced filtering, bulk selection
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, 
  ChevronDown,
  Upload,
  RotateCcw,
  Check,
  Calendar,
  Building2,
  Tag as TagIcon,
  Filter,
  SlidersHorizontal,
  TrendingUp,
  TrendingDown,
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
  const [showPDFUpload, setShowPDFUpload] = useState(false);
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [accountBalance, setAccountBalance] = useState(0);
  const [accounts, setAccounts] = useState([]);
  const [availableBanks, setAvailableBanks] = useState([]);
  const [banksLoading, setBanksLoading] = useState(true);
  const [dropdownStates, setDropdownStates] = useState({
    sort: false,
    time: false,
    bank: false
  });
  
  // Filter states
  const [filters, setFilters] = useState({
    sortBy: 'date',
    sortOrder: 'desc',
    timeFilter: 'all',
    bankFilter: 'all',
    hasCategory: null,
    year: new Date().getFullYear()
  });

  // Load data on component mount and filter changes
  useEffect(() => {
    loadTransactionData();
    loadFilterStats();
    loadAvailableBanks();
  }, [filters.year]);

  // Reload data when filters change (except year which is handled above)
  useEffect(() => {
    loadTransactionData();
  }, [filters.sortBy, filters.sortOrder, filters.timeFilter, filters.bankFilter, filters.hasCategory]);

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

  // Close dropdowns when clicking outside or pressing Escape
  useEffect(() => {
    const handleClickOutside = () => closeAllDropdowns();
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        closeAllDropdowns();
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const loadTransactionData = async () => {
    try {
      setLoading(true);
      const params = {
        year: filters.year,
        search: searchQuery || undefined,
        bank_filter: filters.bankFilter !== 'all' ? filters.bankFilter : undefined,
        has_category: filters.hasCategory,
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

  const loadAvailableBanks = async () => {
    try {
      setBanksLoading(true);
      const response = await api.banks.getAccounts();
      const bankNames = [...new Set(response.accounts.map(account => account.bank_name))];
      setAvailableBanks(bankNames);
    } catch (error) {
      console.error('Error loading banks:', error);
      // Fallback to hardcoded banks if API fails
      setAvailableBanks(['CIBC', 'RBC', 'AMEX', 'TD', 'Scotiabank']);
    } finally {
      setBanksLoading(false);
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
    // Data will auto-reload via useEffect
  };

  const resetFilters = () => {
    setFilters({
      sortBy: 'date',
      sortOrder: 'desc',
      timeFilter: 'all',
      bankFilter: 'all',
      hasCategory: null,
      year: new Date().getFullYear()
    });
    setSearchQuery('');
    closeAllDropdowns();
    // Data will auto-reload via useEffect when filters change
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

  const toggleDropdown = (dropdownName) => {
    setDropdownStates(prev => ({
      ...Object.keys(prev).reduce((acc, key) => ({ ...acc, [key]: false }), {}),
      [dropdownName]: !prev[dropdownName]
    }));
  };

  const closeAllDropdowns = () => {
    setDropdownStates({
      sort: false,
      time: false,
      bank: false
    });
  };

  const getSortOptions = () => [
    { value: 'date_desc', label: 'Newest first' },
    { value: 'date_asc', label: 'Oldest first' },
    { value: 'amount_desc', label: 'Highest amount' },
    { value: 'amount_asc', label: 'Lowest amount' }
  ];

  const getTimeOptions = () => [
    { value: 'all', label: 'All time' },
    { value: '7days', label: 'Last 7 days' },
    { value: '30days', label: 'Last 30 days' },
    { value: '90days', label: 'Last 90 days' },
    { value: '6months', label: 'Last 6 months' },
    { value: '1year', label: 'Last year' }
  ];

  const getBankOptions = () => [
    { value: 'all', label: 'All banks' },
    ...availableBanks.map(bank => ({ value: bank, label: bank }))
  ];

  const getCurrentSortLabel = () => {
    const sortKey = `${filters.sortBy}_${filters.sortOrder}`;
    const option = getSortOptions().find(opt => opt.value === sortKey);
    return option ? option.label : 'Newest first';
  };

  const handleSortSelect = (value) => {
    const [sortBy, sortOrder] = value.split('_');
    setFilters(prev => ({ ...prev, sortBy, sortOrder }));
    closeAllDropdowns();
    // Data will auto-reload via useEffect
  };

  const handleTimeSelect = (value) => {
    handleFilterChange('timeFilter', value);
    closeAllDropdowns();
  };

  const handleBankSelect = (value) => {
    handleFilterChange('bankFilter', value);
    closeAllDropdowns();
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.sortBy !== 'date' || filters.sortOrder !== 'desc') count++;
    if (filters.timeFilter !== 'all') count++;
    if (filters.bankFilter !== 'all') count++;
    if (filters.hasCategory !== null) count++;
    if (searchQuery.trim()) count++;
    return count;
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
            <DropdownFilter
              icon={<SlidersHorizontal className="h-4 w-4" />}
              label={getCurrentSortLabel()}
              active={filters.sortOrder !== 'desc' || filters.sortBy !== 'date'}
              isOpen={dropdownStates.sort}
              onToggle={() => toggleDropdown('sort')}
              options={getSortOptions()}
              onSelect={handleSortSelect}
              currentValue={`${filters.sortBy}_${filters.sortOrder}`}
            />

            {/* Time Filter */}
            <DropdownFilter
              icon={<Calendar className="h-4 w-4" />}
              label={getTimeFilterLabel()}
              active={filters.timeFilter !== 'all'}
              isOpen={dropdownStates.time}
              onToggle={() => toggleDropdown('time')}
              options={getTimeOptions()}
              onSelect={handleTimeSelect}
              currentValue={filters.timeFilter}
            />

            {/* Bank Filter */}
            <DropdownFilter
              icon={banksLoading ? <Loader className="h-4 w-4 animate-spin" /> : <Building2 className="h-4 w-4" />}
              label={banksLoading ? 'Loading banks...' : getBankFilterLabel()}
              active={filters.bankFilter !== 'all'}
              isOpen={dropdownStates.bank && !banksLoading}
              onToggle={() => !banksLoading && toggleDropdown('bank')}
              options={getBankOptions()}
              onSelect={handleBankSelect}
              currentValue={filters.bankFilter}
              disabled={banksLoading}
            />

            {/* Category Filter */}
            <FilterBadge
              icon={<TagIcon className="h-4 w-4" />}
              label="Untagged"
              count={filterStats?.categorization?.untagged || 0}
              active={filters.hasCategory === false}
              onClick={() => handleFilterChange('hasCategory', filters.hasCategory === false ? null : false)}
            />


            {/* Active Filters Count */}
            {getActiveFiltersCount() > 0 && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-100 text-blue-800 rounded-lg text-sm font-medium">
                <Filter className="h-4 w-4" />
                {getActiveFiltersCount()} filter{getActiveFiltersCount() !== 1 ? 's' : ''} active
              </div>
            )}

            {/* Reset Filters */}
            <button
              onClick={resetFilters}
              disabled={getActiveFiltersCount() === 0}
              className="ml-auto flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

// Dropdown Filter Component
function DropdownFilter({ icon, label, active, isOpen, onToggle, options, onSelect, currentValue, disabled }) {
  return (
    <div className="relative inline-block" onClick={(e) => e.stopPropagation()}>
      <button
        onClick={onToggle}
        disabled={disabled}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
          disabled 
            ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
            : active 
              ? 'bg-blue-50 border-blue-200 text-blue-700' 
              : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
        }`}
      >
        {icon}
        <span className="text-sm font-medium">{label}</span>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <div 
          className="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-xl min-w-[200px] whitespace-nowrap"
          style={{ 
            position: 'absolute', 
            zIndex: 9999,
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}
        >
          {options.map((option, index) => (
            <button
              key={option.value}
              onClick={() => onSelect(option.value)}
              className={`w-full text-left px-4 py-2 text-sm transition-colors relative block ${
                index === 0 ? 'rounded-t-lg' : ''
              } ${
                index === options.length - 1 ? 'rounded-b-lg' : ''
              } ${
                currentValue === option.value 
                  ? 'bg-blue-50 text-blue-700 font-medium' 
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              {option.label}
              {currentValue === option.value && (
                <Check className="h-4 w-4 absolute right-3 top-1/2 transform -translate-y-1/2 text-blue-600" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Filter Button Component (kept for non-dropdown filters)
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
function MonthlyGroup({ monthGroup }) {
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
          <div className="col-span-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
            Date
          </div>
          <div className="col-span-5 text-xs font-medium text-gray-500 uppercase tracking-wider">
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
          />
        ))}
      </div>
    </div>
  );
}

// Search Result Row Component
function SearchResultRow({ transaction }) {
  const isCredit = transaction.amount > 0;

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
      className="flex items-center gap-4 px-6 py-4 hover:bg-gray-50 transition-colors"
    >
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
    </div>
  );
}


// Transaction Row Component
function TransactionRow({ transaction }) {
  const isCredit = transaction.is_credit;

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
      className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-gray-50 transition-colors"
    >
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
      <div className="col-span-5 flex items-center min-w-0">
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
    </div>
  );
}