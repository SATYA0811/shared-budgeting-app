"""
Canadian Bank Statement Parsers

This module contains specialized parsers for Canadian banks including:
- CIBC (Canadian Imperial Bank of Commerce)
- RBC (Royal Bank of Canada) 
- American Express Canada
- TD Canada Trust
- BMO (Bank of Montreal)
- Scotiabank

Each parser handles the specific format and patterns used by these banks.
"""

import re
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime


def parse_cibc_transaction(line: str) -> Dict[str, Any]:
    """Parse CIBC transaction line."""
    # CIBC format: Date | Description | Debit | Credit | Balance
    # Example: "Jan 15  GROCERY STORE PURCHASE     45.67         2,345.22"
    
    patterns = {
        'date': r'([A-Za-z]{3}\s+\d{1,2})',  # Jan 15
        'amount': r'(\d{1,3}(?:,\d{3})*\.\d{2})',  # 1,234.56
        'description': r'([A-Z\s]+(?:PURCHASE|PAYMENT|TRANSFER|DEPOSIT|WITHDRAWAL|FEE))'
    }
    
    date_match = re.search(patterns['date'], line)
    amount_matches = re.findall(patterns['amount'], line)
    desc_match = re.search(patterns['description'], line)
    
    if date_match and amount_matches and desc_match:
        try:
            # Parse date (assume current year)
            date_str = date_match.group(1)
            current_year = datetime.now().year
            date_obj = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
            
            # Determine if debit or credit based on position
            # CIBC typically shows: Description | Debit | Credit | Balance
            amount_str = amount_matches[0].replace(',', '')
            amount = float(amount_str)
            
            # Check context to determine sign
            if 'PURCHASE' in line or 'FEE' in line or 'WITHDRAWAL' in line:
                amount = -abs(amount)
            elif 'DEPOSIT' in line or 'PAYMENT' in line and 'CARD PAYMENT' not in line:
                amount = abs(amount)
            else:
                # Default to negative for most transactions
                amount = -abs(amount)
                
            return {
                'date': date_obj,
                'description': desc_match.group(1).strip(),
                'amount': Decimal(str(amount)),
                'bank': 'CIBC'
            }
        except Exception:
            return None
    return None


def parse_rbc_transaction(line: str) -> Dict[str, Any]:
    """Parse RBC transaction line."""
    # RBC format: Date | Description | Withdrawals | Deposits | Balance
    # Example: "2025/01/15  INTERAC E-TRANSFER  25.00    2,320.55"
    
    patterns = {
        'date': r'(\d{4}/\d{1,2}/\d{1,2})',  # 2025/01/15
        'amount': r'(\d{1,3}(?:,\d{3})*\.\d{2})',
        'description': r'([A-Z\s-]+(?:TRANSFER|PAYMENT|PURCHASE|DEPOSIT|WITHDRAWAL|FEE))'
    }
    
    date_match = re.search(patterns['date'], line)
    amount_matches = re.findall(patterns['amount'], line)
    desc_match = re.search(patterns['description'], line)
    
    if date_match and amount_matches and desc_match:
        try:
            date_obj = datetime.strptime(date_match.group(1), "%Y/%m/%d")
            
            amount_str = amount_matches[0].replace(',', '')
            amount = float(amount_str)
            
            # RBC context-based signing
            if 'PURCHASE' in line or 'FEE' in line or 'WITHDRAWAL' in line:
                amount = -abs(amount)
            elif 'DEPOSIT' in line or 'TRANSFER' in line and 'E-TRANSFER' in line:
                amount = abs(amount)
            else:
                amount = -abs(amount)
                
            return {
                'date': date_obj,
                'description': desc_match.group(1).strip(),
                'amount': Decimal(str(amount)),
                'bank': 'RBC'
            }
        except Exception:
            return None
    return None


def parse_amex_canada_transaction(line: str) -> Dict[str, Any]:
    """Parse American Express Canada transaction line."""
    # AMEX format: Date | Description | Amount
    # Example: "JAN 15 GROCERY STORE TORONTO ON $45.67"
    
    patterns = {
        'date': r'([A-Z]{3}\s+\d{1,2})',  # JAN 15
        'amount': r'\$(\d{1,3}(?:,\d{3})*\.\d{2})',  # $123.45
        'description': r'([A-Z\s]+)(?:\s+[A-Z]{2}\s+)?\$'  # Description before amount
    }
    
    date_match = re.search(patterns['date'], line)
    amount_match = re.search(patterns['amount'], line)
    desc_match = re.search(patterns['description'], line)
    
    if date_match and amount_match and desc_match:
        try:
            date_str = date_match.group(1)
            current_year = datetime.now().year
            date_obj = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
            
            amount_str = amount_match.group(1).replace(',', '')
            amount = float(amount_str)
            
            # AMEX transactions are typically expenses (negative)
            amount = -abs(amount)
                
            return {
                'date': date_obj,
                'description': desc_match.group(1).strip(),
                'amount': Decimal(str(amount)),
                'bank': 'AMEX'
            }
        except Exception:
            return None
    return None


def parse_td_transaction(line: str) -> Dict[str, Any]:
    """Parse TD Canada Trust transaction line."""
    # TD format: Date | Description | Debit | Credit | Balance
    # Example: "15/01/2025  INTERAC PURCHASE  67.89    1,234.56"
    
    patterns = {
        'date': r'(\d{1,2}/\d{1,2}/\d{4})',  # 15/01/2025
        'amount': r'(\d{1,3}(?:,\d{3})*\.\d{2})',
        'description': r'([A-Z\s]+(?:PURCHASE|PAYMENT|TRANSFER|DEPOSIT|WITHDRAWAL|FEE))'
    }
    
    date_match = re.search(patterns['date'], line)
    amount_matches = re.findall(patterns['amount'], line)
    desc_match = re.search(patterns['description'], line)
    
    if date_match and amount_matches and desc_match:
        try:
            date_obj = datetime.strptime(date_match.group(1), "%d/%m/%Y")
            
            amount_str = amount_matches[0].replace(',', '')
            amount = float(amount_str)
            
            # TD context-based signing
            if 'PURCHASE' in line or 'FEE' in line or 'WITHDRAWAL' in line:
                amount = -abs(amount)
            elif 'DEPOSIT' in line or 'TRANSFER' in line and 'RECEIVED' in line:
                amount = abs(amount)
            else:
                amount = -abs(amount)
                
            return {
                'date': date_obj,
                'description': desc_match.group(1).strip(),
                'amount': Decimal(str(amount)),
                'bank': 'TD'
            }
        except Exception:
            return None
    return None


def detect_canadian_bank(text: str) -> str:
    """Detect which Canadian bank format the text uses."""
    text_upper = text.upper()
    
    if 'CIBC' in text_upper or 'CANADIAN IMPERIAL BANK' in text_upper:
        return 'CIBC'
    elif 'ROYAL BANK' in text_upper or 'RBC' in text_upper:
        return 'RBC'
    elif 'AMERICAN EXPRESS' in text_upper or 'AMEX' in text_upper:
        return 'AMEX'
    elif 'TD CANADA TRUST' in text_upper or 'TD BANK' in text_upper:
        return 'TD'
    elif 'BANK OF MONTREAL' in text_upper or 'BMO' in text_upper:
        return 'BMO'
    elif 'SCOTIABANK' in text_upper or 'SCOTIA' in text_upper:
        return 'SCOTIA'
    elif 'TANGERINE' in text_upper:
        return 'TANGERINE'
    
    return 'UNKNOWN'


def parse_canadian_bank_transactions(text: str) -> List[Dict[str, Any]]:
    """
    Parse transactions from Canadian bank statements.
    Auto-detects bank type and applies appropriate parser.
    """
    transactions = []
    bank_type = detect_canadian_bank(text)
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        transaction = None
        
        if bank_type == 'CIBC':
            transaction = parse_cibc_transaction(line)
        elif bank_type == 'RBC':
            transaction = parse_rbc_transaction(line)
        elif bank_type == 'AMEX':
            transaction = parse_amex_canada_transaction(line)
        elif bank_type == 'TD':
            transaction = parse_td_transaction(line)
        else:
            # Try all parsers if bank type unknown
            for parser in [parse_cibc_transaction, parse_rbc_transaction, 
                          parse_amex_canada_transaction, parse_td_transaction]:
                transaction = parser(line)
                if transaction:
                    break
                    
        if transaction:
            transactions.append(transaction)
    
    return transactions


def format_canadian_currency(amount: float) -> str:
    """Format amount as Canadian currency."""
    return f"${abs(amount):,.2f} CAD"


def parse_canadian_date_formats(date_str: str) -> datetime:
    """Parse various Canadian date formats."""
    formats = [
        "%d/%m/%Y",      # 15/01/2025
        "%Y/%m/%d",      # 2025/01/15
        "%b %d %Y",      # Jan 15 2025
        "%B %d, %Y",     # January 15, 2025
        "%d-%m-%Y",      # 15-01-2025
        "%Y-%m-%d",      # 2025-01-15
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    raise ValueError(f"Unable to parse date: {date_str}")