#!/usr/bin/env python3
"""
Test the new auto-categorization for e-transfers
"""

from app.parsers.canadian_banks import (
    auto_categorize_transaction, 
    parse_cibc_checking_transaction,
    parse_rbc_checking_transaction
)

def test_auto_categorization():
    """Test automatic categorization of e-transfers."""
    print("🎯 Testing Auto-Categorization")
    print("=" * 60)
    
    test_cases = [
        # E-Transfer cases
        ("E-TRANSFER SATYA SANNIHITH LINGUTLA", 597.00, "Should be Self (28)"),
        ("e-Transfer sent Sunny 3ZNWCM", -533.00, "Should be E-Transfer (27)"),
        ("E-TRANSFER Kumaresh@owner", -900.00, "Should be E-Transfer (27)"),
        ("INTERNET TRANSFER 000000101667", -347.71, "Should be Self (28)"),
        
        # Bill payments
        ("Telephone Bill Pmt FIDO MOBILE", -86.10, "Should be Bills (13)"),
        ("SERVICE CHARGE MONTHLY", -6.95, "Should be Bills (13)"),
        ("Misc Payment AMEX BILL PYMT", -552.29, "Should be Bills (13)"),
        
        # Income
        ("Payroll Deposit The Wawanesa Mu", 2567.28, "Should be Income (1)"),
        
        # Unknown
        ("COSTCO WHOLESALE", -125.50, "Should be None")
    ]
    
    for description, amount, expected in test_cases:
        category_id = auto_categorize_transaction(description, amount, "TEST")
        print(f"✅ '{description[:40]:<40}' → Category {category_id} | {expected}")

def test_checking_parsers_with_categorization():
    """Test checking parsers with auto-categorization."""
    print("\n🔵 Testing CIBC Checking Parser with Categorization")
    print("=" * 60)
    
    cibc_lines = [
        "Jul 4 E-TRANSFER        011359544971 SATYA SANNIHITH LINGUTLA.597.00 1,125.40",
        "Jul 9 INTERNET TRANSFER 000000101667 347.71 642.69",
        "Jul 31 SERVICE CHARGE ADD TXN$0.00;MONTHLY$6.95 RECORD-KEEPING  N/A6.95 640.72"
    ]
    
    for line in cibc_lines:
        result = parse_cibc_checking_transaction(line)
        if result:
            cat_id = result.get('auto_category_id', 'None')
            print(f"✅ {result['description'][:30]:<30} | ${result['amount']:<8} | Cat: {cat_id}")
    
    print("\n🔴 Testing RBC Checking Parser with Categorization")
    print("=" * 60)
    
    rbc_lines = [
        "Jul 9, 2025e-Transfer sent Sunny 3ZNWCM- $533.00 $1,657.96",
        "Jul 14, 2025Telephone Bill Pmt FIDO MOBILE- $86.10 $1,496.86",
        "Jul 4, 2025Payroll Deposit The Wawanesa Mu$2,567.28"
    ]
    
    for line in rbc_lines:
        result = parse_rbc_checking_transaction(line)
        if result:
            cat_id = result.get('auto_category_id', 'None')
            print(f"✅ {result['description'][:30]:<30} | ${result['amount']:<8} | Cat: {cat_id}")

if __name__ == "__main__":
    print("🧪 Testing Enhanced Auto-Categorization System")
    print("=" * 80)
    test_auto_categorization()
    test_checking_parsers_with_categorization()
    
    print("\n📊 Category Reference:")
    print("=" * 40)
    print("27. Interac E-Transfer")
    print("28. Interac E-Transfer Self") 
    print("13. Bills")
    print(" 1. Income")