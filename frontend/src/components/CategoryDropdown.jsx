/**
 * CategoryDropdown Component - Simple and Compact
 * 
 * Displays categories in a flat list for easy selection
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, Tag, Utensils, Car, ShoppingBag, ShoppingCart, Film, Calendar, MapPin, Heart, Dumbbell, Wrench, CreditCard, TrendingUp, Users, Shield, FileText, Wallet, Baby, MoreHorizontal, ArrowRightLeft, PiggyBank, Gift, DollarSign, CreditCard as BillIcon, Tv as SubscriptionIcon } from 'lucide-react';
import api from '../services/api';

// Category icon mapping
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    // Main categories
    'Income': DollarSign,
    'Food & Drinks': Utensils,
    'Transport': Car,
    'Shopping': ShoppingBag,
    'Groceries': ShoppingCart,
    'Entertainment': Film,
    'Events': Calendar,
    'Travel': MapPin,
    'Medical': Heart,
    'Personal': Users,
    'Fitness': Dumbbell,
    'Services': Wrench,
    'Bills': BillIcon,
    'Subscriptions': SubscriptionIcon,
    'EMI': CreditCard,
    'Credit Bill': CreditCard,
    'Investment': TrendingUp,
    'Support': Users,
    'Insurance': Shield,
    'Tax': FileText,
    'Top-up': Wallet,
    'Children': Baby,
    'Miscellaneous': MoreHorizontal,
    'Self Transfer': ArrowRightLeft,
    'Savings': PiggyBank,
    'Gifts': Gift,
  };

  const IconComponent = iconMap[categoryName] || Tag;
  return IconComponent;
};

export default function CategoryDropdown({ 
  value, 
  onChange, 
  placeholder = "Untagged",
  className = ""
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, right: 'auto' });
  const dropdownRef = useRef(null);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    const handleResize = () => {
      if (isOpen) {
        calculateDropdownPosition();
      }
    };

    const handleScroll = () => {
      if (isOpen) {
        calculateDropdownPosition();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleScroll, true);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleScroll, true);
    };
  }, [isOpen]);

  const loadCategories = async () => {
    try {
      const response = await api.categories.getCategories();
      setCategories(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  // Get categories as a flat list (no parent-child grouping)
  const getFlatCategories = () => {
    if (!Array.isArray(categories) || categories.length === 0) {
      return [];
    }
    return categories;
  };

  // Filter categories based on search term
  const getFilteredCategories = () => {
    const flatCategories = getFlatCategories();
    if (!searchTerm) return flatCategories;

    return flatCategories.filter(category =>
      category.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };


  const handleCategorySelect = (category) => {
    onChange(category);
    setIsOpen(false);
    setSearchTerm('');
  };


  const handleCategoryClick = (category) => {
    handleCategorySelect(category);
  };

  // Calculate dropdown position to prevent overflow
  const calculateDropdownPosition = () => {
    if (!dropdownRef.current) return;
    
    const rect = dropdownRef.current.getBoundingClientRect();
    const dropdownWidth = 320; // width of dropdown (w-80 = 20rem = 320px)
    const dropdownHeight = 480; // max-height of dropdown
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const padding = 8; // minimum padding from viewport edge
    
    // For mobile devices, use full width with padding
    const isMobile = viewportWidth < 640; // sm breakpoint
    const effectiveWidth = isMobile ? Math.min(dropdownWidth, viewportWidth - padding * 2) : dropdownWidth;
    
    let position = {
      top: rect.bottom + padding,
      left: rect.left,
      right: 'auto',
      width: isMobile ? effectiveWidth : undefined
    };
    
    // For mobile, center the dropdown
    if (isMobile) {
      position.left = (viewportWidth - effectiveWidth) / 2;
    } else {
      // Check if dropdown would overflow right edge
      if (rect.left + dropdownWidth > viewportWidth - padding) {
        // Position from right edge instead
        position.left = 'auto';
        position.right = viewportWidth - rect.right;
        
        // If still overflowing, align to right edge of viewport
        if (position.right + dropdownWidth > viewportWidth - padding) {
          position.left = viewportWidth - dropdownWidth - padding;
          position.right = 'auto';
        }
      }
    }
    
    // Check if dropdown would overflow bottom edge
    if (rect.bottom + dropdownHeight > viewportHeight - padding) {
      // Position above the trigger instead
      position.top = rect.top - dropdownHeight - padding;
      
      // If still overflowing top, position within viewport
      if (position.top < padding) {
        position.top = padding;
      }
    }
    
    setDropdownPosition(position);
  };

  const getSelectedCategory = () => {
    if (!value) return null;
    const selected = categories.find(cat => cat.id === value);
    return selected;
  };

  const filteredCategories = getFilteredCategories();

  // Get category color based on parent category
  const getCategoryColor = (categoryName, parentName = null) => {
    const parentCategoryName = parentName || categoryName;
    const colorMap = {
      'Food & Drinks': 'bg-orange-100 text-orange-700 border-orange-200',
      'Transport': 'bg-blue-100 text-blue-700 border-blue-200',
      'Shopping': 'bg-purple-100 text-purple-700 border-purple-200',
      'Groceries': 'bg-green-100 text-green-700 border-green-200',
      'Entertainment': 'bg-pink-100 text-pink-700 border-pink-200',
      'Services': 'bg-indigo-100 text-indigo-700 border-indigo-200',
      'Bill': 'bg-red-100 text-red-700 border-red-200',
      'Medical': 'bg-emerald-100 text-emerald-700 border-emerald-200',
      'Personal': 'bg-cyan-100 text-cyan-700 border-cyan-200',
      'Investment': 'bg-yellow-100 text-yellow-700 border-yellow-200',
    };
    return colorMap[parentCategoryName] || 'bg-gray-100 text-gray-700 border-gray-200';
  };


  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button - Styled as Badge */}
      <button
        type="button"
        onClick={() => {
          if (!isOpen) {
            calculateDropdownPosition();
          }
          setIsOpen(!isOpen);
        }}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500 ${
          value ? (() => {
            const selectedCategory = getSelectedCategory();
            return getCategoryColor(selectedCategory?.name);
          })() : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100'
        }`}
      >
        {(() => {
          const selectedCategory = getSelectedCategory();
          if (selectedCategory) {
            const IconComponent = getCategoryIcon(selectedCategory.name);
            return <IconComponent className="w-3.5 h-3.5 flex-shrink-0" />;
          }
          return <Tag className="w-3.5 h-3.5 flex-shrink-0" />;
        })()}
        <span className="truncate">
          {(() => {
            const selectedCategory = getSelectedCategory();
            if (!selectedCategory) {
              return placeholder;
            }
            return selectedCategory.name;
          })()}
        </span>
        <ChevronDown className={`h-3 w-3 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="fixed z-50 bg-white border border-gray-200 rounded-xl shadow-2xl max-h-[480px] overflow-hidden"
          style={{
            top: dropdownPosition.top,
            left: dropdownPosition.left !== 'auto' ? dropdownPosition.left : undefined,
            right: dropdownPosition.right !== 'auto' ? dropdownPosition.right : undefined,
            width: dropdownPosition.width || '320px',
            boxShadow: '0 20px 40px -12px rgba(0, 0, 0, 0.25)'
          }}
        >
          {/* Search Input */}
          <div className="p-3 border-b border-gray-100">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder='Search "Grooming"'
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-gray-50 focus:bg-white transition-colors"
                autoFocus
              />
            </div>
          </div>

          {/* Categories List */}
          <div className="max-h-72 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500 text-sm">Loading categories...</div>
            ) : filteredCategories.length > 0 ? (
              <div className="py-1">
                {filteredCategories.map((category) => (
                  <button
                    key={category.id}
                    type="button"
                    onClick={() => handleCategoryClick(category)}
                    className={`w-full px-3 py-2.5 bg-white hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                      value === category.id ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center ${getCategoryColor(category.name).replace('border-', 'border-0 ')}`}>
                      {(() => {
                        const IconComponent = getCategoryIcon(category.name);
                        return <IconComponent className="w-4 h-4" />;
                      })()}
                    </div>
                    <div className="flex-1 text-left">
                      <span className="font-medium text-gray-800 text-sm">
                        {category.name}
                      </span>
                      {category.description && (
                        <p className="text-xs text-gray-500 mt-0.5">{category.description}</p>
                      )}
                    </div>
                    {value === category.id && (
                      <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    )}
                  </button>
                ))}
              </div>
            ) : categories.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <p className="text-sm">Loading categories...</p>
                <p className="text-xs mt-1">Please wait</p>
              </div>
            ) : (
              <div className="p-4 text-center text-gray-500">
                <p className="text-sm">No categories found</p>
                {searchTerm && <p className="text-xs mt-1">Try a different search term</p>}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );
}