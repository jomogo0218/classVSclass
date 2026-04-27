import json
import os

def update_9th_period():
    schedules_path = 'd:/classVSclass/schedules.json'
    with open(schedules_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    teachers = {
        "高一忠": ["陳國棟", "鄧靜蓓", "余姿瑩", "陳國棟", "葉峰銘"],
        "高一孝": ["王珊璞", "楊培渝", "楊培渝", "王倫筑", "楊于萱"],
        "高一仁": ["黃宇正", "陳勝璿", "許儷瓊", "黃宇正", "晏文珍"],
        "高一愛": ["鍾雯慧", "林俊銘", "林俊銘", "李毓旋", "洪翊敏"],
        "高一信": ["劉娜均", "張君楷", "李映柔", "張君楷", "陳明政"],
        "高二忠": ["許曜昕", "黃子信", "黃子信", "何月娥", "張泰瑞"],
        "高二孝": ["黃文良", "莊芯螢", "傅詮閣", "黃佩綾", "黃文良"],
        "高二仁": ["蘇紫甄", "陳昭瑜", "袁鳳笙", "袁鳳笙", "謝琬瑩"],
        "高二愛": ["蔡一德", "洪羿廷", "鍾慧容", "鍾慧容", "翁晨珈"],
        "高二信": ["游韻婷", "陳耀祖", "林宏亮", "彭舒渝", "陳耀祖"],
        "高三忠": ["晏文珍", "黃崧浩", "王富寬", "黃崧浩", "陳昭瑜"],
        "高三孝": ["洪翊敏", "翁晨珈", "姚譯婷", "洪羿廷", "姚譯婷"],
        "高三仁": ["陳明政", "周佩蓉", "周佩蓉", "崔若喬", "蘇紫甄"],
        "高三愛": ["蔡孟儒", "蔡孟儒", "謝琬瑩", "周芳如", "莊芯螢"],
        "高三信": ["楊于萱", "傅詮閣", "張淑枝", "鍾雯慧", "張淑枝"]
    }

    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    
    count = 0
    for class_name, week_teachers in teachers.items():
        if class_name in data['schedules']:
            for i, day in enumerate(days):
                teacher = week_teachers[i]
                # Ensure the list has at least 10 items (index 0 to 9)
                while len(data['schedules'][class_name][day]) < 10:
                    data['schedules'][class_name][day].append("")
                
                data['schedules'][class_name][day][9] = f"精進學習|{teacher}"
                count += 1
        else:
            print(f"Warning: Class {class_name} not found in schedules.json")

    with open(schedules_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully updated 9th period for {len(teachers)} classes ({count} slots).")

if __name__ == "__main__":
    update_9th_period()
