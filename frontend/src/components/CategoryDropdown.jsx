/**
 * CategoryDropdown Component - Simple and Compact
 * 
 * Matches the UI design with parent categories and subcategories
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, ChevronDown, Tag, Utensils, Car, ShoppingBag, ShoppingCart, Film, Calendar, MapPin, Heart, Dumbbell, Wrench, Receipt, Repeat, CreditCard, TrendingUp, Users, Shield, FileText, Wallet, Baby, MoreHorizontal, ArrowRightLeft, PiggyBank, Gift, Shirt, Zap, Hammer, Camera, Gauge, Paintbrush, FileStack, Scale, Truck, Settings, Coffee, Pizza, Wine, Soup, IceCream, Apple, Cherry, Fish, GlassWater, Scissors, Package, Droplets, Fuel, Bus, Bike, Train, Plane, Home, Building, Store, Gamepad2, Music, Headphones, Tv, Book, Briefcase, GraduationCap, Stethoscope, Pill, Hospital, Flower2, Diamond, Watch, Glasses, Footprints, Brush, Palette, Cake } from 'lucide-react';
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
    'Laundry': Droplets,
    'Tailor': Scissors,
    'Courier': Package,
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
    
    // Food & Drinks subcategories  
    'Eating out': Utensils,
    'Take Away': ShoppingBag,
    'Tea & Coffee': Coffee,
    'Fast Food': Pizza,
    'Snacks': Apple,
    'Swiggy': Utensils,
    'Zomato': Utensils,
    'Sweets': Cake,
    'Liquor': Wine,
    'Beverages': GlassWater,
    'Tiffin': Soup,
    'Pizza': Pizza,
    'Data': Fish,
    'Others': MoreHorizontal,
    
    // More Food & Drinks options
    'Candy': Cherry,
    'Meat': Fish,
    'Desserts': IceCream,
    'Bakery': Coffee,
    'Alcohol': Wine,
    'Beer': Wine,
    'Fruits': Apple,
    'Dairy': GlassWater,
    
    // Transport subcategories
    'Uber': Car,
    'Rapido': Car,
    'Auto': Car,
    'Cab': Car,
    'Bus': Bus,
    'Train': Train,
    'Flight': Plane,
    'Bike': Bike,
    'Fuel': Fuel,
    'Parking': Car,
    
    // Shopping subcategories
    'Clothes': Shirt,
    'Electronics': ShoppingBag,
    'Jewelry': Diamond,
    'Books': Book,
    'Footwear': Footprints,
    'Accessories': Watch,
    'Home Decor': Home,
    'Furniture': Building,
    'Toys': Gamepad2,
    'Sports': Dumbbell,
    
    // Entertainment subcategories
    'Movies': Film,
    'Music': Music,
    'Games': Gamepad2,
    'TV': Tv,
    'Concerts': Music,
    'Parties': Calendar,
    
    // Personal subcategories
    'Beauty': Brush,
    'Salon': Scissors,
    'Spa': Flower2,
    'Glasses': Glasses,
    'Healthcare': Stethoscope,
    'Medicine': Pill,
    'Hospital': Hospital,
    'Dental': Heart,
    
    // Education & Work
    'Education': GraduationCap,
    'Training': Book,
    'Office': Briefcase,
    'Stationery': FileText,
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
    if (selectedCategory) {
      onChange(selectedCategory);
    }
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

  // Get parent category for a child category
  const getParentCategoryName = (category) => {
    if (!category) return null;
    if (!category.parent_id) return category.name;
    const parent = categories.find(cat => cat.id === category.parent_id);
    return parent ? parent.name : category.name;
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Trigger Button - Styled as Badge */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500 ${
          value ? (() => {
            const selectedCategory = getSelectedCategory();
            const parentName = getParentCategoryName(selectedCategory);
            return getCategoryColor(selectedCategory?.name, parentName);
          })() : 'bg-gray-50 text-gray-500 border-gray-200 hover:bg-gray-100'
        }`}
      >
        {(() => {
          const selectedCategory = getSelectedCategory();
          if (selectedCategory) {
            // Always use the specific category's icon (whether parent or child)
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
            
            // If it's a subcategory, show the subcategory name
            // If it's a parent category, show the parent category name
            return selectedCategory.name;
          })()}
        </span>
        <ChevronDown className={`h-3 w-3 flex-shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          className="fixed z-50 bg-white border border-gray-200 rounded-xl shadow-2xl w-80 max-h-[480px] overflow-hidden"
          style={{
            top: dropdownRef.current ? dropdownRef.current.getBoundingClientRect().bottom + 8 : 0,
            left: dropdownRef.current ? Math.max(8, dropdownRef.current.getBoundingClientRect().left - 100) : 0,
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
                {filteredCategories.map((parentCategory) => (
                  <div key={parentCategory.id}>
                    {/* Parent Category Header */}
                    <button
                      type="button"
                      onClick={() => handleParentCategoryClick(parentCategory)}
                      className={`w-full px-3 py-2.5 bg-white hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                        activeParentCategory?.id === parentCategory.id || selectedCategory?.id === parentCategory.id || (selectedCategory === null && value === parentCategory.id) ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center ${getCategoryColor(parentCategory.name).replace('border-', 'border-0 ')}`}>
                        {(() => {
                          const IconComponent = getCategoryIcon(parentCategory.name);
                          return <IconComponent className="w-4 h-4" />;
                        })()}
                      </div>
                      <div className="flex-1 text-left">
                        <span className="font-medium text-gray-800 text-sm">
                          {parentCategory.name}
                        </span>
                      </div>
                      {(selectedCategory?.id === parentCategory.id || (selectedCategory === null && value === parentCategory.id)) && (
                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                      )}
                    </button>

                    {/* Child Categories - Vertical List Layout */}
                    {parentCategory.children.length > 0 && (
                      <div className="py-1">
                        {parentCategory.children.map((childCategory) => (
                          <button
                            key={childCategory.id}
                            type="button"
                            onClick={() => handleCategorySelect(childCategory)}
                            className={`w-full flex items-center gap-3 px-4 py-2 hover:bg-gray-50 transition-colors text-left ${
                              selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id)
                                ? 'bg-blue-50 border-l-2 border-blue-500' 
                                : 'border-l-2 border-transparent'
                            }`}
                          >
                            {(() => {
                              const IconComponent = getCategoryIcon(childCategory.name);
                              return <IconComponent className={`w-4 h-4 ${
                                selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id) ? 'text-blue-600' : 'text-gray-500'
                              }`} />;
                            })()}
                            <span className={`text-sm ${
                              selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id) ? 'text-blue-700 font-medium' : 'text-gray-700'
                            }`}>
                              {childCategory.name}
                            </span>
                            {(selectedCategory?.id === childCategory.id || (selectedCategory === null && value === childCategory.id)) && (
                              <div className="ml-auto w-2 h-2 rounded-full bg-blue-500"></div>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
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
          <div className="border-t border-gray-100 p-3 flex gap-2 bg-white">
            <button
              type="button"
              onClick={handleCancel}
              className="flex-1 px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDone}
              className="flex-1 px-3 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}