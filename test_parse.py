import pypdf
import json
import re

def parse_schedule(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    all_schedules = {}

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        
        # Extract class name
        # Looking for something like "班級: 國一 1" or similar
        class_match = re.search(r'班級:\s*([^\s]+)\s*([^\s]*)', text)
        if class_match:
            class_name = class_match.group(1) + (class_match.group(2) if class_match.group(2) else "")
            class_name = class_name.strip()
        else:
            class_name = f"Unknown_Page_{i+1}"

        # Initialize schedule structure
        # We want Day 1-5, Periods 1-9
        # Weekdays: 一, 二, 三, 四, 五
        schedule = {
            "mon": [""] * 9,
            "tue": [""] * 9,
            "wed": [""] * 9,
            "thu": [""] * 9,
            "fri": [""] * 9
        }

        # This is a bit tricky because text extraction might not be simple
        # Let's try to look for period markers and times
        lines = text.split('\n')
        
        # Search for lines that look like periods
        # e.g. "第 一 節 08:05 ... 08:50"
        
        # Actually, let's use the OCR text structure if possible, 
        # but pypdf might give us something else.
        # Let's see what pypdf gives us by printing the first page.
        if i == 0:
            print(f"DEBUG: Page 1 Text:\n{text}\n---")

    return {}

if __name__ == "__main__":
    # Test on the file
    parse_schedule("d:/classVSclass/114-2班級課表(0309起實施).pdf")
