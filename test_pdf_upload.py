#!/usr/bin/env python3
"""
Test script for PDF upload functionality
This script tests the PDF extraction independently to debug issues
"""

import pdfplumber
import sys
import os

def test_pdf_extraction(pdf_path):
    """Test PDF text extraction"""
    print(f"Testing PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                print(f"\n=== PAGE {page_num + 1} ===")
                page_text = page.extract_text()
                if page_text:
                    print(f"Text length: {len(page_text)} characters")
                    print("First 500 characters:")
                    print(page_text[:500])
                    print("...")
                else:
                    print("No text found on this page")
                    
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

def test_bank_detection():
    """Test bank detection with sample text"""
    from backend.app.parsers.canadian_banks import detect_canadian_bank, parse_canadian_bank_transactions
    
    # Test CIBC format
    cibc_sample = """
    CIBC BANK STATEMENT
    Jan 15  GROCERY STORE PURCHASE     45.67         2,345.22
    Jan 16  INTERAC E-TRANSFER         25.00         2,370.22
    """
    
    print(f"CIBC detection: {detect_canadian_bank(cibc_sample)}")
    transactions = parse_canadian_bank_transactions(cibc_sample)
    print(f"CIBC transactions found: {len(transactions)}")
    
    # Test RBC format
    rbc_sample = """
    ROYAL BANK OF CANADA
    2025/01/15  INTERAC E-TRANSFER  25.00    2,320.55
    2025/01/16  GROCERY PURCHASE    45.67    2,274.88
    """
    
    print(f"RBC detection: {detect_canadian_bank(rbc_sample)}")
    transactions = parse_canadian_bank_transactions(rbc_sample)
    print(f"RBC transactions found: {len(transactions)}")
    
    # Test AMEX format
    amex_sample = """
    AMERICAN EXPRESS CANADA
    JAN 15 GROCERY STORE TORONTO ON $45.67
    JAN 16 GAS STATION VANCOUVER BC $65.43
    """
    
    print(f"AMEX detection: {detect_canadian_bank(amex_sample)}")
    transactions = parse_canadian_bank_transactions(amex_sample)
    print(f"AMEX transactions found: {len(transactions)}")

if __name__ == "__main__":
    print("PDF Upload Test Script")
    print("=" * 40)
    
    # Test bank detection first
    print("\n1. Testing bank detection patterns:")
    test_bank_detection()
    
    # Test actual PDF if provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"\n2. Testing PDF extraction:")
        test_pdf_extraction(pdf_path)
    else:
        print(f"\n2. Testing available PDF files:")
        # Test available PDFs
        pdf_files = ["test.pdf", "shared_budgeting_app_plan.pdf"]
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                test_pdf_extraction(pdf_file)
                break
        else:
            print("No PDF files found to test")
    
    print("\nTest complete!")