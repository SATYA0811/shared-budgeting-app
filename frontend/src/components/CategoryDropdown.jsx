/**
 * CategoryDropdown Component - Simple and Compact
 * 
 * Matches the UI design with parent categories and subcategories
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, Tag, Utensils, Car, ShoppingBag, ShoppingCart, Film, Calendar, MapPin, Heart, Dumbbell, Wrench, Receipt, Repeat, CreditCard, TrendingUp, Users, Shield, FileText, Wallet, Baby, MoreHorizontal, ArrowRightLeft, PiggyBank, Gift, Shirt, Zap, Hammer, Camera, Gauge, Paintbrush, FileStack, Scale, Truck, Settings } from 'lucide-react';
import api from '../services/api';

// Category icon mapping
const getCategoryIcon = (categoryName) => {
  const iconMap = {
    // Parent categories
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
    'Bill': Receipt,
    'Subscription': Repeat,
    'EMI': CreditCard,
    'Credit Bill': CreditCard,
    'Investment': TrendingUp,
    'Support': Users,
    'Insurance': Shield,
    'Tax': FileText,
    'Top-up': Wallet,
    'Children': Baby,
    'Misc.': MoreHorizontal,
    'Self Transfer': ArrowRightLeft,
    'Savings': PiggyBank,
    'Gift': Gift,
    
    // Child categories - Services (as shown in your image)
    'Laundry': Shirt,
    'Tailor': Users,
    'Courier': Truck,
    'Carpenter': Hammer,
    'Plumber': Wrench,
    'Mechanic': Settings,
    'Photographer': Camera,
    'Driver': Car,
    'Vehicle Wash': Car,
    'Electrician': Zap,
    'Painting': Paintbrush,
    'Xerox': FileStack,
    'Legal': Scale,
    'Advisor': Users,
    'Repair': Wrench,
    'Logistics': Truck,
    'Others': MoreHorizontal,
    
    // Other child categories
    'Eating out': Utensils,
    'Take Away': ShoppingBag,
    'Uber': Car,
    'Rapido': Car,
    'Clothes': Shirt,
    'Electronics': ShoppingBag,
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

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadCategories = async () => {
    try {
      const response = await api.categories.getCategories();
      console.log('Categories loaded:', response);
      setCategories(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error('Error loading categories:', error);
      setCategories([]);
    } finally {
      setLoading(false);
    }
  };

  // Group categories by parent-child relationship
  const getGroupedCategories = () => {
    if (!Array.isArray(categories) || categories.length === 0) {
      return [];
    }

    const parentCategories = categories.filter(cat => !cat.parent_id);
    const childCategories = categories.filter(cat => cat.parent_id);

    return parentCategories.map(parent => ({
      ...parent,
      children: childCategories.filter(child => child.parent_id === parent.id)
    }));
  };

  // Filter categories based on search term
  const getFilteredCategories = () => {
    const grouped = getGroupedCategories();
    if (!searchTerm) return grouped;

    return grouped.map(parent => {
      const matchingChildren = parent.children.filter(child =>
        child.name.toLowerCase().includes(searchTerm.toLowerCase())
      );

      const parentMatches = parent.name.toLowerCase().includes(searchTerm.toLowerCase());

      if (parentMatches || matchingChildren.length > 0) {
        return {
          ...parent,
          children: parentMatches ? parent.children : matchingChildren
        };
      }
      return null;
    }).filter(Boolean);
  };

  const [selectedCategory, setSelectedCategory] = useState(null);
  const [activeParentCategory, setActiveParentCategory] = useState(null);

  const handleCategorySelect = (category) => {
    setSelectedCategory(category);
    // Don't close dropdown immediately - let user click Done
  };

  const handleDone = () => {
    onChange(selectedCategory);
    setIsOpen(false);
    setSearchTerm('');
    setSelectedCategory(null);
    setActiveParentCategory(null);
  };

  const handleCancel = () => {
    setSelectedCategory(null);
    setActiveParentCategory(null);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleParentCategoryClick = (parentCategory) => {
    // Set this parent as active (for UI feedback)
    setActiveParentCategory(parentCategory);
    // Also set it as selected (in case user wants to select the parent directly)
    setSelectedCategory(parentCategory);
  };

  const getSelectedCategory = () => {
    if (!value) return null;
    return categories.find(cat => cat.id === value);
  };

  const filteredCategories = getFilteredCategories();

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full text-left px-2 py-1 text-xs border border-gray-300 rounded bg-white hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 min-h-6 flex items-center justify-between"
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {(() => {
            const selectedCategory = getSelectedCategory();
            if (selectedCategory) {
              const IconComponent = getCategoryIcon(selectedCategory.name);
              return <IconComponent className="w-3 h-3 text-gray-500 flex-shrink-0" />;
            }
            return <Tag className="w-3 h-3 text-gray-400 flex-shrink-0" />;
          })()}
          <span className={`truncate ${value ? "text-gray-900" : "text-gray-500"}`}>
            {getSelectedCategory()?.name || placeholder}
          </span>
        </div>
        <ChevronDown className={`h-3 w-3 text-gray-400 ml-1 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="fixed z-50 bg-white border border-gray-200 rounded-xl shadow-2xl w-96 max-h-[500px] overflow-hidden"
          style={{
            top: dropdownRef.current ? dropdownRef.current.getBoundingClientRect().bottom + 8 : 0,
            left: dropdownRef.current ? Math.max(8, dropdownRef.current.getBoundingClientRect().left - 150) : 0,
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}
        >
          {/* Search Input */}
          <div className="p-4 border-b border-gray-100">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search categories..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm bg-gray-50 focus:bg-white transition-colors"
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
                {filteredCategories.map((parentCategory) => (
                  <div key={parentCategory.id}>
                    {/* Parent Category Header */}
                    <button
                      type="button"
                      onClick={() => handleParentCategoryClick(parentCategory)}
                      className={`w-full px-4 py-3 bg-white border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                        activeParentCategory?.id === parentCategory.id || selectedCategory?.id === parentCategory.id || (selectedCategory === null && value === parentCategory.id) ? 'bg-blue-50 border-blue-200' : ''
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          parentCategory.name === 'Services' ? 'bg-purple-100' : 'bg-blue-100'
                        }`}>
                          {(() => {
                            const IconComponent = getCategoryIcon(parentCategory.name);
                            return <IconComponent className={`w-4 h-4 ${
                              parentCategory.name === 'Services' ? 'text-purple-600' : 'text-blue-600'
                            }`} />;
                          })()}
                        </div>
                        <div className="flex-1 text-left">
                          <span className="font-semibold text-gray-800 text-sm">
                            {parentCategory.name}
                          </span>
                          {parentCategory.description && (
                            <p className="text-xs text-gray-500 mt-0.5">
                              {parentCategory.description}
                            </p>
                          )}
                        </div>
                        {(selectedCategory?.id === parentCategory.id || (selectedCategory === null && value === parentCategory.id)) && (
                          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                        )}
                      </div>
                    </button>

                    {/* Child Categories - Grid Layout with Pills */}
                    <div className="p-4 bg-gray-50">
                      <div className="grid grid-cols-2 gap-2">
                        {parentCategory.children.map((childCategory) => (
                          <button
                            key={childCategory.id}
                            type="button"
                            onClick={() => handleCategorySelect(childCategory)}
                            className={`flex items-center gap-2 px-3 py-2 rounded-full text-xs font-medium transition-all duration-200 ${
                              selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id)
                                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                                : 'bg-white text-gray-700 border border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                            }`}
                          >
                            {(() => {
                              const IconComponent = getCategoryIcon(childCategory.name);
                              return <IconComponent className={`w-3.5 h-3.5 ${
                                selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id) ? 'text-blue-600' : 'text-gray-500'
                              }`} />;
                            })()}
                            <span className="truncate">
                              {childCategory.name}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
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

          {/* Action Buttons */}
          <div className="border-t border-gray-100 p-4 flex gap-3 bg-gray-50">
            <button
              type="button"
              onClick={handleCancel}
              className="flex-1 px-4 py-2.5 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDone}
              className="flex-1 px-4 py-2.5 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}