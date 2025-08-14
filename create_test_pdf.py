#!/usr/bin/env python3
"""
Create a test PDF that simulates a bank statement for testing PDF parsing.
"""

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    def create_bank_statement_pdf():
        filename = "test_bank_statement.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Bank header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "First National Bank")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 70, "Account Statement")
        c.drawString(50, height - 90, "Account: 1234567890")
        
        # Transaction table header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 130, "Date")
        c.drawString(150, height - 130, "Description")
        c.drawString(350, height - 130, "Amount")
        
        # Draw line under header
        c.line(50, height - 140, 500, height - 140)
        
        # Sample transactions
        transactions = [
            ("01/20/2024", "Walmart Supercenter", "-67.45"),
            ("01/21/2024", "Direct Deposit Payroll", "1250.00"),
            ("01/22/2024", "Shell Gas Station", "-42.33"),
            ("01/23/2024", "Amazon Purchase", "-89.99"),
            ("01/24/2024", "ATM Withdrawal", "-60.00"),
            ("01/25/2024", "Starbucks Coffee", "-5.75")
        ]
        
        c.setFont("Helvetica", 10)
        y_position = height - 160
        
        for date, desc, amount in transactions:
            c.drawString(50, y_position, date)
            c.drawString(150, y_position, desc)
            c.drawString(350, y_position, amount)
            y_position -= 20
        
        c.save()
        print(f"✅ Created {filename}")
        return filename
    
    if __name__ == "__main__":
        create_bank_statement_pdf()

except ImportError:
    print("❌ ReportLab not installed. Creating simple text file instead...")
    
    # Fallback: Create a simple text file that looks like a PDF statement
    filename = "test_bank_statement.txt"
    content = """First National Bank
Account Statement
Account: 1234567890

Date        Description              Amount
01/20/2024  Walmart Supercenter      -67.45
01/21/2024  Direct Deposit Payroll   1250.00  
01/22/2024  Shell Gas Station        -42.33
01/23/2024  Amazon Purchase          -89.99
01/24/2024  ATM Withdrawal           -60.00
01/25/2024  Starbucks Coffee         -5.75
"""
    
    with open(filename, 'w') as f:
        f.write(content)
    print(f"✅ Created {filename} (text format)")