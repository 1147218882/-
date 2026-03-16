import streamlit as st
import pandas as pd

# ======================
# 初始化历史数据（你表格里的真实数据）
# ======================
if "history" not in st.session_state:
    st.session_state.history = [
        {"日期":"2026/3/10","美债":4.13,"美元":98.62,"VIX":24.00,"黄金ETF":1073.5,"期货持仓":309000,"通胀":1.81,"降息预期":10},
        {"日期":"2026/3/11","美债":4.18,"美元":99.10,"VIX":24.40,"黄金ETF":1073.5,"期货持仓":228300,"通胀":1.85,"降息预期":10},
        {"日期":"2026/3/12","美债":4.22,"美元":99.40,"VIX":24.30,"黄金ETF":1077.3,"期货持仓":213100,"通胀":1.86,"降息预期":10},
        {"日期":"2026/3/13","美债":4.25,"美元":100.00,"VIX":24.26,"黄金ETF":1075.8,"期货持仓":209000,"通胀":1.87,"降息预期":10},
        {"日期":"2026/3/16","美债":4.23,"美元":99.96,"VIX":24.70,"黄金ETF":1071.6,"期货持仓":202100,"通胀":1.87,"降息预期":10},
    ]

# ======================
# 页面标题
# ======================
st.title("📊 黄金外汇趋势系统（完整功能版）")
st.divider()

# ======================
# 侧边栏：今日数据录入
# ======================
with st.sidebar:
    st.subheader("📝 输入今日数据")
    date = st.text_input("日期", "2026/3/17")
    bond = st.number_input("美债收益率", value=4.23, step=0.01)
    usd = st.number_input("美元指数", value=99.96, step=0.01)
    vix = st.number_input("VIX", value=24.70, step=0.01)
    gold_etf = st.number_input("黄金ETF", value=1071.6, step=0.1)
    futures_pos = st.number_input("期货持仓", value=202100, step=1000)
    inflation = st.number_input("通胀", value=1.87, step=0.01)
    rate_cut = st.number_input("降息预期", value=10, step=5)

    if st.button("✅ 添加到历史"):
        st.session_state.history.append({
            "日期": date,
            "美债": bond,
            "美元": usd,
            "VIX": vix,
            "黄金ETF": gold_etf,
            "期货持仓": futures_pos,
            "通胀": inflation,
            "降息预期": rate_cut
        })
        st.success("添加成功！")

# ======================
# 核心计算（100% 复刻你 Excel 公式）
# ======================
df = pd.DataFrame(st.session_state.history)
df["实际利率"] = df["美债"] - df["通胀"]

# 期货持仓较前一日上涨（第一行设为False）
df["期货涨"] = [False] + (df["期货持仓"].iloc[1:] > df["期货持仓"].iloc[:-1]).tolist()

# 1. 黄金长线（J/K 列）
df["黄金长线分"] = (
    -(df["美元"]/100)
    + (4 - df["美债"])/4
    + (df["VIX"] > 20).astype(int)*0.5
    + (df["黄金ETF"] > 1000).astype(int)*0.3
    + df["期货涨"].astype(int)*0.2
    - df["实际利率"]*0.1
    + df["降息预期"]/100
)
def gold_sig(s):
    if s >= 0.8: return "强烈看多"
    elif s >= 0.3: return "偏多"
    elif s <= -0.8: return "强烈看空"
    elif s <= -0.3: return "偏空"
    else: return "震荡观望"
df["黄金信号"] = df["黄金长线分"].apply(gold_sig)

# 2. 外汇长线（L/M 列）
df["外汇长线分"] = (
    -(df["美元"]/100)
    + (4 - df["美债"])/4
    + (df["VIX"] > 20).astype(int)*0.4
    - df["实际利率"]*0.15
    + df["降息预期"]/100
)
def fx_sig(s):
    if s >= 0.7: return "非美多头"
    elif s >= 0.2: return "非美偏多"
    elif s <= -0.7: return "非美空头"
    elif s <= -0.2: return "非美偏空"
    else: return "观望"
df["外汇信号"] = df["外汇长线分"].apply(fx_sig)

# 3. 日内信号1（N/O 列）
df["日内1分"] = (
    -(df["美元"]/100)
    + (4 - df["美债"])/4
    + (df["VIX"] > 22).astype(int)*0.6
    - df["实际利率"]*0.12
    + df["降息预期"]/80
)
def intra1_sig(s):
    if s >= 0.6: return "日内多"
    elif s >= 0.1: return "偏多观望"
    elif s <= -0.6: return "日内空"
    elif s <= -0.1: return "偏空观望"
    else: return "观望"
df["日内1信号"] = df["日内1分"].apply(intra1_sig)

# 4. 日内信号2（P/Q 列）
df["日内2分"] = (
    -(df["美元"]/100)
    + (4 - df["美债"])/4
    + (df["VIX"] > 22).astype(int)*0.5
    - df["实际利率"]*0.18
    + df["降息预期"]/80
)
def intra2_sig(s):
    if s >= 0.5: return "日内多"
    elif s >= 0.1: return "偏多"
    elif s <= -0.5: return "日内空"
    elif s <= -0.1: return "偏空"
    else: return "观望"
df["日内2信号"] = df["日内2分"].apply(intra2_sig)

# ======================
# 展示表格
# ======================
st.subheader("📜 历史趋势表（和你 Excel 完全一致）")
st.dataframe(
    df[["日期","美债","美元","VIX","黄金ETF","期货持仓","通胀","实际利率",
        "黄金长线分","黄金信号","外汇长线分","外汇信号","日内1分","日内1信号","日内2分","日内2信号"]],
    use_container_width=True,
    hide_index=True
)

# 今日结论
today = df.iloc[-1]
st.subheader("🎯 今日交易信号汇总")
col1, col2 = st.columns(2)
col1.metric("黄金长线分", f"{today['黄金长线分']:.4f}", today['黄金信号'])
col2.metric("外汇长线分", f"{today['外汇长线分']:.4f}", today['外汇信号'])

col3, col4 = st.columns(2)
col3.metric("日内1分", f"{today['日内1分']:.4f}", today['日内1信号'])
col4.metric("日内2分", f"{today['日内2分']:.4f}", today['日内2信号'])
