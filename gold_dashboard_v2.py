import streamlit as st
import pandas as pd

# ======================
# 历史数据
# ======================
if "history" not in st.session_state:
    st.session_state.history = [
        {"日期":"2026/3/10","美债":4.11,"美元":98.52,"VIX":17,"黄金ETF":1070.7,"期货持仓":350000,"通胀":2.35,"降息预期":20},
        {"日期":"2026/3/11","美债":4.18,"美元":99.10,"VIX":24.40,"黄金ETF":1073.5,"期货持仓":228300,"通胀":2.33,"降息预期":10},
        {"日期":"2026/3/12","美债":4.22,"美元":99.40,"VIX":24.30,"黄金ETF":1077.3,"期货持仓":213100,"通胀":2.36,"降息预期":10},
        {"日期":"2026/3/13","美债":4.25,"美元":100.00,"VIX":24.26,"黄金ETF":1075.8,"期货持仓":209000,"通胀":2.38,"降息预期":10},
        {"日期":"2026/3/16","美债":4.23,"美元":99.96,"VIX":24.70,"黄金ETF":1071.6,"期货持仓":202100,"通胀":2.37,"降息预期":10},
    ]

# ======================
# 页面
# ======================
st.title("📊 黄金外汇打分系统（标准版）")
st.divider()

# ======================
# 输入区
# ======================
with st.sidebar:
    st.subheader("📝 今日数据")
    date = st.text_input("日期", "2026/3/17")
    bond = st.number_input("美债收益率", value=4.23, step=0.01)
    usd  = st.number_input("美元指数", value=99.96, step=0.01)
    vix  = st.number_input("VIX", value=24.70, step=0.01)
    gold = st.number_input("黄金ETF", value=1071.6, step=0.1)
    pos  = st.number_input("期货持仓", value=202100, step=1000)
    inf  = st.number_input("通胀", value=2.37, step=0.01)
    cut  = st.number_input("降息预期", value=10, step=5)

    if st.button("✅ 添加今日数据"):
        st.session_state.history.append({
            "日期":date,"美债":bond,"美元":usd,"VIX":vix,
            "黄金ETF":gold,"期货持仓":pos,"通胀":inf,"降息预期":cut
        })
        st.success("已保存")

# ======================
# 计算（完全按你的Excel公式）
# ======================
df = pd.DataFrame(st.session_state.history)
df["实际利率"] = df["美债"] - df["通胀"]

# 期货较前一日增加
df["期货增"] = [False] + (df["期货持仓"].iloc[1:] > df["期货持仓"].iloc[:-1]).tolist()

# 黄金长线 J2
df["黄金长线分"] = (
    -(df["美元"]/100)
    + (4-df["美债"])/4
    + (df["VIX"]>20)*0.5
    + (df["黄金ETF"]>1000)*0.3
    + df["期货增"]*0.2
    - df["实际利率"]*0.1
    + df["降息预期"]/100
)

# 外汇长线 L2
df["外汇长线分"] = (
    -(df["美元"]/100)
    + (4-df["美债"])/4
    + (df["VIX"]>20)*0.4
    - df["实际利率"]*0.15
    + df["降息预期"]/100
)

# 日内1 N2
df["日内1分"] = (
    -(df["美元"]/100)
    + (4-df["美债"])/4
    + (df["VIX"]>22)*0.6
    - df["实际利率"]*0.12
    + df["降息预期"]/80
)

# 日内2 P2
df["日内2分"] = (
    -(df["美元"]/100)
    + (4-df["美债"])/4
    + (df["VIX"]>22)*0.5
    - df["实际利率"]*0.18
    + df["降息预期"]/80
)

# ======================
# 信号判断
# ======================
def sig_gold(s):
    if s>=0.8: return "🔴 强烈看多"
    elif s>=0.3: return "🟡 偏多"
    elif s<=-0.8: return "🔵 强烈看空"
    elif s<=-0.3: return "🟢 偏空"
    else: return "⚪ 震荡观望"

def sig_fx(s):
    if s>=0.7: return "🔴 非美多头"
    elif s>=0.2: return "🟡 非美偏多"
    elif s<=-0.7: return "🔵 非美空头"
    elif s<=-0.2: return "🟢 非美偏空"
    else: return "⚪ 观望"

def sig_intra1(s):
    if s>=0.6: return "🔴 日内多"
    elif s>=0.1: return "🟡 偏多观望"
    elif s<=-0.6: return "🔵 日内空"
    elif s<=-0.1: return "🟢 偏空观望"
    else: return "⚪ 观望"

def sig_intra2(s):
    if s>=0.5: return "🔴 日内多"
    elif s>=0.1: return "🟡 偏多"
    elif s<=-0.5: return "🔵 日内空"
    elif s<=-0.1: return "🟢 偏空"
    else: return "⚪ 观望"

df["黄金信号"] = df["黄金长线分"].apply(sig_gold)
df["外汇信号"] = df["外汇长线分"].apply(sig_fx)
df["日内1信号"] = df["日内1分"].apply(sig_intra1)
df["日内2信号"] = df["日内2分"].apply(sig_intra2)

# ======================
# 今日信号卡片（红绿灯）
# ======================
today = df.iloc[-1]
st.subheader("🎯 今日交易信号（红绿灯版）")

c1,c2 = st.columns(2)
with c1:
    st.metric("黄金长线", today["黄金信号"], f"{today['黄金长线分']:.3f}")
with c2:
    st.metric("外汇长线", today["外汇信号"], f"{today['外汇长线分']:.3f}")

c3,c4 = st.columns(2)
with c3:
    st.metric("日内信号1", today["日内1信号"], f"{today['日内1分']:.3f}")
with c4:
    st.metric("日内信号2", today["日内2信号"], f"{today['日内2分']:.3f}")

st.divider()

# ======================
# 完整表格
# ======================
st.subheader("📜 历史打分表")
show_cols = [
    "日期","美债","美元","VIX","黄金ETF","实际利率",
    "黄金长线分","黄金信号","外汇长线分","外汇信号",
    "日内1分","日内1信号","日内2分","日内2信号"
]
st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
