import pandas as pd
import random

# 1. 定义学校和学生数据
schools = ["完小A", "完小B", "完小C", "镇小学A", "镇小学B", "县小学"]
subjects = ["语文", "数学", "英语"]

data = []
for i in range(1, 201):
    student = {
        "学号": f"2026{i:03d}",
        "姓名": f"学生{i}",
        "所属学校": random.choice(schools),
        "语文": random.randint(60, 100),
        "数学": random.randint(50, 100),
        "英语": random.randint(55, 100),
    }
    data.append(student)

# 2. 保存为 CSV 文件
df = pd.DataFrame(data)
df.to_csv("students_grades.csv", index=False, encoding='utf-8-sig')
print("数据已生成：students_grades.csv")