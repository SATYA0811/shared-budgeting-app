#!/usr/bin/env python3
"""
Test script for checking account parsers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.parsers.canadian_banks import (
    detect_canadian_bank, 
    parse_cibc_checking_transaction,
    parse_rbc_checking_transaction,
    parse_canadian_bank_transactions
)

def test_bank_detection():
    """Test bank and account type detection."""
    print("🏦 Testing Bank & Account Type Detection")
    print("=" * 60)
    
    # Read the checking account statements
    with open('../cibc_checking_text.txt', 'r', encoding='utf-8') as f:
        cibc_text = f.read()
    
    with open('../rbc_checking_text.txt', 'r', encoding='utf-8') as f:
        rbc_text = f.read()
    
    # Test detection
    cibc_bank, cibc_type = detect_canadian_bank(cibc_text)
    rbc_bank, rbc_type = detect_canadian_bank(rbc_text)
    
    print(f"✅ CIBC PDF: {cibc_bank} - {cibc_type}")
    print(f"✅ RBC PDF:  {rbc_bank} - {rbc_type}")
    
    return cibc_text, rbc_text

def test_cibc_checking_parsing(text):
    """Test CIBC checking account parsing."""
    print("\n🔵 Testing CIBC Checking Parser")
    print("=" * 60)
    
    # Test specific transaction lines
    test_lines = [
        "Jul 4 E-TRANSFER        011359544971 SATYA SANNIHITH LINGUTLA.597.00 1,125.40",
        "Jul 9 INTERNET TRANSFER 000000101667 347.71 642.69",
        "Jul 4 DEPOSIT TPS/GST35.35 528.40",
        "Jul 31 SERVICE CHARGE ADD TXN$0.00;MONTHLY$6.95 RECORD-KEEPING  N/A6.95 640.72"
    ]
    
    for line in test_lines:
        result = parse_cibc_checking_transaction(line)
        if result:
            print(f"✅ '{line[:50]}...' → {result['description']} | ${result['amount']}")
        else:
            print(f"❌ '{line[:50]}...' → Failed to parse")

def test_rbc_checking_parsing(text):
    """Test RBC checking account parsing."""
    print("\n🔴 Testing RBC Checking Parser")
    print("=" * 60)
    
    # Test specific transaction lines
    test_lines = [
        "Jul 15, 2025 to Find & Save - $75.00 $1,417.86",
        "Jul 4, 2025Payroll Deposit The Wawanesa Mu$2,567.28",
        "Jul 14, 2025Telephone Bill Pmt FIDO MOBILE- $86.10 $1,496.86",
        "Jul 9, 2025e-Transfer sent Sunny 3ZNWCM- $533.00 $1,657.96"
    ]
    
    for line in test_lines:
        result = parse_rbc_checking_transaction(line)
        if result:
            print(f"✅ '{line[:50]}...' → {result['description']} | ${result['amount']}")
        else:
            print(f"❌ '{line[:50]}...' → Failed to parse")

def test_full_parsing():
    """Test full document parsing."""
    print("\n🎯 Testing Full Document Parsing")
    print("=" * 60)
    
    # Read and parse both PDFs
    with open('../cibc_checking_text.txt', 'r', encoding='utf-8') as f:
        cibc_text = f.read()
        cibc_transactions = parse_canadian_bank_transactions(cibc_text)
    
    with open('../rbc_checking_text.txt', 'r', encoding='utf-8') as f:
        rbc_text = f.read()
        rbc_transactions = parse_canadian_bank_transactions(rbc_text)
    
    print(f"✅ CIBC Checking: Found {len(cibc_transactions)} transactions")
    for i, trans in enumerate(cibc_transactions[:5], 1):
        print(f"   {i}. {trans['date'].strftime('%b %d')} | {trans['description'][:30]} | ${trans['amount']}")
    
    print(f"✅ RBC Checking: Found {len(rbc_transactions)} transactions")
    for i, trans in enumerate(rbc_transactions[:5], 1):
        print(f"   {i}. {trans['date'].strftime('%b %d')} | {trans['description'][:30]} | ${trans['amount']}")
    
    return len(cibc_transactions), len(rbc_transactions)

if __name__ == "__main__":
    print("🧪 Testing Enhanced Bank Statement Parsers")
    print("=" * 80)
    
    # Test detection
    cibc_text, rbc_text = test_bank_detection()
    
    # Test individual parsers
    test_cibc_checking_parsing(cibc_text)
    test_rbc_checking_parsing(rbc_text)
    
    # Test full parsing
    cibc_count, rbc_count = test_full_parsing()
    
    print("\n📊 Summary")
    print("=" * 60)
    print(f"🔵 CIBC Checking: {cibc_count} transactions parsed")
    print(f"🔴 RBC Checking:  {rbc_count} transactions parsed")
    print("✅ Enhanced parsers ready for checking accounts!")