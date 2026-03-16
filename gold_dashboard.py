import streamlit as st
import pandas as pd
from datetime import datetime

# ======================
# 页面设置
# ======================
st.set_page_config(page_title="黄金外汇日内趋势系统", layout="wide")
st.title("📊 黄金外汇日内趋势系统（1:1 复刻 Excel 公式）")
st.divider()

# ======================
# 初始化历史数据（用你截图里的真实数据）
# ======================
if "history" not in st.session_state:
    st.session_state.history = [
        {"日期":"2026/3/10","美债":4.13,"美元":98.62,"VIX":24.00,"黄金ETF":1073.5,"期货持仓":309000,"盈亏平衡":2.32,"通胀":1.81,"降息预期":10},
        {"日期":"2026/3/11","美债":4.18,"美元":99.10,"VIX":24.40,"黄金ETF":1073.5,"期货持仓":228300,"盈亏平衡":2.33,"通胀":1.85,"降息预期":10},
        {"日期":"2026/3/12","美债":4.22,"美元":99.40,"VIX":24.30,"黄金ETF":1077.3,"期货持仓":213100,"盈亏平衡":2.36,"通胀":1.86,"降息预期":10},
        {"日期":"2026/3/13","美债":4.25,"美元":100.00,"VIX":24.26,"黄金ETF":1075.8,"期货持仓":209000,"盈亏平衡":2.38,"通胀":1.87,"降息预期":10},
        {"日期":"2026/3/16","美债":4.23,"美元":99.96,"VIX":24.70,"黄金ETF":1071.6,"期货持仓":202100,"盈亏平衡":2.36,"通胀":1.87,"降息预期":10},
    ]

today_str = datetime.now().strftime("%Y/%m/%d")

# ======================
# 侧边栏：今日数据录入（和你表格字段完全一致）
# ======================
with st.sidebar:
    st.subheader("📝 输入今日数据")
    input_date = st.text_input("日期", today_str)
    bond = st.number_input("美债收益率", value=4.23, step=0.01)
    usd = st.number_input("美元指数", value=99.96, step=0.01)
    vix = st.number_input("VIX", value=24.70, step=0.01)
    gold_etf = st.number_input("黄金ETF", value=1071.6, step=0.1)
    futures_pos = st.number_input("期货持仓", value=202100, step=1000)
    pnl_balance = st.number_input("盈亏平衡", value=2.36, step=0.01)
    inflation = st.number_input("通胀", value=1.87, step=0.01)
    rate_cut = st.number_input("降息预期分", value=10, step=5)

    if st.button("✅ 添加到历史表"):
        dates = [row["日期"] for row in st.session_state.history]
        if input_date not in dates:
            st.session_state.history.append({
                "日期": input_date,
                "美债": bond,
                "美元": usd,
                "VIX": vix,
                "黄金ETF": gold_etf,
                "期货持仓": futures_pos,
                "盈亏平衡": pnl_balance,
                "通胀": inflation,
                "降息预期": rate_cut
            })
            st.success("添加成功！")
        else:
            st.warning("今日数据已存在")

# ======================
# 核心：100% 复刻你 Excel 的所有公式
# ======================
def calc_all_signals(df):
    df = df.copy()
    # 1. 实际利率 = 美债 - 通胀（H列）
    df["实际利率"] = df["美债"] - df["通胀"]
    
    # 2. 黄金长线分（J列）
    df["黄金长线分"] = (
        -(df["美元"]/100)
        + (4 - df["美债"])/4
        + (df["VIX"] > 20).astype(int)*0.5
        + (df["黄金ETF"] > 1000).astype(int)*0.3
        + (df["期货持仓"] > df["期货持仓"].shift(1)).astype(int)*0.2
        - df["实际利率"]*0.1
        + df["降息预期"]/100
    )
    # 黄金长线信号（K列）
    def gold_signal(score):
        if score >= 0.8:
            return "强烈看多"
        elif score >= 0.3:
            return "偏多"
        elif score <= -0.8:
            return "强烈看空"
        elif score <= -0.3:
            return "偏空"
        else:
            return "震荡观望"
    df["黄金长线信号"] = df["黄金长线分"].apply(gold_signal)
    
    # 3. 外汇长线分（L列）
    df["外汇长线分"] = (
        -(df["美元"]/100)
        + (4 - df["美债"])/4
        + (df["VIX"] > 20).astype(int)*0.4
        - df["实际利率"]*0.15
        + df["降息预期"]/100
    )
    # 外汇长线信号（M列）
    def fx_signal(score):
        if score >= 0.7:
            return "非美多头"
        elif score >= 0.2:
            return "非美偏多"
        elif score <= -0.7:
            return "非美空头"
        elif score <= -0.2:
            return "非美偏空"
        else:
            return "观望"
    df["外汇长线信号"] = df["外汇长线分"].apply(fx_signal)
    
    # 4. 日内信号1分（N列）
    df["日内信号1分"] = (
        -(df["美元"]/100)
        + (4 - df["美债"])/4
        + (df["VIX"] > 22).astype(int)*0.6
        - df["实际利率"]*0.12
        + df["降息预期"]/80
    )
    # 日内信号1（O列）
    def intra1_signal(score):
        if score >= 0.6:
            return "日内多"
        elif score >= 0.1:
            return "偏多观望"
        elif score <= -0.6:
            return "日内空"
        elif score <= -0.1:
            return "偏空观望"
        else:
            return "观望"
    df["日内信号1"] = df["日内信号1分"].apply(intra1_signal)
    
    # 5. 日内信号2分（P列）
    df["日内信号2分"] = (
        -(df["美元"]/100)
        + (4 - df["美债"])/4
        + (df["VIX"] > 22).astype(int)*0.5
        - df["实际利率"]*0.18
        + df["降息预期"]/80
    )
    # 日内信号2（Q列）
    def intra2_signal(score):
        if score >= 0.5:
            return "日内多"
        elif score >= 0.1:
            return "偏多"
        elif score <= -0.5:
            return "日内空"
        elif score <= -0.1:
            return "偏空"
        else:
            return "观望"
    df["日内信号2"] = df["日内信号2分"].apply(intra2_signal)
    return df

# ======================
# 计算所有历史数据
# ======================
df = pd.DataFrame(st.session_state.history)
df = calc_all_signals(df)

# ======================
# 主界面展示（和你表格结构完全一致）
# ======================
st.subheader("📜 历史趋势表（和你 Excel 完全一致）")
st.dataframe(
    df[["日期","美债","美元","VIX","黄金ETF","期货持仓","盈亏平衡","通胀","实际利率","降息预期",
        "黄金长线分","黄金长线信号","外汇长线分","外汇长线信号",
        "日内信号1分","日内信号1","日内信号2分","日内信号2"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# 今日结论展示
today_data = df.iloc[-1]
st.subheader("🎯 今日交易信号汇总")
col1, col2 = st.columns(2)
col1.metric("黄金长线分", f"{today_data['黄金长线分']:.4f}", today_data['黄金长线信号'])
col2.metric("外汇长线分", f"{today_data['外汇长线分']:.4f}", today_data['外汇长线信号'])

col3, col4 = st.columns(2)
col3.metric("日内信号1分", f"{today_data['日内信号1分']:.4f}", today_data['日内信号1'])
col4.metric("日内信号2分", f"{today_data['日内信号2分']:.4f}", today_data['日内信号2'])
