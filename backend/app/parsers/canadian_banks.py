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
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime


def clean_merchant_name(merchant_name: str) -> str:
    """
    Clean merchant name by removing location codes, reference numbers, and store IDs.
    
    Examples:
    - "PRESTO AUTO RELOAD 123456789" → "PRESTO AUTO"
    - "WAL-MART SUPERCENTER#1007" → "WAL-MART SUPERCENTER"
    - "UBER CANADA/UBEREATS*TRIP ABC123" → "UBER CANADA/UBEREATS"
    - "STARBUCKS #1234 TORONTO" → "STARBUCKS"
    - "TIM HORTONS #5678" → "TIM HORTONS"
    - "INTERNET TRANSFER 000000101667" → "INTERNET TRANSFER"
    """
    if not merchant_name:
        return merchant_name
    
    name = merchant_name.strip()
    
    # Special cases: Banking transactions that should preserve their type
    banking_patterns = [
        r'^(INTERNET\s+TRANSFER|E-TRANSFER|ETRANSFER|WIRE\s+TRANSFER|ACH\s+TRANSFER|ONLINE\s+TRANSFER)',
        r'^(PAYROLL\s+DEPOSIT|DIRECT\s+DEPOSIT|SALARY\s+DEPOSIT)',
        r'^(SERVICE\s+CHARGE|MONTHLY\s+FEE|OVERDRAFT\s+FEE)',
        r'^(BILL\s+PAYMENT|TELEPHONE\s+BILL|MISC\s+PAYMENT)'
    ]
    
    # Check if this is a banking transaction
    for pattern in banking_patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            # For banking transactions, just remove reference numbers at the end
            # but preserve the transaction type
            transaction_type = match.group(1)
            # Remove reference numbers (6+ digits) at the end only
            cleaned = re.sub(r'\s+\d{6,}.*$', '', name).strip()
            return cleaned
    
    # Pattern-based cleaning rules
    patterns_to_remove = [
        # Store/location numbers with # symbol
        r'#\d+.*$',                          # "#1007", "#1234 TORONTO", etc.
        
        # Reference/transaction numbers (long digit sequences)
        r'\s+\d{6,}.*$',                     # " 123456789" (6+ digits at end)
        
        # Location codes in parentheses
        r'\s*\([^)]*\).*$',                  # " (LOCATION123)"
        
        # Specific patterns for known merchants
        r'\*TRIP\s+[A-Z0-9]+.*$',           # Uber trip codes "*TRIP ABC123"
        r'\*ORDER\s+[A-Z0-9]+.*$',          # Order codes "*ORDER XYZ789"
        r'\s+REF\s*[:#]?\s*[A-Z0-9]+.*$',   # Reference numbers "REF: ABC123"
        r'\s+TRANS\s*[:#]?\s*[A-Z0-9]+.*$', # Transaction IDs "TRANS: 123"
        r'\s+AUTH\s*[:#]?\s*[A-Z0-9]+.*$',  # Auth codes "AUTH: 456"
        
        # Impark specific patterns
        r'\d{8}H.*$',                       # Impark codes like "00120172H"
        r'\d{7,}[A-Z].*$',                  # Similar patterns with letter suffix
        
        # General number patterns (more aggressive)
        r'\d{5,}.*$',                       # 5+ consecutive digits anywhere
        r'\s+\d{3,4}\s*[A-Z]*\s*$',       # 3-4 digits at end with optional letters
        
        # City names (common Canadian cities) - only if at the end
        r'\s+(TORONTO|MISSISSAUGA|OTTAWA|CALGARY|VANCOUVER|MONTREAL|WINNIPEG|KITCHENER|HAMILTON|LONDON|MARKHAM|VAUGHAN|RICHMOND|BURNABY|SASKATOON|HALIFAX|VICTORIA|WINDSOR|OSHAWA|GATINEAU|LONGUEUIL|SHERBROOKE|SAGUENAY|LEVIS|KELOWNA|ABBOTSFORD|COQUITLAM|TERREBONNE|SAANICH|RICHMOND HILL|THUNDER BAY|CAMBRIDGE|WATERLOO|GUELPH|SUDBURY|BRANTFORD|LAVAL)(\s+[A-Z]{2})?.*$',
        
        # Province codes at the end
        r'\s+(ON|BC|AB|QC|MB|SK|NS|NB|PE|NL|YT|NT|NU).*$',
        
        # Phone numbers
        r'\s+\d{3}[-.]?\d{3}[-.]?\d{4}.*$',  # Phone numbers
        
        # Contact info patterns
        r'\s+\d{3}[-.]?\d{3}[-.]?\d{4}.*$',  # Phone: 844-309-1028
        
        # Postal codes (Canadian format)
        r'\s+[A-Z]\d[A-Z]\s?\d[A-Z]\d.*$',  # "K1A 0A6"
    ]
    
    # Apply cleaning patterns
    for pattern in patterns_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    
    # Specific merchant name corrections
    merchant_corrections = {
        # Transit systems
        'PRESTO AUTO RELOAD': 'PRESTO AUTO',
        'PRESTO AUTOLOAD': 'PRESTO AUTO',
        'PRESTO AUTO': 'PRESTO AUTO',
        
        # Parking services
        'IMPARK': 'IMPARK',
        'DIAMOND PARKING': 'DIAMOND PARKING',
        'EASYPARK': 'EASYPARK',
        'PARK PLUS': 'PARK PLUS',
        
        # Warehouse stores
        'COSTCO WHOLESALE': 'COSTCO',
        'COSTCO': 'COSTCO',
        'COSTCO GAS': 'COSTCO GAS',
        'COSTCO GASOLINE': 'COSTCO GAS',
        'COSTCO FUEL': 'COSTCO GAS',
        
        # Common retailers
        'WAL-MART SUPERCENTER': 'WAL-MART SUPERCENTER',
        'WALMART SUPERCENTER': 'WALMART SUPERCENTER',
        'WAL-MART': 'WAL-MART',
        'WALMART': 'WALMART',
        'CANADIAN TIRE': 'CANADIAN TIRE',
        'METRO': 'METRO',
        'LOBLAWS': 'LOBLAWS',
        'SOBEYS': 'SOBEYS',
        'NO FRILLS': 'NO FRILLS',
        'FOOD BASICS': 'FOOD BASICS',
        'REAL CANADIAN SUPERSTORE': 'REAL CANADIAN SUPERSTORE',
        'SUPERSTORE': 'SUPERSTORE',
        
        # Coffee shops
        'TIM HORTONS': 'TIM HORTONS',
        'STARBUCKS': 'STARBUCKS',
        'SECOND CUP': 'SECOND CUP',
        'COFFEE TIME': 'COFFEE TIME',
        
        # Fast food
        'MCDONALDS': 'MCDONALDS',
        'SUBWAY': 'SUBWAY',
        'PIZZA PIZZA': 'PIZZA PIZZA',
        'BURGER KING': 'BURGER KING',
        'KFC': 'KFC',
        'TACO BELL': 'TACO BELL',
        'A&W': 'A&W',
        
        # Gas stations
        'PETRO CANADA': 'PETRO CANADA',
        'PETRO-CANADA': 'PETRO CANADA',
        'SHELL': 'SHELL',
        'ESSO': 'ESSO',
        'HUSKY': 'HUSKY',
        'MOBIL': 'MOBIL',
        'ULTRAMAR': 'ULTRAMAR',
        'PIONEER': 'PIONEER',
        
        # Services
        'UBER CANADA/UBEREATS': 'UBER CANADA/UBEREATS',
        'UBER EATS': 'UBER EATS',
        'SKIP THE DISHES': 'SKIP THE DISHES',
        'DOORDASH': 'DOORDASH',
        'INSTACART': 'INSTACART',
        
        # Pharmacies
        'SHOPPERS DRUG MART': 'SHOPPERS DRUG MART',
        'REXALL': 'REXALL',
        'PHARMASAVE': 'PHARMASAVE',
        
        # Electronics
        'BEST BUY': 'BEST BUY',
        'FUTURE SHOP': 'FUTURE SHOP',
        'THE SOURCE': 'THE SOURCE',
    }
    
    # Check if the cleaned name starts with any known merchant
    # Sort by length (longest first) to match more specific patterns first
    name_upper = name.upper()
    sorted_merchants = sorted(merchant_corrections.items(), key=lambda x: len(x[0]), reverse=True)
    
    for merchant_key, clean_name in sorted_merchants:
        if name_upper.startswith(merchant_key.upper()):
            return clean_name
    
    # Final cleanup: remove extra spaces and trim
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Remove trailing special characters
    name = re.sub(r'[#*/-]+$', '', name).strip()
    
    return name


def map_pdf_category_to_system_id(pdf_category: Optional[str]) -> Optional[int]:
    """Map PDF category to system category ID."""
    if not pdf_category:
        return None
    
    # Mapping based on the current system categories
    category_mapping = {
        'restaurants': 2,           # Food & Drinks
        'transportation': 3,        # Transport  
        'grocery': 5,              # Groceries
        'retail': 4,               # Shopping (for general retail)
        'entertainment': 6,        # Entertainment
        'gas': 3,                  # Transport (gas stations)
        'etransfer': 27,           # Interac E-Transfer
        'etransfer_self': 28,      # Interac E-Transfer Self
        'e-transfer': 27,          # Interac E-Transfer
        'e-transfer_self': 28,     # Interac E-Transfer Self
    }
    
    return category_mapping.get(pdf_category.lower())


def auto_categorize_transaction(description: str, amount: float, bank: str) -> Optional[int]:
    """Automatically categorize transaction based on description and context."""
    description_upper = description.upper()
    
    # E-Transfer categorization
    if 'E-TRANSFER' in description_upper or 'ETRANSFER' in description_upper:
        # Check if it's a self-transfer (to/from same person or between accounts)
        self_indicators = [
            'SATYA', 'SANNIHITH', 'LINGUTLA',  # User's name
            'SELF', 'MYSELF', 'OWN ACCOUNT',
            'SAVINGS', 'CHECKING', 'ACCOUNT',
            'TRANSFER TO', 'TRANSFER FROM'
        ]
        
        # Check if it's from/to the same person (self-transfer)
        if any(indicator in description_upper for indicator in self_indicators):
            return 28  # Interac E-Transfer Self
        else:
            return 27  # Interac E-Transfer
    
    # Internet Transfer categorization (typically self-transfers)
    if 'INTERNET TRANSFER' in description_upper:
        return 28  # Interac E-Transfer Self
    
    # Service charges and fees
    if any(keyword in description_upper for keyword in ['SERVICE CHARGE', 'FEE', 'MONTHLY']):
        return 13  # Bills
    
    # Payroll deposits
    if any(keyword in description_upper for keyword in ['PAYROLL', 'SALARY', 'WAGE']):
        return 1  # Income
    
    # Bill payments
    if any(keyword in description_upper for keyword in ['BILL', 'PAYMENT', 'PYMT']):
        return 13  # Bills
    
    # Phone/telecom
    if any(keyword in description_upper for keyword in ['FIDO', 'ROGERS', 'BELL', 'TELUS', 'PHONE']):
        return 13  # Bills
    
    # Utilities
    if any(keyword in description_upper for keyword in ['HYDRO', 'ELECTRIC', 'GAS', 'WATER', 'UTILITIES']):
        return 13  # Bills
    
    return None  # No automatic categorization


def parse_cibc_checking_transaction(line: str) -> Dict[str, Any]:
    """Parse CIBC checking account transaction line."""
    # CIBC Checking format: Date Description Withdrawals ($) Deposits ($) Balance ($)
    # BUT the actual format is more complex with amounts embedded in description
    # Example: "Jul 4 E-TRANSFER        011359544971 SATYA SANNIHITH LINGUTLA.597.00 1,125.40"
    # Example: "Jul 9 INTERNET TRANSFER 000000101667 347.71 642.69"
    
    line = line.strip()
    if not line or line.startswith('Date') or 'Balance forward' in line or 'Opening balance' in line or 'Closing balance' in line:
        return None
    
    # First, try to extract date at the beginning
    date_pattern = r'^([A-Za-z]{3}\s+\d{1,2})\s+(.+)'
    date_match = re.match(date_pattern, line)
    
    if not date_match:
        return None
    
    try:
        date_str = date_match.group(1)
        rest_of_line = date_match.group(2).strip()
        
        # Parse date (assume current year)
        current_year = datetime.now().year
        date_obj = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
        
        # Find all monetary amounts in the line
        amount_pattern = r'(\d{1,3}(?:,\d{3})*\.\d{2})'
        amounts = re.findall(amount_pattern, rest_of_line)
        
        if len(amounts) < 2:
            return None  # Need at least transaction amount and balance
        
        # The last amount is always the balance, the second-to-last is the transaction amount
        transaction_amount = float(amounts[-2].replace(',', ''))
        balance = float(amounts[-1].replace(',', ''))
        
        # Extract description by removing amounts from the end
        description_part = rest_of_line
        for amount in reversed(amounts[-2:]):  # Remove last two amounts
            # Only remove the amount if it's at the end or followed by whitespace
            if description_part.endswith(amount):
                description_part = description_part[:-len(amount)].strip()
            else:
                # More careful replacement - look for the amount at word boundaries
                pattern = r'\b' + re.escape(amount) + r'\b'
                description_part = re.sub(pattern, '', description_part).strip()
        
        # Determine if this is a deposit or withdrawal based on keywords
        description_upper = description_part.upper()
        deposit_keywords = ['DEPOSIT', 'E-TRANSFER', 'PAYROLL', 'TRANSFER IN']
        withdrawal_keywords = ['INTERNET TRANSFER', 'PREAUTHORIZED DEBIT', 'SERVICE CHARGE', 'FEE']
        
        if any(keyword in description_upper for keyword in deposit_keywords):
            amount = abs(transaction_amount)  # Deposit (positive)
        elif any(keyword in description_upper for keyword in withdrawal_keywords):
            amount = -abs(transaction_amount)  # Withdrawal (negative)
        else:
            # Default logic: if description contains names, likely a transfer out
            if any(name in description_upper for name in ['SATYA', 'LINGUTLA', 'KUMARESH', 'BHIMESWARA', 'YASH', 'ARJUN']):
                amount = abs(transaction_amount)  # Transfer in (positive)
            else:
                amount = -abs(transaction_amount)  # Default to withdrawal
        
        # Clean description using our merchant cleaning function
        description = clean_merchant_name(description_part)
        
        # Auto-categorize the transaction
        category_id = auto_categorize_transaction(description, amount, 'CIBC')
        
        return {
            'date': date_obj,
            'description': description,
            'amount': Decimal(str(amount)),
            'bank': 'CIBC',
            'account_type': 'CHECKING',
            'pdf_category': None,
            'auto_category_id': category_id
        }
    except Exception as e:
        return None
    
    return None


def parse_cibc_transaction(line: str) -> Dict[str, Any]:
    """Parse CIBC credit card transaction line."""
    # CIBC Credit Card format: Transaction_Date Processing_Date MERCHANT_NAME LOCATION CATEGORY Amount
    # Example: "Jun 26 Jun 26 IMPARK00120172H 844-309-1028 ON Transportation 13.00"
    # Example: "Jul 09 Jul 10 PAYMENT THANK YOU/PAIEMENT MERCI 347.71"
    
    line = line.strip()
    if not line:
        return None
    
    # Pattern for CIBC credit card transactions
    # Format: MMM DD MMM DD MERCHANT_INFO... CATEGORY AMOUNT
    pattern = r'^([A-Za-z]{3}\s+\d{1,2})\s+([A-Za-z]{3}\s+\d{1,2})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*\.\d{2})$'
    
    match = re.match(pattern, line)
    if match:
        try:
            transaction_date = match.group(1)  # e.g., "Jun 26"
            processing_date = match.group(2)   # e.g., "Jun 26"
            merchant_info = match.group(3).strip()  # Everything between dates and amount
            amount_str = match.group(4)        # e.g., "13.00"
            
            # Parse date (use transaction date, assume current year)
            current_year = datetime.now().year
            date_obj = datetime.strptime(f"{transaction_date} {current_year}", "%b %d %Y")
            
            # Parse amount
            amount = float(amount_str.replace(',', ''))
            
            # Extract description and category from merchant info
            parts = merchant_info.split()
            
            # For payments, the merchant info is clear
            if 'PAYMENT' in merchant_info.upper():
                description = 'PAYMENT'
                amount = abs(amount)  # Payments are positive (credits)
                category = None
            else:
                # For purchases, extract merchant name using spacing pattern
                # Merchant name is separated from location by 2+ spaces
                parts_by_spaces = re.split(r'\s{2,}', merchant_info)
                
                if len(parts_by_spaces) >= 2:
                    # First part is the merchant name
                    raw_description = parts_by_spaces[0].strip()
                    location_info = ' '.join(parts_by_spaces[1:]).strip()
                    
                    # Clean the merchant name using our new function
                    description = clean_merchant_name(raw_description)
                else:
                    # Fallback: split by words and find province code
                    words = merchant_info.split()
                    province_start = -1
                    for i, word in enumerate(words):
                        if word.upper() in ['ON', 'BC', 'AB', 'QC', 'MB', 'SK', 'NS', 'NB', 'PE', 'NL', 'YT', 'NT', 'NU']:
                            province_start = i
                            break
                    
                    if province_start > 1:
                        # Assume last word before province is city, everything before is merchant
                        merchant_words = words[:province_start-1]
                        raw_description = ' '.join(merchant_words).strip()
                        location_info = ' '.join(words[province_start-1:]).strip()
                    else:
                        # Last fallback: use first 3 words
                        raw_description = ' '.join(words[:3]).strip()
                        location_info = ' '.join(words[3:]).strip()
                    
                    # Clean the merchant name using our new function
                    description = clean_merchant_name(raw_description)
                
                # Extract category from location_info
                category = None
                location_text = location_info.lower()
                if 'restaurants' in location_text:
                    category = 'restaurants'
                elif 'transportation' in location_text:
                    category = 'transportation'  
                elif 'retail' in location_text and 'grocery' in location_text:
                    category = 'grocery'
                elif 'grocery' in location_text:
                    category = 'grocery'
                elif 'entertainment' in location_text:
                    category = 'entertainment'
                elif 'gas' in location_text:
                    category = 'gas'
                
                amount = -abs(amount)  # Purchases are negative (debits)
            
            return {
                'date': date_obj,
                'description': description.strip(),
                'amount': Decimal(str(amount)),
                'bank': 'CIBC',
                'pdf_category': category  # Add extracted category
            }
        except Exception as e:
            return None
    
    return None


def parse_rbc_checking_transaction(line: str) -> Dict[str, Any]:
    """Parse RBC checking account transaction line."""
    # RBC Checking format: DATE DESCRIPTION WITHDRAWALS DEPOSITS BALANCE
    # Example: "Jul 15, 2025 to Find & Save - $75.00 $1,417.86"
    # Example: "Jul 4, 2025Payroll Deposit The Wawanesa Mu$2,567.28"
    
    line = line.strip()
    if not line or line.startswith('DATE') or 'about:blank' in line:
        return None
    
    # Pattern for RBC checking transactions
    # Format: MMM DD, YYYY DESCRIPTION - $AMOUNT $BALANCE or MMM DD, YYYY DESCRIPTION $AMOUNT
    pattern = r'^([A-Za-z]{3}\s+\d{1,2},\s+\d{4})\s*(.+?)(?:-\s*)?\$(\d{1,3}(?:,\d{3})*\.\d{2})\s*(?:\$(\d{1,3}(?:,\d{3})*\.\d{2}))?'
    
    match = re.search(pattern, line)
    if match:
        try:
            date_str = match.group(1)
            description_raw = match.group(2).strip()
            amount_value = float(match.group(3).replace(',', ''))
            balance = float(match.group(4).replace(',', '')) if match.group(4) else 0
            
            # Parse date
            date_obj = datetime.strptime(date_str, "%b %d, %Y")
            
            # Determine if this is a deposit or withdrawal based on description and format
            deposit_keywords = ['DEPOSIT', 'PAYROLL', 'E-TRANSFER RECEIVED', 'TRANSFER FROM']
            withdrawal_keywords = ['WITHDRAW', 'PAYMENT', 'FEE', 'TRANSFER TO', 'E-TRANSFER SENT']
            
            description_upper = description_raw.upper()
            
            if any(keyword in description_upper for keyword in deposit_keywords):
                amount = abs(amount_value)  # Deposit (positive)
            elif any(keyword in description_upper for keyword in withdrawal_keywords):
                amount = -abs(amount_value)  # Withdrawal (negative)
            elif '-' in line:  # Line has dash, indicating withdrawal
                amount = -abs(amount_value)
            else:  # Default to deposit if no clear indication
                amount = abs(amount_value)
            
            # Clean description using our merchant cleaning function
            description = clean_merchant_name(description_raw)
            
            # Auto-categorize the transaction
            category_id = auto_categorize_transaction(description, amount, 'RBC')
            
            return {
                'date': date_obj,
                'description': description,
                'amount': Decimal(str(amount)),
                'bank': 'RBC',
                'account_type': 'CHECKING',
                'pdf_category': None,
                'auto_category_id': category_id
            }
        except Exception as e:
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


def detect_canadian_bank(text: str) -> tuple:
    """Detect which Canadian bank format and account type the text uses."""
    text_upper = text.upper()
    
    # Detect bank
    bank = 'UNKNOWN'
    account_type = 'UNKNOWN'
    
    if 'CIBC' in text_upper or 'CANADIAN IMPERIAL BANK' in text_upper:
        bank = 'CIBC'
        # Detect account type for CIBC
        if ('ACCOUNT STATEMENT' in text_upper and ('WITHDRAWALS' in text_upper or 'DEPOSITS' in text_upper)) or \
           'CHEQUING' in text_upper or 'CHECKING' in text_upper or \
           ('INTERNET TRANSFER' in text_upper and 'E-TRANSFER' in text_upper):
            account_type = 'CHECKING'
        elif 'CREDIT CARD' in text_upper or 'VISA' in text_upper or \
             ('PURCHASE' in text_upper and 'PAYMENT' in text_upper):
            account_type = 'CREDIT'
        else:
            account_type = 'CHECKING'  # Default for CIBC (most common)
            
    elif 'ROYAL BANK' in text_upper or 'RBC' in text_upper:
        bank = 'RBC'
        # Detect account type for RBC
        if 'DAY TO DAY BANKING' in text_upper or 'PERSONAL DEPOSIT ACCOUNT' in text_upper or \
           'CHEQUING' in text_upper or 'CHECKING' in text_upper or \
           ('E-TRANSFER' in text_upper and 'PAYROLL' in text_upper):
            account_type = 'CHECKING'
        elif 'CREDIT CARD' in text_upper or 'VISA' in text_upper or 'MASTERCARD' in text_upper:
            account_type = 'CREDIT'
        else:
            account_type = 'CHECKING'  # Default for RBC
            
    elif 'AMERICAN EXPRESS' in text_upper or 'AMEX' in text_upper:
        bank = 'AMEX'
        account_type = 'CREDIT'  # AMEX is always credit
        
    elif 'TD CANADA TRUST' in text_upper or 'TD BANK' in text_upper:
        bank = 'TD'
        account_type = 'CHECKING'  # Default for TD
        
    elif 'BANK OF MONTREAL' in text_upper or 'BMO' in text_upper:
        bank = 'BMO'
        account_type = 'CHECKING'  # Default for BMO
        
    elif 'SCOTIABANK' in text_upper or 'SCOTIA' in text_upper:
        bank = 'SCOTIA'
        account_type = 'CHECKING'  # Default for Scotia
        
    elif 'TANGERINE' in text_upper:
        bank = 'TANGERINE'
        account_type = 'CHECKING'  # Default for Tangerine
    
    return bank, account_type


def parse_canadian_bank_transactions(text: str) -> List[Dict[str, Any]]:
    """
    Parse transactions from Canadian bank statements.
    Auto-detects bank type and account type, then applies appropriate parser.
    """
    transactions = []
    bank_type, account_type = detect_canadian_bank(text)
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        transaction = None
        
        # Choose parser based on bank and account type
        if bank_type == 'CIBC':
            if account_type == 'CHECKING':
                transaction = parse_cibc_checking_transaction(line)
            else:  # CREDIT or unknown
                transaction = parse_cibc_transaction(line)
        elif bank_type == 'RBC':
            if account_type == 'CHECKING':
                transaction = parse_rbc_checking_transaction(line)
            else:  # CREDIT or unknown
                transaction = parse_rbc_transaction(line)
        elif bank_type == 'AMEX':
            transaction = parse_amex_canada_transaction(line)
        elif bank_type == 'TD':
            transaction = parse_td_transaction(line)
        else:
            # Try all parsers if bank type unknown
            for parser in [parse_cibc_checking_transaction, parse_cibc_transaction, 
                          parse_rbc_checking_transaction, parse_rbc_transaction,
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


def extract_account_info(text: str, bank_type: str, account_type: str = None) -> Dict[str, str]:
    """Extract account information from bank statement text."""
    text_upper = text.upper()
    account_info = {
        'account_number': 'UNKNOWN',
        'account_type': 'CHECKING',  # Default
        'account_name': '',
        'last_4_digits': '0000'
    }
    
    if bank_type == 'CIBC':
        # CIBC patterns - including credit card formats
        # Account number patterns: "Account Number: 1234 5678 901", "****1234", "4505 XXXX XXXX 7841"
        patterns = [
            r'ACCOUNT\s+NUMBER[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})',
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})',
            r'(\d{4})\s+X{4}\s+X{4}\s+(\d{4})',  # CIBC credit card format: "4505 XXXX XXXX 7841"
            r'\*{4}(\d{4})',
            r'(\d{4})\s*CHEQUING',
            r'(\d{4})\s*SAVINGS',
            r'(\d{4})\s*CREDIT'
        ]
        
        # Account type detection
        if 'CHEQUING' in text_upper or 'CHECKING' in text_upper:
            account_info['account_type'] = 'CHECKING'
        elif 'SAVINGS' in text_upper:
            account_info['account_type'] = 'SAVINGS'
        elif 'CREDIT' in text_upper or 'VISA' in text_upper:
            account_info['account_type'] = 'CREDIT'
            
    elif bank_type == 'RBC':
        # RBC patterns
        patterns = [
            r'ACCOUNT\s+(\d{5}-\d{7})',  # RBC format: 12345-1234567
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})',
            r'\*{4}(\d{4})',
            r'(\d{4})\s*CHEQUING',
            r'(\d{4})\s*SAVINGS'
        ]
        
        # RBC account type detection
        if 'CHEQUING' in text_upper or 'CHECKING' in text_upper:
            account_info['account_type'] = 'CHECKING'
        elif 'SAVINGS' in text_upper or 'HIGH INTEREST' in text_upper:
            account_info['account_type'] = 'SAVINGS'
        elif 'CREDIT' in text_upper or 'VISA' in text_upper or 'MASTERCARD' in text_upper:
            account_info['account_type'] = 'CREDIT'
            
    elif bank_type == 'AMEX':
        # AMEX patterns - typically credit cards
        patterns = [
            r'CARD\s+ENDING\s+(\d{4})',
            r'\*{4}(\d{4})',
            r'(\d{4})\s*CREDIT',
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{6}[\s-]*\d{5})'  # AMEX 15-digit format
        ]
        account_info['account_type'] = 'CREDIT'  # AMEX is always credit
        
    else:
        # Generic patterns for other banks
        patterns = [
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})',
            r'\*{4}(\d{4})',
            r'(\d{4})\s*(?:CHEQUING|SAVINGS|CREDIT)'
        ]
    
    # Try to extract account number
    for pattern in patterns:
        match = re.search(pattern, text_upper)
        if match:
            # Handle special case for CIBC credit card format with two groups
            if len(match.groups()) == 2 and 'X{4}' in pattern:
                # This is the "4505 XXXX XXXX 7841" format
                first_four = match.group(1)
                last_four = match.group(2)
                account_info['account_number'] = f"{first_four}XXXX{last_four}"
                account_info['last_4_digits'] = last_four
            else:
                account_number = match.group(1)
                # Clean up the account number
                clean_number = re.sub(r'[\s-]', '', account_number)
                account_info['account_number'] = clean_number
                
                # Extract last 4 digits
                if len(clean_number) >= 4:
                    account_info['last_4_digits'] = clean_number[-4:]
            break
    
    return account_info


def extract_account_balance(text: str, bank_type: str) -> float:
    """Extract current account balance from bank statement."""
    text_upper = text.upper()
    
    if bank_type == 'CIBC':
        # CIBC patterns for balance - ordered by priority (most specific first)
        patterns = [
            # Credit card specific patterns (highest priority)
            r'TOTAL\s+BALANCE\s*=\s*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})CR',  # "$0.54CR"
            r'TOTAL\s+BALANCE\s*=\s*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',     # "Total balance = $123.45"
            r'AMOUNT\s+DUE[1-9]?\s*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',      # "Amount Due1 $0.00"
            r'NEW\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'CURRENT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'STATEMENT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            # Generic balance patterns (lower priority)
            r'BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'ACCOUNT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})'
        ]
        
    elif bank_type == 'RBC':
        # RBC patterns
        patterns = [
            r'CLOSING\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'CURRENT\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'ACCOUNT\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'NEW\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})'
        ]
        
    elif bank_type == 'AMEX':
        # AMEX patterns
        patterns = [
            r'NEW\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'CURRENT\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'ACCOUNT\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'TOTAL\s+BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})'
        ]
        
    else:
        # Generic patterns
        patterns = [
            r'BALANCE[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'CURRENT[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
            r'TOTAL[:\s]*[\$\s]*([+-]?\d{1,3}(?:,\d{3})*\.\d{2})'
        ]
    
    # Try to extract balance
    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        if matches:
            try:
                # Take the first match (ordered by priority)
                balance_str = matches[0].replace(',', '').replace('+', '')
                balance = float(balance_str)
                
                # For credit cards, negative balance means you owe money
                # Positive balance with CR means credit (you have money)
                if 'CR' in pattern:
                    # This is a credit balance - make it positive since it's what you have
                    balance = abs(balance)
                else:
                    # For "Amount Due", this is what you owe, so keep it as debt
                    if 'AMOUNT\\s+DUE' in pattern:
                        balance = -abs(balance) if balance > 0 else 0  # Amount due is debt
                
                return balance
            except (ValueError, IndexError):
                continue
    
    # Default to 0 if no balance found
    return 0.0


def extract_statement_period(text: str) -> Dict[str, str]:
    """Extract statement period from bank statement."""
    period_info = {
        'start_date': '',
        'end_date': '',
        'statement_date': ''
    }
    
    text_upper = text.upper()
    
    # Common period patterns
    period_patterns = [
        r'STATEMENT\s+PERIOD[:\s]*(\w+\s+\d{1,2},?\s+\d{4})\s+TO\s+(\w+\s+\d{1,2},?\s+\d{4})',
        r'FROM[:\s]*(\w+\s+\d{1,2},?\s+\d{4})\s+TO\s+(\w+\s+\d{1,2},?\s+\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})\s+TO\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{4}-\d{2}-\d{2})\s+TO\s+(\d{4}-\d{2}-\d{2})'
    ]
    
    for pattern in period_patterns:
        match = re.search(pattern, text_upper)
        if match:
            period_info['start_date'] = match.group(1)
            period_info['end_date'] = match.group(2)
            break
    
    return period_info