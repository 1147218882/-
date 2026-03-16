import streamlit as st
import pandas as pd
from datetime import datetime

# ======================
# 页面设置
# ======================
st.set_page_config(page_title="黄金晴雨表", layout="wide")
st.title("📊 黄金外汇趋势晴雨表")
st.caption("数据准确 → 信号可靠 → 自动记录历史")
st.divider()

# ======================
# 初始化历史数据
# ======================
if "history" not in st.session_state:
    st.session_state.history = [
        {"日期":"2026/3/10","美债":4.11,"美元":98.52,"VIX":17.00,"黄金ETF":1070.70,"通胀":2.35,"降息":20},
        {"日期":"2026/3/11","美债":4.18,"美元":99.10,"VIX":24.40,"黄金ETF":1073.50,"通胀":2.33,"降息":10},
        {"日期":"2026/3/12","美债":4.22,"美元":99.40,"VIX":24.30,"黄金ETF":1077.30,"通胀":2.36,"降息":10},
        {"日期":"2026/3/13","美债":4.25,"美元":100.00,"VIX":24.26,"黄金ETF":1075.80,"通胀":2.38,"降息":10},
        {"日期":"2026/3/16","美债":4.27,"美元":100.15,"VIX":23.90,"黄金ETF":1074.20,"通胀":2.38,"降息":25},
    ]

today_str = datetime.now().strftime("%Y/%m/%d")

# ======================
# 侧边栏：今日数据录入
# ======================
with st.sidebar:
    st.subheader("📝 今日数据")
    input_date = st.text_input("日期", today_str)
    bond = st.number_input("美债收益率", value=4.27, step=0.01)
    usd = st.number_input("美元指数", value=100.15, step=0.01)
    vix = st.number_input("VIX恐慌指数", value=23.90, step=0.01)
    gold = st.number_input("黄金ETF(GLD)", value=1074.20, step=0.01)
    inf = st.number_input("通胀率", value=2.38, step=0.01)
    cut = st.number_input("降息预期", value=25, step=5)

    if st.button("✅ 添加今日数据"):
        # 去重：如果今天已经有了就不重复加
        dates = [row["日期"] for row in st.session_state.history]
        if input_date not in dates:
            st.session_state.history.append({
                "日期": input_date,
                "美债": bond,
                "美元": usd,
                "VIX": vix,
                "黄金ETF": gold,
                "通胀": inf,
                "降息": cut
            })
            st.success("添加成功！")
        else:
            st.warning("今天数据已存在")

# ======================
# 自动计算所有信号
# ======================
df = pd.DataFrame(st.session_state.history)

def calculate_all(df_row, prev_etf):
    b = df_row["美债"]
    usd = df_row["美元"]
    vix = df_row["VIX"]
    etf = df_row["黄金ETF"]
    inf = df_row["通胀"]
    cut = df_row["降息"]

    real = b - inf

    j = -(usd/100) + (4-b)/4 + (0.5 if vix>20 else 0) + (0.3 if etf>1000 else 0) + (0.2 if etf>prev_etf else 0) - real*0.1 + cut/100
    l = -(usd/100) + (4-b)/4 + (0.4 if vix>20 else 0) - real*0.15 + cut/100
    n = -(usd/100) + (4-b)/4 + (0.6 if vix>22 else 0) - real*0.12 + cut/80
    p = -(usd/100) + (4-b)/4 + (0.5 if vix>22 else 0) - real*0.18 + cut/80

    gold_signal = "强烈看多" if j>=0.8 else "偏多" if j>=0.3 else "强烈看空" if j<=-0.8 else "偏空" if j<=-0.3 else "震荡观望"
    fx_signal   = "非美多头" if l>=0.7 else "非美偏多" if l>=0.2 else "非美空头" if l<=-0.7 else "非美偏空" if l<=-0.2 else "观望"
    intra1      = "日内多" if n>=0.6 else "偏多观望" if n>=0.1 else "日内空" if n<=-0.6 else "偏空观望" if n<=-0.1 else "观望"
    intra2      = "日内多" if p>=0.5 else "偏多" if p>=0.1 else "日内空" if p<=-0.5 else "偏空" if p<=-0.1 else "观望"

    return real, gold_signal, fx_signal, intra1, intra2

# 逐行计算
result = []
for i, row in df.iterrows():
    prev_etf = df.iloc[i-1]["黄金ETF"] if i > 0 else row["黄金ETF"]
    real, gold_sig, fx_sig, in1, in2 = calculate_all(row, prev_etf)
    result.append({
        "日期": row["日期"],
        "美债": row["美债"],
        "美元": row["美元"],
        "VIX": row["VIX"],
        "黄金ETF": row["黄金ETF"],
        "实际利率": round(real, 3),
        "黄金趋势": gold_sig,
        "外汇趋势": fx_sig,
        "日内1": in1,
        "日内2": in2
    })

df_out = pd.DataFrame(result)
today = df_out.iloc[-1]

# ======================
# 主界面展示
# ======================
st.subheader("📈 今日核心指标")
c1, c2, c3, c4 = st.columns(4)
c1.metric("美债收益率", f"{today['美债']:.2f}%")
c2.metric("美元指数", f"{today['美元']:.2f}")
c3.metric("VIX", f"{today['VIX']:.2f}")
c4.metric("黄金ETF", f"{today['黄金ETF']:.2f}")

st.divider()

st.subheader("🧠 趋势信号")
cl, cr = st.columns(2)
cl.metric("黄金趋势", today["黄金趋势"])
cr.metric("外汇趋势", today["外汇趋势"])

st.divider()

st.subheader("⚡ 日内交易信号")
n1, n2 = st.columns(2)
n1.metric("日内信号1", today["日内1"])
n2.metric("日内信号2", today["日内2"])

st.divider()
st.subheader("📜 历史记录")
st.dataframe(df_out, use_container_width=True, hide_index=True)

