import pandas as pd
from supabase import create_client
import os

# 配置
URL = "https://lnbtbsnwmnwwdbojlscl.supabase.co"
KEY = "sb_secret_4swt3PACrR6szRbk6tI_hw_Yf7iPiKA" # 保持与 test_conn.py 一致
CSV_PATH = r"E:\student_system\students_grades.csv" # 使用绝对路径

supabase = create_client(URL, KEY)

# 读取数据
df = pd.read_csv(CSV_PATH)

# 1. 导入学生信息
# 使用 .to_dict('records') 转换
students_list = df[["姓名", "学号", "所属学校"]].drop_duplicates().to_dict('records')
# 手动改一下 key 的名称以匹配数据库
formatted_students = [{"name": s["姓名"], "student_id": str(s["学号"]), "school_name": s["所属学校"]} for s in students_list]

print("开始导入学生数据...")
supabase.table("students").insert(formatted_students).execute()
print("学生数据导入完成。")

# 2. 导入成绩数据
print("开始导入成绩数据...")
for _, row in df.iterrows():
    # 对每科成绩进行插入
    for subject in ["语文", "数学", "英语"]:
        grade_entry = {
            "student_id": str(row["学号"]),
            "subject": subject,
            "score": float(row[subject]),
            "exam_date": "2026-05-01"
        }
        supabase.table("grades").insert(grade_entry).execute()

print("全部数据导入成功！")