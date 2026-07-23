from supabase import create_client

# 请将下方两处替换为你最新的数据
URL = "https://lnbtbsnwmnwwdbojlscl.supabase.co"
# 这里直接粘贴你刚才新生成的那个 sb_secret_ 开头的 Key
KEY = "sb_secret_4swt3PACrR6szRbk6tI_hw_Yf7iPiKA"

try:
    supabase = create_client(URL, KEY)
    # 发起一个简单的查询，不需要读取数据，只是为了测试连通性
    res = supabase.table("students").select("count").execute()
    print("连接成功！")
except Exception as e:
    print(f"连接失败，报错信息：{e}")