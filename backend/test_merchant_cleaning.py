#!/usr/bin/env python3
"""
Test script for merchant name cleaning functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.parsers.canadian_banks import clean_merchant_name

def test_merchant_cleaning():
    """Test various merchant name cleaning scenarios."""
    
    test_cases = [
        # Your specific examples
        ("PRESTO AUTO RELOAD 123456789", "PRESTO AUTO"),
        ("WAL-MART SUPERCENTER#1007", "WAL-MART SUPERCENTER"),
        ("WALMART SUPERCENTER#1007KITCHENER", "WALMART SUPERCENTER"),
        
        # Store numbers and locations
        ("TIM HORTONS #5678", "TIM HORTONS"),
        ("STARBUCKS #1234 TORONTO", "STARBUCKS"),
        ("CANADIAN TIRE #123", "CANADIAN TIRE"),
        ("METRO #456 MISSISSAUGA", "METRO"),
        
        # Reference numbers
        ("UBER CANADA/UBEREATS*TRIP ABC123", "UBER CANADA/UBEREATS"),
        ("MCDONALDS REF: 987654321", "MCDONALDS"),
        ("SUBWAY ORDER XYZ789", "SUBWAY"),
        
        # Phone numbers and locations
        ("PIZZA PIZZA 416-555-1234 TORONTO ON", "PIZZA PIZZA"),
        ("ESSO 123 MAIN ST OTTAWA", "ESSO"),
        
        # Long reference numbers (6+ digits)
        ("SHELL 123456789", "SHELL"),
        ("PETRO CANADA 987654", "PETRO CANADA"),
        
        # Complex cases
        ("YASEENS SHAWARMA & GRIL#123 KITCHENER ON", "YASEENS SHAWARMA & GRIL"),
        ("SECOND CUP #789 WATERLOO 519-555-9999", "SECOND CUP"),
        
        # Edge cases
        ("SIMPLE NAME", "SIMPLE NAME"),  # No cleaning needed
        ("", ""),  # Empty string
        ("A", "A"),  # Single character
        
        # Province codes
        ("LOBLAWS MISSISSAUGA ON", "LOBLAWS"),
        ("SOBEYS HALIFAX NS", "SOBEYS"),
        ("NO FRILLS VANCOUVER BC", "NO FRILLS"),
        
        # Postal codes
        ("FOOD BASICS K1A 0A6", "FOOD BASICS"),
        ("HUSKY M5V 3A8 TORONTO", "HUSKY"),
    ]
    
    print("🧪 Testing Merchant Name Cleaning")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for input_name, expected in test_cases:
        result = clean_merchant_name(input_name)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | '{input_name}' → '{result}' (expected: '{expected}')")
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} tests failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_merchant_cleaning()
    sys.exit(0 if success else 1)