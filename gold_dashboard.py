
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="黄金外汇日内趋势表", page_icon="📊", layout="wide")
st.title("📊 黄金外汇日内趋势表")

# --- 定义核心计算逻辑 ---
def calculate_signals(bond_rate, usd_index, vix, open_interest):
    # 长线信号 J (黄金/非美)
    J = -(usd_index/100) + (4 - bond_rate)/4 + (0.5 if vix > 20 else 0) - open_interest*0.1
    J_label = "强烈看多" if J >= 0.8 else "偏多" if J >= 0.3 else "强烈看空" if J <= -0.8 else "偏空"
    
    # 日内短线信号 N/P
    N = -(bond_rate/100) + (4 - usd_index)/4 + (0.6 if vix > 22 else 0) - open_interest*0.12
    P = -(usd_index/100) + (4 - bond_rate)/4 + (0.5 if vix > 22 else 0) - open_interest*0.18
    return J, J_label, N, P

# --- 模拟：这里替换成你每天真实获取的数据 ---
# 示例：3/13 数据（你每天运行时会自动获取最新值）
today_data = {
    "日期": datetime.now().strftime("%Y/%m/%d"),
    "美债收益率": 4.25,    # 示例值，替换成真实数据
    "美元指数": 100.00,   # 示例值
    "VIX": 24.26,        # 示例值
    "期货持仓": 209000,  # 示例值
    "亏平衡通胀": 2.38   # 示例值
}

# --- 计算信号 ---
J, J_label, N, P = calculate_signals(
    bond_rate=today_data["美债收益率"],
    usd_index=today_data["美元指数"],
    vix=today_data["VIX"],
    open_interest=today_data["期货持仓"]
)

# --- 展示当前核心指标 ---
st.subheader("最新核心指标与信号")
col1, col2, col3, col4 = st.columns(4)
col1.metric("美债收益率", f"{today_data['美债收益率']:.2f}")
col2.metric("美元指数", f"{today_data['美元指数']:.2f}")
col3.metric("VIX 恐慌指数", f"{today_data['VIX']:.2f}", help=J_label)
col4.metric("期货持仓", f"{today_data['期货持仓']:.0f}")

# --- 展示信号结果 ---
st.divider()
st.subheader("📈 信号分析")
cl, cr = st.columns(2)
cl.metric("长线信号 (黄金/非美)", value="", help=J_label)
cl.write(f"**信号方向**: {J_label}")
cl.write(f"**数值**: {J:.4f}")

cr.metric("日内短线信号", value="", help="日内交易参考")
cr.write(f"信号1 (日内多): {N:.4f}")
cr.write(f"信号2 (日内空): {P:.4f}")

# --- 历史数据记录表 ---
st.divider()
st.subheader("📜 历史数据回溯 (3/10 - 3/13)")
# 注意：这里的字段名要和你之前的定义一致
history_data = [
    {"日期": "2026/3/10", "美债收益率": 4.11, "美元指数": 98.52, "VIX": 17, "期货持仓": 309000, "亏平衡通胀": 2.35},
    {"日期": "2026/3/11", "美债收益率": 4.18, "美元指数": 99.10, "VIX": 24.40, "期货持仓": 228300, "亏平衡通胀": 2.33},
    {"日期": "2026/3/12", "美债收益率": 4.22, "美元指数": 99.40, "VIX": 24.30, "期货持仓": 213100, "亏平衡通胀": 2.36},
    {"日期": "2026/3/13", "美债收益率": 4.25, "美元指数": 100.00, "VIX": 24.26, "期货持仓": 209000, "亏平衡通胀": 2.38},
]
history_df = pd.DataFrame(history_data)
st.dataframe(history_df, use_container_width=True, hide_index=True)
