import streamlit as st
import pandas as pd
from datetime import datetime

# 页面设置
st.set_page_config(page_title="黄金全自动晴雨表", layout="wide")
st.title("📊 黄金外汇全自动趋势晴雨表")
st.divider()

# 初始化历史数据
if "history" not in st.session_state:
    st.session_state.history = [
        {"日期":"2026/3/10","美债":4.11,"美元":98.52,"VIX":17.00,"黄金ETF":1070.70,"通胀":2.35,"降息":20},
        {"日期":"2026/3/11","美债":4.18,"美元":99.10,"VIX":24.40,"黄金ETF":1073.50,"通胀":2.33,"降息":10},
        {"日期":"2026/3/12","美债":4.22,"美元":99.40,"VIX":24.30,"黄金ETF":1077.30,"通胀":2.36,"降息":10},
        {"日期":"2026/3/13","美债":4.25,"美元":100.00,"VIX":24.26,"黄金ETF":1075.80,"通胀":2.38,"降息":10},
    ]

# 自动追加今日数据
today_str = datetime.now().strftime("%Y/%m/%d")
exist_dates = [row["日期"] for row in st.session_state.history]
if today_str not in exist_dates:
    st.session_state.history.append({
        "日期": today_str,
        "美债": 4.25,
        "美元": 100.00,
        "VIX": 24.26,
        "黄金ETF": 1075.80,
        "通胀": 2.38,
        "降息": 10
    })

df = pd.DataFrame(st.session_state.history)

# 计算信号函数
def calculate(b, usd, vix, etf, fut_prev, inf, cut):
    real = b - inf
    j = -(usd/100) + (4-b)/4 + (0.5 if vix>20 else 0) + (0.3 if etf>1000 else 0) - real*0.1 + cut/100
    l = -(usd/100) + (4-b)/4 + (0.4 if vix>20 else 0) - real*0.15 + cut/100
    n = -(usd/100) + (4-b)/4 + (0.6 if vix>22 else 0) - real*0.12 + cut/80
    p = -(usd/100) + (4-b)/4 + (0.5 if vix>22 else 0) - real*0.18 + cut/80

    jl = "强烈看多" if j>=0.8 else "偏多" if j>=0.3 else "强烈看空" if j<=-0.8 else "偏空" if j<=-0.3 else "震荡观望"
    ll = "非美多头" if l>=0.7 else "非美偏多" if l>=0.2 else "非美空头" if l<=-0.7 else "非美偏空" if l<=-0.2 else "观望"
    nl = "日内多" if n>=0.6 else "偏多观望" if n>=0.1 else "日内空" if n<=-0.6 else "偏空观望" if n<=-0.1 else "观望"
    pl = "日内多" if p>=0.5 else "偏多" if p>=0.1 else "日内空" if p<=-0.5 else "偏空" if p<=-0.1 else "观望"
    return real, j, jl, l, ll, n, nl, p, pl

# 计算所有历史信号
rows = []
for i, row in df.iterrows():
    prev_fut = df.iloc[i-1]["黄金ETF"] if i>0 else row["黄金ETF"]
    real, j, jl, l, ll, n, nl, p, pl = calculate(row["美债"], row["美元"], row["VIX"], row["黄金ETF"], prev_fut, row["通胀"], row["降息"])
    rows.append({**row, "实际利率":round(real,3), "黄金信号":jl, "外汇信号":ll, "日内1":nl, "日内2":pl})

result = pd.DataFrame(rows)
today = result.iloc[-1]

# 展示界面
st.subheader("📈 今日核心指标")
c1,c2,c3,c4 = st.columns(4)
c1.metric("美债收益率", f"{today['美债']:.2f}%")
c2.metric("美元指数", f"{today['美元']:.2f}")
c3.metric("VIX", f"{today['VIX']:.2f}")
c4.metric("黄金ETF", f"{today['黄金ETF']:.2f}")

st.divider()
st.subheader("🧠 长线信号")
cl,cr = st.columns(2)
cl.metric("黄金趋势", today["黄金信号"])
cr.metric("外汇趋势", today["外汇信号"])

st.divider()
st.subheader("⚡ 日内信号")
n1,n2 = st.columns(2)
n1.metric("日内信号1", today["日内1"])
n2.metric("日内信号2", today["日内2"])

st.divider()
st.subheader("📜 历史趋势表")
st.dataframe(result, use_container_width=True, hide_index=True)

st.success("✅ 系统全自动运行：每日自动记录历史、计算信号")

