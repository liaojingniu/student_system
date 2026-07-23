import streamlit as st
import pandas as pd
import datetime
from supabase import create_client

# --- 1. 页面基本配置 ---
st.set_page_config(
    page_title="学生成绩分析与教学诊断报告",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. 注入精细化 A4 打印与 CSS 优化 ---
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 模拟 A4 纸张容器 */
    .main .block-container {
        max-width: 800px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        background-color: #ffffff;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border-radius: 8px;
        margin-top: 15px;
        margin-bottom: 20px;
        padding-left: 35px !important;
        padding-right: 35px !important;
    }

    /* 报告页眉 */
    .report-header {
        border-bottom: 3px solid #1d4ed8;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .report-title {
        font-size: 24px;
        font-weight: 800;
        color: #1e3a8a;
        margin: 0;
        text-align: center;
    }
    .meta-info {
        font-size: 11px;
        color: #64748b;
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        background: #f8fafc;
        padding: 6px 12px;
        border-radius: 4px;
    }

    /* KPI 卡片 */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin: 15px 0 20px 0;
    }
    .kpi-card {
        flex: 1;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #2563eb;
        border-radius: 6px;
        padding: 10px 6px;
        text-align: center;
    }
    .kpi-title { font-size: 12px; color: #64748b; font-weight: 600; }
    .kpi-value { font-size: 22px; font-weight: 800; color: #1e293b; margin: 2px 0; }
    .kpi-sub { font-size: 10px; color: #94a3b8; }

    /* 模块标题 */
    .section-title {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
        border-left: 4px solid #2563eb;
        padding-left: 8px;
        margin: 20px 0 12px 0;
    }

    /* 自定义横向柱状图样式 */
    .dist-bar-box {
        margin: 8px 0;
    }
    .dist-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #334155;
        font-weight: 600;
        margin-bottom: 3px;
    }
    .dist-bar-bg {
        background-color: #e2e8f0;
        border-radius: 4px;
        height: 12px;
        overflow: hidden;
    }
    .dist-bar-fill {
        background-color: #2563eb;
        height: 100%;
        border-radius: 4px;
    }

    /* 页脚与断行 */
    .footer-notes {
        font-size: 11px;
        color: #94a3b8;
        text-align: center;
        border-top: 1px solid #e2e8f0;
        padding-top: 10px;
        margin-top: 25px;
    }
    .page-break-line {
        margin: 30px 0;
        border-bottom: 1px dashed #cbd5e1;
    }

    @media print {
        [data-testid="stSidebar"] { display: none !important; }
        .stButton { display: none !important; }
        .main .block-container {
            box-shadow: none !important;
            margin: 0 !important;
            padding: 0 !important;
            max-width: 100% !important;
        }
        .page-break-line {
            page-break-after: always;
            break-after: page;
            visibility: hidden;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化 Supabase 客户端 ---
URL = "https://lnbtbsnwmnwwdbojlscl.supabase.co"
KEY = "sb_secret_4swt3PACrR6szRbk6tI_hw_Yf7iPiKA"

supabase = create_client(URL, KEY)

# --- 4. 数据加载 ---
@st.cache_data(ttl=60)
def load_data():
    s_res = supabase.table("students").select("*").execute()
    g_res = supabase.table("grades").select("*").execute()
    
    df_s = pd.DataFrame(s_res.data)
    df_g = pd.DataFrame(g_res.data)
    
    if not df_s.empty and not df_g.empty:
        df_merged = pd.merge(df_g, df_s, left_on="student_id", right_on="student_id", how="left")
        df_merged['score'] = pd.to_numeric(df_merged['score'])
        return df_merged
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("未能获取到有效数据，请检查 Supabase 数据库。")
    st.stop()

# --- 5. 侧边栏控制面板 ---
st.sidebar.title("🎛️ 报告导出控制")

schools = ["全部学校"] + list(df["school_name"].dropna().unique()) if "school_name" in df.columns else ["全部学校"]
selected_school = st.sidebar.selectbox("🏫 筛选目标学校", schools)

filtered_df = df if selected_school == "全部学校" else df[df["school_name"] == selected_school]

st.sidebar.markdown("---")
st.sidebar.success("📄 提示：按 **`Ctrl + P`** 可导出无侧边栏的 2页 A4 PDF 报告！")

current_time = datetime.datetime.now().strftime("%Y-%m-%d")
school_title = selected_school if selected_school != "全部学校" else "全区总体"

# ==============================================================================
# 📄 第 1 页：封面元数据 + KPI 卡片 + 折线图 + 横向条形图
# ==============================================================================
st.markdown(f"""
<div class="report-header">
    <div class="report-title">📊 {school_title} 学生成绩分析与学情诊断报告</div>
    <div class="meta-info">
        <span><b>分析周期：</b> 2026年夏季学期</span>
        <span><b>生成日期：</b> {current_time}</span>
        <span><b>样本容量：</b> {len(filtered_df)} 人次</span>
    </div>
</div>

<div class="section-title">一、 核心教学质量指标 (KPI)</div>

<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">总参考人次</div>
        <div class="kpi-value">{len(filtered_df)}</div>
        <div class="kpi-sub">覆盖学生样本</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">总体平均分</div>
        <div class="kpi-value">{filtered_df['score'].mean():.1f}</div>
        <div class="kpi-sub">满分 100 分</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">整体及格率</div>
        <div class="kpi-value">{(filtered_df['score'] >= 60).mean() * 100:.1f}%</div>
        <div class="kpi-sub">60分及以上</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">高分优秀率</div>
        <div class="kpi-value">{(filtered_df['score'] >= 85).mean() * 100:.1f}%</div>
        <div class="kpi-sub">85分及以上</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 换成图表 1：学科平均分折线图
st.markdown("<div class='section-title'>二、 各学科平均分走势与对比</div>", unsafe_allow_html=True)
avg_scores = filtered_df.groupby("subject")["score"].mean().reset_index()
avg_scores["score"] = avg_scores["score"].round(1)

st.line_chart(avg_scores.set_index("subject"), height=200)

# 换成图表 2：成绩等级分布（自定精细横向比例条，解决文字旋转问题）
st.markdown("<div class='section-title'>三、 成绩梯队分布图（按人次与百分比）</div>", unsafe_allow_html=True)

bins = [0, 60, 75, 85, 101]
labels = ['不及格 (<60分)', '中等 (60-74分)', '良好 (75-84分)', '优秀 (85-100分)']
filtered_df['score_level'] = pd.cut(filtered_df['score'], bins=bins, labels=labels, right=False)
level_counts = filtered_df['score_level'].value_counts().reindex(labels).fillna(0)

total_count = len(filtered_df)

for lvl, count in level_counts.items():
    pct = (count / total_count * 100) if total_count > 0 else 0
    st.markdown(f"""
    <div class="dist-bar-box">
        <div class="dist-bar-label">
            <span>{lvl}</span>
            <span>{int(count)} 人 ({pct:.1f}%)</span>
        </div>
        <div class="dist-bar-bg">
            <div class="dist-bar-fill" style="width: {pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer-notes">页码：第 1 页 / 共 2 页 | 学生成绩管理与诊断系统</div>
<div class="page-break-line"></div>
""", unsafe_allow_html=True)

# ==============================================================================
# 📄 第 2 页：能力维度可视化 + 详细数据 + 教研建议
# ==============================================================================
st.markdown(f"""
<div class="report-header">
    <div class="report-title">{school_title} - 学科能力模型与教研诊断</div>
    <div class="meta-info">
        <span><b>诊断引擎：</b> 规则匹配诊断 v1.5</span>
        <span><b>生成时间：</b> {current_time}</span>
    </div>
</div>

<div class="section-title">四、 各学科综合能力掌握度</div>
""", unsafe_allow_html=True)

pass_score = 60
excellent_score = 85

subject_stats = filtered_df.groupby("subject")["score"].agg(
    平均分=lambda x: round(x.mean(), 1),
    最高分="max",
    最低分="min",
    及格率=lambda x: round((x >= pass_score).mean() * 100, 1),
    优秀率=lambda x: round((x >= excellent_score).mean() * 100, 1)
).reset_index()

for _, row in subject_stats.iterrows():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write(f"**{row['subject']}** (`{row['平均分']}分`)")
    with col2:
        progress_val = min(max(row['平均分'] / 100.0, 0.0), 1.0)
        st.progress(progress_val)

st.markdown("<div class='section-title'>五、 各学科详细数据汇总</div>", unsafe_allow_html=True)

display_stats = subject_stats.copy()
display_stats['及格率'] = display_stats['及格率'].astype(str) + '%'
display_stats['优秀率'] = display_stats['优秀率'].astype(str) + '%'
st.dataframe(display_stats, use_container_width=True, hide_index=True)

st.markdown("<div class='section-title'>六、 重点关注预警与针对性教研建议</div>", unsafe_allow_html=True)

low_score_students = filtered_df[filtered_df["score"] < 60]
if not low_score_students.empty:
    st.warning(f"⚠️ **低分预警**：本次共有 **{len(low_score_students)}** 人次成绩低于 60 分，建议安排课后专项补差。")

for _, row in subject_stats.iterrows():
    subj = row['subject']
    avg = row['平均分']
    pass_rate = row['及格率']
    
    if pass_rate < 70:
        st.error(f"🔴 **{subj}**（均分: {avg} | 及格率: {pass_rate}%）：及格率偏低，建议开展基础知识点专项巩固，降低作业难度梯度。")
    elif avg >= 80:
        st.success(f"🟢 **{subj}**（均分: {avg} | 优秀率: {row['优秀率']}%）：整体表现优异，建议保持当前授课节奏，可适当增加高阶拓展题。")
    else:
        st.warning(f"🟡 **{subj}**（均分: {avg} | 及格率: {pass_rate}%）：表现平稳，主要提升潜力集中在 60-75 分中等生群体，建议加强课堂限时训练。")

st.markdown("""
<div class="footer-notes">
    免责声明：本报告由系统基于数据库自动生成，数据结果仅供校内教研与教学改进参考。<br>
    页码：第 2 页 / 共 2 页
</div>
""", unsafe_allow_html=True)