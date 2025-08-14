#!/usr/bin/env python3
import pdfplumber

def debug_pdf_content(filename):
    print(f"🔍 Analyzing PDF: {filename}")
    
    try:
        with pdfplumber.open(filename) as pdf:
            print(f"📄 Total pages: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\n📖 Page {page_num}:")
                print("=" * 50)
                
                # Try table extraction
                tables = page.extract_tables()
                if tables:
                    print(f"📊 Found {len(tables)} table(s)")
                    for i, table in enumerate(tables):
                        print(f"\nTable {i+1}:")
                        for row_idx, row in enumerate(table[:5]):  # Show first 5 rows
                            print(f"Row {row_idx}: {row}")
                        if len(table) > 5:
                            print(f"... and {len(table)-5} more rows")
                else:
                    print("📊 No tables found")
                
                # Get text content
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    print(f"\n📝 Text content ({len(lines)} lines):")
                    print("First 10 lines:")
                    for i, line in enumerate(lines[:10]):
                        print(f"{i+1:2d}: {line.strip()}")
                    
                    if len(lines) > 10:
                        print(f"... and {len(lines)-10} more lines")
                        
                    # Look for potential transaction patterns
                    print("\n🔍 Lines with date patterns:")
                    import re
                    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
                    for i, line in enumerate(lines):
                        if re.search(date_pattern, line):
                            print(f"Line {i+1}: {line.strip()}")
                else:
                    print("📝 No text content found")
    
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

if __name__ == "__main__":
    debug_pdf_content("test.pdf")