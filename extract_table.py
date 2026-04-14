import pdfplumber
import json

def extract_tables(pdf_path):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extract basic info from the top
            text = page.extract_text()
            lines = text.split('\n')
            class_info = ""
            for line in lines:
                if "班級:" in line:
                    class_info = line.split("班級:")[1].split("導師:")[0].strip()
                    break
            
            # Extract tables
            table = page.extract_table()
            if table:
                all_data.append({
                    "class": class_info,
                    "table": table
                })
            
            if i == 0:
                print(f"DEBUG Page 1 Table:\n{table}")

    with open("schedule_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_tables("d:/classVSclass/114-2班級課表(0309起實施).pdf")
