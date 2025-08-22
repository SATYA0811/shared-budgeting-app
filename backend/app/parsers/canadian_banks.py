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
    # Real CIBC Checking format from statement:
    # Multi-line transactions where amounts are at the end of lines:
    # "Jul 4 E-TRANSFER        011359544971"
    # "SATYA SANNIHITH LINGUTLA.597.00 1,125.40"
    # " INTERNET TRANSFER 000000101667 347.71 642.69"
    # "SERVICE CHARGE"
    # "ADD TXN$0.00;MONTHLY$6.95"
    # "RECORD-KEEPING  N/A6.95 640.72"
    
    line = line.strip()
    if not line:
        return None
    
    # Skip header and footer lines
    skip_patterns = [
        'Date Description', 'Balance forward', 'Opening balance', 'Closing balance',
        'Transaction details', 'Page ', 'continued', 'Important:', 'Foreign Currency',
        'Trademark', 'Registered trademark', 'Account Statement', 'Account number',
        'Branch transit number', 'Contact information', 'www.', 'TTY hearing',
        'Outside Canada', 'Free Transaction', 'This statement will be',
        'For Jul', 'to Jul', 'Withdrawals', 'Deposits', 'Balance ($)'
    ]
    
    if any(pattern in line for pattern in skip_patterns):
        return None
    
    # Pattern 1: Line with transaction amount and balance at the end
    # Examples:
    # "SATYA SANNIHITH LINGUTLA.597.00 1,125.40"
    # " INTERNET TRANSFER 000000101667 347.71 642.69"
    # "RECORD-KEEPING  N/A6.95 640.72"
    
    # Look for pattern: [description] [amount] [balance]
    amount_balance_pattern = r'^(.+?)\s*(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d{1,3}(?:,\d{3})*\.\d{2})$'
    match = re.search(amount_balance_pattern, line)
    
    if match:
        description_part, amount_str, balance_str = match.groups()
        
        # Clean up description
        description = description_part.strip()
        
        # Handle special cases
        # 1. Service charge with N/A pattern
        if 'N/A' in description:
            description = description.replace('N/A', '').strip()
            description = 'SERVICE CHARGE RECORD-KEEPING' if 'RECORD-KEEPING' in description else 'SERVICE CHARGE'
        
        # 2. Remove trailing dots from names
        description = description.rstrip('.')
        
        # 3. Clean up whitespace
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Determine transaction amount and sign
        transaction_amount = float(amount_str.replace(',', ''))
        
        # Determine if deposit or withdrawal based on description
        description_upper = description.upper()
        
        # Determine transaction direction based on CIBC checking account rules
        description_upper = description.upper()
        
        # TPS/GST deposits are incoming (government tax refunds)
        if 'TPS/GST' in description_upper or 'GST' in description_upper:
            amount = abs(transaction_amount)  # Deposit (+)
        # DEPOSITS are always incoming
        elif 'DEPOSIT' in description_upper:
            amount = abs(transaction_amount)  # Deposit (+)
        # E-TRANSFERS - determine direction by looking at reference numbers in context
        elif 'E-TRANSFER' in description_upper:
            # In CIBC statements:
            # - Incoming e-transfers have reference numbers starting with 011
            # - Outgoing e-transfers have reference numbers starting with 105
            # Check the context around this line for reference patterns
            context_text = '\n'.join(lines[max(0, i-5):i+5]) if 'lines' in locals() else line
            if re.search(r'\b105\d{9}\b', context_text):
                amount = -abs(transaction_amount)  # Outgoing e-transfer (-)
            elif re.search(r'\b011\d{9}\b', context_text):
                amount = abs(transaction_amount)   # Incoming e-transfer (+)
            else:
                # Fallback: check by name patterns for known people
                if any(name in description_upper for name in ['KUMARESH', 'BHIMESWARA', 'YASH', 'ARJUN']) and '@' not in description_upper:
                    amount = -abs(transaction_amount)  # Likely outgoing (-)
                else:
                    amount = abs(transaction_amount)   # Default to incoming (+)
        # INTERNET TRANSFERS are typically outgoing (withdrawals from checking)
        elif 'INTERNET TRANSFER' in description_upper:
            amount = -abs(transaction_amount)  # Outgoing (-)
        # PREAUTHORIZED DEBITS are always outgoing
        elif 'PREAUTHORIZED DEBIT' in description_upper:
            amount = -abs(transaction_amount)  # Outgoing (-)
        # SERVICE CHARGES are always outgoing
        elif 'SERVICE CHARGE' in description_upper:
            amount = -abs(transaction_amount)  # Outgoing (-)
        # Companies/services are typically outgoing payments
        elif any(company in description_upper for company in ['REMITLY', 'CIBC SECURITIES']):
            amount = -abs(transaction_amount)  # Outgoing (-)
        # For specific people names, check if they're incoming or outgoing transfers
        elif any(name in description_upper for name in ['SATYA', 'KUMARESH', 'BHIMESWARA', 'YASH', 'ARJUN', 'HARSHIL']):
            # If the line contains the person's name directly, it's likely incoming
            amount = abs(transaction_amount)   # Incoming (+)
        # People with email-like patterns or just names are typically incoming
        elif any(indicator in description_upper for indicator in ['@']) or re.search(r'^[a-z]+\d*$', description.lower()):
            amount = abs(transaction_amount)  # Incoming (+) 
        else:
            # Default for unknown patterns - checking account context suggests outgoing
            amount = -abs(transaction_amount)  # Default to outgoing (-)
        
        # Use July 1st as default date (will be context-aware in full parsing)
        current_year = datetime.now().year
        date_obj = datetime.strptime(f"Jul 1 {current_year}", "%b %d %Y")
        
        # Preserve transaction type in description
        original_desc = description
        if 'E-TRANSFER' not in description_upper and ('SATYA' in description_upper or 'KUMARESH' in description_upper or any(name in description_upper for name in ['BHIMESWARA', 'YASH', 'ARJUN', 'HARSHIL', '@'])):
            description = f"E-TRANSFER {description}"
        elif 'INTERNET TRANSFER' not in description_upper and re.search(r'\b\d{12}\b', original_desc):
            description = f"INTERNET TRANSFER {description}"
        elif 'PREAUTHORIZED DEBIT' not in description_upper and any(company in description_upper for company in ['REMITLY', 'CIBC SECURITIES']):
            description = f"PREAUTHORIZED DEBIT {description}"
        elif 'SERVICE CHARGE' not in description_upper and 'RECORD-KEEPING' in description_upper:
            description = f"SERVICE CHARGE {description}"
        elif 'DEPOSIT' not in description_upper and 'TPS/GST' in description_upper:
            description = f"DEPOSIT {description}"
        
        # Clean description
        description = clean_merchant_name(description)
        
        # Auto-categorize
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
    
    # Pattern 2: Service charge multi-line format
    # "ADD TXN$0.00;MONTHLY$6.95"
    if 'TXN$' in line and 'MONTHLY$' in line:
        monthly_match = re.search(r'MONTHLY\$(\d+\.\d{2})', line)
        if monthly_match:
            amount_str = monthly_match.group(1)
            amount = -float(amount_str)  # Service charge is negative
            
            current_year = datetime.now().year
            date_obj = datetime.strptime(f"Jul 31 {current_year}", "%b %d %Y")
            
            description = "SERVICE CHARGE MONTHLY"
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
    
    # Pattern 3: Check for date-only lines or description-only lines
    # These are parts of multi-line transactions that will be combined elsewhere
    if re.match(r'^[A-Za-z]{3}\s+\d{1,2}$', line):  # "Jul 4"
        return None  # Date-only line, skip
    
    if re.match(r'^[A-Z\s-]+$', line) and len(line) < 50:  # Description lines like "DEPOSIT" or "SERVICE CHARGE"
        return None  # Description-only line, skip
    
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
    import logging
    transactions = []
    bank_type, account_type = detect_canadian_bank(text)
    
    lines = text.split('\n')
    logging.info(f"🔍 Parsing {len(lines)} lines for {bank_type} {account_type}")
    
    # For CIBC CHECKING, use the enhanced line-by-line parser with better date tracking
    if bank_type == 'CIBC' and account_type == 'CHECKING':
        return parse_cibc_checking_with_dates(text)
    
    parsed_count = 0
    skipped_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        transaction = None
        
        # Choose parser based on bank and account type
        if bank_type == 'CIBC':
            if account_type == 'CHECKING':
                transaction = parse_cibc_checking_transaction(line)
                if not transaction and line and not line.startswith('Date'):
                    logging.debug(f"❌ Line {i}: Skipped '{line[:60]}...'")
                    skipped_count += 1
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
            parsed_count += 1
            logging.debug(f"✅ Line {i}: Parsed '{transaction['description'][:40]}' - ${transaction['amount']}")
            transactions.append(transaction)
    
    logging.info(f"📊 Parse Summary: {parsed_count} parsed, {skipped_count} skipped, {len(transactions)} total")
    return transactions


def parse_cibc_checking_statement(text: str) -> List[Dict[str, Any]]:
    """Parse CIBC checking statement with context-aware date tracking."""
    import logging
    from decimal import Decimal
    
    transactions = []
    lines = text.split('\n')
    
    current_date = None
    current_year = datetime.now().year
    
    logging.info(f"🔍 Context-aware parsing of CIBC checking statement")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if this line contains a date
        date_match = re.match(r'^([A-Za-z]{3}\s+\d{1,2})(?:\s|$)', line)
        if date_match:
            try:
                date_str = date_match.group(1)
                current_date = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
                logging.debug(f"📅 Found date: {current_date.strftime('%b %d')}")
                continue
            except ValueError:
                pass
        
        # Try to parse as transaction (with amounts and balance)
        amount_balance_pattern = r'^(.+?)\s*(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d{1,3}(?:,\d{3})*\.\d{2})$'
        match = re.search(amount_balance_pattern, line)
        
        if match:
            description_part, amount_str, balance_str = match.groups()
            
            # Clean up description
            description = description_part.strip()
            
            # Skip if this looks like a header or summary line
            skip_patterns = [
                'Date Description', 'Balance forward', 'Opening balance', 'Closing balance',
                'Transaction details', 'Withdrawals', 'Deposits', 'Balance ($)'
            ]
            if any(pattern in description for pattern in skip_patterns):
                continue
            
            # Handle special cases
            if 'N/A' in description:
                description = description.replace('N/A', '').strip()
                description = 'SERVICE CHARGE RECORD-KEEPING' if 'RECORD-KEEPING' in description else 'SERVICE CHARGE'
            
            # Remove trailing dots and clean whitespace
            description = description.rstrip('.').strip()
            description = re.sub(r'\s+', ' ', description)
            
            # Parse amount
            transaction_amount = float(amount_str.replace(',', ''))
            
            # Determine transaction direction
            description_upper = description.upper()
            
            # TPS/GST deposits are incoming
            if 'TPS/GST' in description_upper or 'GST' in description_upper:
                amount = abs(transaction_amount)
            # E-transfers with names - check reference numbers to determine direction
            elif any(name in description_upper for name in ['SATYA', 'KUMARESH', 'BHIMESWARA', 'YASH', 'ARJUN', 'HARSHIL']):
                # Look for outgoing reference patterns (105...)
                if re.search(r'\b105\d{9}\b', text[max(0, i-5):i+1]):  # Check context around this line
                    amount = -abs(transaction_amount)  # Outgoing
                else:
                    amount = abs(transaction_amount)   # Incoming
            # Internet transfers are outgoing
            elif 'INTERNET TRANSFER' in description_upper:
                amount = -abs(transaction_amount)
            # Companies/services are outgoing
            elif any(company in description_upper for company in ['REMITLY', 'CIBC SECURITIES', 'FIDO']):
                amount = -abs(transaction_amount)
            # Service charges are outgoing
            elif 'SERVICE CHARGE' in description_upper:
                amount = -abs(transaction_amount)
            # Deposits are incoming
            elif 'DEPOSIT' in description_upper:
                amount = abs(transaction_amount)
            else:
                # For people names, assume incoming
                if any(indicator in description_upper for indicator in ['@', 'PATEL']) or re.search(r'[a-z]+\d+', description):
                    amount = abs(transaction_amount)
                else:
                    amount = -abs(transaction_amount)
            
            # Use current date or default to July 1st
            if current_date:
                date_obj = current_date
            else:
                date_obj = datetime.strptime(f"Jul 1 {current_year}", "%b %d %Y")
            
            # Clean description
            description = clean_merchant_name(description)
            
            # Auto-categorize
            category_id = auto_categorize_transaction(description, amount, 'CIBC')
            
            transaction = {
                'date': date_obj,
                'description': description,
                'amount': Decimal(str(amount)),
                'bank': 'CIBC',
                'account_type': 'CHECKING',
                'pdf_category': None,
                'auto_category_id': category_id
            }
            
            transactions.append(transaction)
            logging.debug(f"✅ Parsed: {description[:30]} | ${amount} | {date_obj.strftime('%b %d')}")
    
    # Handle service charge pattern separately
    for line in lines:
        if 'TXN$' in line and 'MONTHLY$' in line:
            monthly_match = re.search(r'MONTHLY\$(\d+\.\d{2})', line)
            if monthly_match:
                amount_str = monthly_match.group(1)
                amount = -float(amount_str)
                
                # Use July 31st for monthly service charges
                date_obj = datetime.strptime(f"Jul 31 {current_year}", "%b %d %Y")
                description = "SERVICE CHARGE MONTHLY"
                category_id = auto_categorize_transaction(description, amount, 'CIBC')
                
                transaction = {
                    'date': date_obj,
                    'description': description,
                    'amount': Decimal(str(amount)),
                    'bank': 'CIBC',
                    'account_type': 'CHECKING',
                    'pdf_category': None,
                    'auto_category_id': category_id
                }
                
                transactions.append(transaction)
                logging.debug(f"✅ Added monthly service charge: ${amount} | Jul 31")
    
    logging.info(f"📊 Context-aware parsing complete: {len(transactions)} transactions found")
    return transactions


def parse_cibc_checking_with_dates(text: str) -> List[Dict[str, Any]]:
    """Parse CIBC checking statement using enhanced context-aware parsing."""
    import logging
    
    # Use enhanced context-aware parser directly (dynamic parser has import issues in web context)
    lines = text.split('\n')
    transactions = []
    current_date = None
    current_year = datetime.now().year
    
    logging.info(f"🚀 Enhanced CIBC checking parsing with context and proper descriptions")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check for dates in lines
        date_match = re.match(r'^([A-Za-z]{3}\s+\d{1,2})(?:\s|$)', line)
        if date_match:
            try:
                date_str = date_match.group(1)
                current_date = datetime.strptime(f"{date_str} {current_year}", "%b %d %Y")
                logging.debug(f"📅 Date context updated: {current_date.strftime('%b %d')}")
            except ValueError:
                pass
        
        # Try to parse with raw transaction parser (no description cleaning)
        transaction = parse_cibc_raw_transaction_with_context(line, lines, i)
        if transaction:
            # Update the date with our context if we have one
            if current_date:
                transaction['date'] = current_date
            transactions.append(transaction)
            
    logging.info(f"📊 Enhanced parsing complete: {len(transactions)} transactions found")
    return transactions


def parse_cibc_checking_transaction_with_context(line: str, all_lines: list, line_index: int) -> Dict[str, Any]:
    """Parse CIBC checking transaction with full context for better direction detection."""
    # Get context around this line (5 lines before and after)
    context_start = max(0, line_index - 5)
    context_end = min(len(all_lines), line_index + 6)
    context_lines = all_lines[context_start:context_end]
    context_text = '\n'.join(context_lines)
    
    # Use original parsing but with context for direction detection
    transaction = parse_cibc_checking_transaction(line)
    if not transaction:
        return None
    
    # Override the amount direction using context analysis
    description = transaction['description']
    description_upper = description.upper()
    amount_value = abs(float(transaction['amount']))
    
    # E-TRANSFERS - use context to determine direction
    if 'E-TRANSFER' in description_upper:
        # Find the closest reference number to this transaction line
        closest_ref = None
        closest_distance = float('inf')
        
        # Search for reference numbers and find the closest one
        for j in range(max(0, line_index - 3), min(len(all_lines), line_index + 3)):
            ref_line = all_lines[j].strip()
            
            # Check for 011 (incoming) patterns
            ref_011 = re.search(r'\b011\d{9}\b', ref_line)
            if ref_011 and abs(j - line_index) < closest_distance:
                closest_ref = '011'
                closest_distance = abs(j - line_index)
                
            # Check for 105 (outgoing) patterns  
            ref_105 = re.search(r'\b105\d{9}\b', ref_line)
            if ref_105 and abs(j - line_index) < closest_distance:
                closest_ref = '105'
                closest_distance = abs(j - line_index)
        
        # Apply direction based on closest reference number
        if closest_ref == '105':
            transaction['amount'] = Decimal(str(-amount_value))  # Outgoing (-)
        elif closest_ref == '011':
            transaction['amount'] = Decimal(str(amount_value))   # Incoming (+)
        else:
            # Fallback: use name patterns
            if any(name in description_upper for name in ['KUMARESH', 'BHIMESWARA', 'YASH', 'ARJUN']) and '@' not in description_upper:
                transaction['amount'] = Decimal(str(-amount_value))  # Likely outgoing (-)
            else:
                transaction['amount'] = Decimal(str(amount_value))   # Default to incoming (+)
    
    # INTERNET TRANSFERS - determine direction based on context and balance changes
    elif 'INTERNET TRANSFER' in description_upper:
        # Small amounts (< $1) are often adjustments or corrections (typically incoming)
        if amount_value < 1.0:
            transaction['amount'] = Decimal(str(amount_value))   # Small amounts likely incoming (+)
        else:
            # For larger amounts, assume outgoing unless context suggests otherwise
            transaction['amount'] = Decimal(str(-amount_value))  # Default to outgoing (-)
    
    return transaction


def parse_cibc_raw_transaction_with_context(line: str, all_lines: list, line_index: int) -> Dict[str, Any]:
    """Parse CIBC checking transaction without description cleaning - preserves original names and details."""
    # Basic CIBC transaction pattern: [description] [amount] [balance]
    pattern = r'(.+?)(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d{1,3}(?:,\d{3})*\.\d{2})$'
    match = re.search(pattern, line.strip())
    
    if not match:
        return None
        
    description_raw = match.group(1).strip()
    amount_str = match.group(2).replace(',', '')
    balance_str = match.group(3).replace(',', '')
    
    # Clean up description (remove reference numbers but keep transaction types and names)
    description = description_raw
    
    # Remove reference numbers but preserve transaction types and names
    description = re.sub(r'\b\d{12,}\b', '', description)  # Remove long reference numbers  
    description = re.sub(r'\s+', ' ', description).strip()  # Clean up whitespace
    
    # Ensure transaction types are preserved and add them if missing
    if not any(t in description.upper() for t in ['E-TRANSFER', 'INTERNET TRANSFER', 'PREAUTHORIZED DEBIT', 'SERVICE CHARGE', 'DEPOSIT']):
        # Infer transaction type from context
        if 'TPS/GST' in description.upper():
            description = f"DEPOSIT {description}"
        elif any(name in description.upper() for name in ['SATYA', 'BHIMESWARA', 'YASH', 'ARJUN', 'HARSHIL', 'KUMARESH', '@']) or re.search(r'\b011\d{9}\b|\b105\d{9}\b', description_raw):
            description = f"E-TRANSFER {description}"
        elif 'REMITLY' in description.upper() or 'CIBC SECURITIES' in description.upper():
            description = f"PREAUTHORIZED DEBIT {description}"
        elif 'RECORD-KEEPING' in description.upper() or 'MONTHLY' in description.upper():
            description = f"SERVICE CHARGE {description}"
        elif re.search(r'\b000000\d{6}\b', description_raw):  # Internet transfer reference pattern
            description = f"INTERNET TRANSFER {description}"

    try:
        transaction_amount = Decimal(amount_str)
        amount_value = abs(float(transaction_amount))
        
        # Use balance change analysis for direction detection
        new_balance = float(balance_str.replace(',', ''))
        
        # Find previous balance by looking backwards for balance patterns
        previous_balance = None
        for i in range(line_index - 1, max(0, line_index - 20), -1):
            prev_line = all_lines[i].strip()
            
            # Look for balance patterns in previous lines
            balance_match = re.search(r'(\d+(?:,\d{3})*\.\d{2})$', prev_line)
            if balance_match:
                candidate_balance = float(balance_match.group(1).replace(',', ''))
                
                # Skip if this balance is the same as current transaction (same line context)
                if abs(candidate_balance - new_balance) < 0.01:
                    continue
                    
                # This is likely the previous balance
                previous_balance = candidate_balance
                break
        
        # Determine direction based on balance change
        if previous_balance is not None:
            balance_change = new_balance - previous_balance
            
            # If balance increased, it's a deposit (+)
            # If balance decreased, it's a withdrawal (-)
            if balance_change > 0:
                amount = Decimal(str(amount_value))   # Incoming (+)
            elif balance_change < 0:
                amount = Decimal(str(-amount_value))  # Outgoing (-)
            else:
                amount = transaction_amount  # Use original sign
        else:
            # Fallback: Use reference patterns for E-TRANSFERs
            if 'E-TRANSFER' in description.upper():
                context_start = max(0, line_index - 3)
                context_end = min(len(all_lines), line_index + 3)
                context_text = '\n'.join(all_lines[context_start:context_end])
                
                if re.search(r'\b105\d{9}\b', context_text):
                    amount = Decimal(str(-amount_value))  # Outgoing (-)
                elif re.search(r'\b011\d{9}\b', context_text):
                    amount = Decimal(str(amount_value))   # Incoming (+)
                else:
                    amount = Decimal(str(amount_value))   # Default to incoming
            else:
                # Use transaction type defaults
                if any(t in description.upper() for t in ['PREAUTHORIZED DEBIT', 'SERVICE CHARGE']):
                    amount = Decimal(str(-amount_value))  # Always outgoing
                elif 'DEPOSIT' in description.upper():
                    amount = Decimal(str(amount_value))   # Always incoming
                else:
                    amount = transaction_amount  # Use original amount
        
        # Use current date as placeholder (will be updated with context)
        date_obj = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Auto-categorize without changing description
        category_id = auto_categorize_transaction(description, amount, 'CIBC')
        
        return {
            'date': date_obj,
            'description': description,  # Preserve original with transaction type
            'amount': amount,
            'balance': Decimal(balance_str.replace(',', '')),
            'category_id': category_id
        }
    except (ValueError, TypeError):
        return None


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
        'account_type': account_type or 'CHECKING',  # Use passed account_type or default
        'account_name': '',
        'last_4_digits': '0000'
    }
    
    if bank_type == 'CIBC':
        # CIBC patterns - including checking and credit card formats
        patterns = [
            # Two-group patterns first (most specific)
            r'(\d{4})\s+X{4}\s+X{4}\s+(\d{4})',  # CIBC credit card format: "4505 XXXX XXXX 7841"
            r'(\d{4})\s+(\d{3})',  # "1234 567" format - capture both groups
            # Single-group checking account patterns 
            r'ACCOUNT[:\s]*(\d{4}[\s-]+\d{3})',  # Account: 1234 567 or Account: 1234-567
            r'ACCOUNT\s+NUMBER[:\s]*(\d{4}[\s-]*\d{3}[\s-]*\d{3})',  # 1234-567-890
            r'ACCOUNT\s+NUMBER[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})', # Standard format
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{3}[\s-]*\d{3})',
            r'(\d{4})\s*CHEQUING',  # Account ending in checking statement
            r'(\d{4})\s*CHECKING',
            r'CHEQUING\s+ACCOUNT\s+(\d{4})',  # "CHEQUING ACCOUNT 1234"
            r'CHECKING\s+ACCOUNT\s+(\d{4})',
            # Other patterns
            r'\*{4}(\d{4})',
            r'(\d{4})\s*SAVINGS',
            r'(\d{4})\s*CREDIT'
        ]
        
        # Account type already set from parameter or default
            
    elif bank_type == 'RBC':
        # RBC patterns
        patterns = [
            r'ACCOUNT\s+(\d{5}-\d{7})',  # RBC format: 12345-1234567
            r'ACCOUNT[:\s]*(\d{4}[\s-]*\d{4}[\s-]*\d{3,4})',
            r'\*{4}(\d{4})',
            r'(\d{4})\s*CHEQUING',
            r'(\d{4})\s*SAVINGS'
        ]
        
        # Account type already set from parameter or default
            
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
            # Handle different pattern types
            if len(match.groups()) == 2:
                if 'X{4}' in pattern:
                    # This is the "4505 XXXX XXXX 7841" credit card format
                    first_four = match.group(1)
                    last_four = match.group(2)
                    account_info['account_number'] = f"{first_four}XXXX{last_four}"
                    account_info['last_4_digits'] = last_four
                else:
                    # This is likely the "1234 567" checking account format
                    part1 = match.group(1)
                    part2 = match.group(2)
                    full_number = f"{part1}{part2}"
                    account_info['account_number'] = full_number
                    # For CIBC checking format "1234 567", use the second part (567) as the identifier
                    # but pad with zeros if needed to make it 4 digits for consistency
                    if len(part2) == 3:
                        account_info['last_4_digits'] = f"0{part2}"  # 567 becomes 0567
                    else:
                        account_info['last_4_digits'] = part2 if len(part2) >= 4 else full_number[-4:]
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


def extract_account_balance(text: str, bank_type: str, account_type: str = None) -> float:
    """Extract current account balance from bank statement."""
    text_upper = text.upper()
    
    if bank_type == 'CIBC':
        # CIBC patterns for balance - ordered by priority based on account type
        if account_type and account_type.upper() == 'CHECKING':
            # For checking accounts, prioritize closing balance
            patterns = [
                r'CLOSING\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'ENDING\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'FINAL\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'CURRENT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'STATEMENT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'ACCOUNT\s+BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})',
                r'BALANCE[:\s]*\$([+-]?\d{1,3}(?:,\d{3})*\.\d{2})'
            ]
        else:
            # For credit cards and other accounts, use existing patterns
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