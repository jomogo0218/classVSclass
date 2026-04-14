import json

def process_schedules(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = {
        "classes": [],
        "schedules": {}
    }

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    # We'll map rows to period numbers (1-9)
    # Row index in pdfplumber table for each period
    # Based on observation:
    # Row 1: 早自習 (Skip for now or keep as 0)
    # Row 2: 1
    # Row 3: 2
    # Row 4: 3
    # Row 5: 4
    # Row 6: 5
    # Row 7: 6
    # Row 8: 7
    # Row 9: 8 (Remedial)
    # Row 10: 9 (Advance)
    
    period_rows = list(range(1, 11)) 

    for entry in data:
        class_name = entry.get("class", "Unknown")
        if not class_name or class_name == "Unknown":
            continue
        
        result["classes"].append(class_name)
        
        table = entry.get("table", [])
        if not table or len(table) < 11:
            continue
            
        class_schedule = {day: [] for day in days}
        
        for p_idx, row_idx in enumerate(period_rows):
            if row_idx >= len(table):
                for day in days:
                    class_schedule[day].append("")
                continue
                
            row = table[row_idx]
            # Days are at indices 3, 4, 5, 6, 7
            for d_idx, day in enumerate(days):
                cell_content = row[d_idx + 3] if (d_idx + 3) < len(row) else ""
                if cell_content is None:
                    cell_content = ""
                # Clean up: take subject and teacher
                lines = [l.strip() for l in cell_content.split("\n") if l.strip()]
                subject = lines[0] if len(lines) > 0 else ""
                teacher = lines[1] if len(lines) > 1 else ""
                
                full_info = f"{subject}|{teacher}" if teacher else subject
                class_schedule[day].append(full_info)
        
        result["schedules"][class_name] = class_schedule

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_schedules("d:/classVSclass/schedule_data.json", "d:/classVSclass/schedules.json")
