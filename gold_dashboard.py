import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="黄金外汇日内趋势表", page_icon="📊", layout="wide")
st.title("📊 黄金外汇日内趋势表")
st.divider()

# ======================
# 你的真实表格 4 天数据
# ======================
df = pd.DataFrame([
    {"日期":"2026/3/10", "B":4.11, "C":98.52, "D":17, "E":1070.7, "F":309000, "G":2.35, "I":20},
    {"日期":"2026/3/11", "B":4.18, "C":99.10, "D":24.4, "E":1073.5, "F":228300, "G":2.33, "I":10},
    {"日期":"2026/3/12", "B":4.22, "C":99.40, "D":24.3, "E":1077.3, "F":213100, "G":2.36, "I":10},
    {"日期":"2026/3/13", "B":4.25, "C":100.00,"D":24.26,"E":1075.8, "F":209000, "G":2.38, "I":10},
])

# ======================
# 核心计算函数
# ======================
def calc_all(row, F_prev):
    B = row["B"]
    C = row["C"]
    D = row["D"]
    E = row["E"]
    F = row["F"]
    G = row["G"]
    I = row["I"]
    H = B - G  # 实际利率
    
    # 黄金长线信号 (J)
    J = -(C/100) + (4-B)/4 + (0.5 if D>20 else 0) + (0.3 if E>1000 else 0) + (0.2 if F>F_prev else 0) - H*0.1 + I/100
    # 外汇长线信号 (L)
    L = -(C/100) + (4-B)/4 + (0.4 if D>20 else 0) - H*0.15 + I/100
    # 日内短线信号1 (N)
    N = -(C/100) + (4-B)/4 + (0.6 if D>22 else 0) - H*0.12 + I/80
    # 日内短线信号2 (P)
    P = -(C/100) + (4-B)/4 + (0.5 if D>22 else 0) - H*0.18 + I/80
    
    return H, J, L, N, P

# 遍历计算
rows = []
F_prev = None
for _, row in df.iterrows():
    H, J, L, N, P = calc_all(row, F_prev)
    F_prev = row["F"]
    
    # 信号文字判定
    if J >= 0.8:
        J_txt = "强烈看多"
    elif J >= 0.3:
        J_txt = "偏多"
    elif J <= -0.8:
        J_txt = "强烈看空"
    elif J <= -0.3:
        J_txt = "偏空"
    else:
        J_txt = "震荡观望"

    if L >= 0.7:
        L_txt = "非美多头"
    elif L >= 0.2:
        L_txt = "非美偏多"
    elif L <= -0.7:
        L_txt = "非美空头"
    elif L <= -0.2:
        L_txt = "非美偏空"
    else:
        L_txt = "观望"

    if N >= 0.6:
        N_txt = "日内多"
    elif N >= 0.1:
        N_txt = "偏多观望"
    elif N <= -0.6:
        N_txt = "日内空"
    elif N <= -0.1:
        N_txt = "偏空观望"
    else:
        N_txt = "观望"

    if P >= 0.5:
        P_txt = "日内多"
    elif P >= 0.1:
        P_txt = "偏多"
    elif P <= -0.5:
        P_txt = "日内空"
    elif P <= -0.1:
        P_txt = "偏空"
    else:
        P_txt = "观望"
    
    rows.append({
        "日期": row["日期"],
        "美债收益率": B,
        "美元指数": C,
        "VIX": D,
        "黄金ETF": E,
        "期货持仓": F,
        "亏平衡通胀": G,
        "实际利率": H,
        "降息预期": I,
        "黄金长线": J,
        "黄金信号": J_txt,
        "外汇长线": L,
        "外汇信号": L_txt,
        "日内1": N,
        "日内信号1": N_txt,
        "日内2": P,
        "日内信号2": P_txt
    })

res = pd.DataFrame(rows)
latest = res.iloc[-1]

# ======================
# 页面展示
# ======================
st.subheader("最新核心指标 (2026/3/13)")
c1,c2,c3,c4 = st.columns(4)
c1.metric("美债收益率", f"{latest['美债收益率']:.2f}")
c2.metric("美元指数", f"{latest['美元指数']:.2f}")
c3.metric("VIX", f"{latest['VIX']:.2f}")
c4.metric("黄金ETF", f"{latest['黄金ETF']:.1f}")

c5,c6,c7 = st.columns(3)
c5.metric("期货持仓", f"{latest['期货持仓']:.0f}")
c6.metric("亏平衡通胀", f"{latest['亏平衡通胀']:.2f}")
c7.metric("实际利率", f"{latest['实际利率']:.2f}")

st.divider()
st.subheader("长线信号")
cl, cr = st.columns(2)
cl.metric("黄金长线信号", f"{latest['黄金长线']:.4f}", help=latest['黄金信号'])
cl.caption(f"判定：**{latest['黄金信号']}**")
cr.metric("外汇长线信号", f"{latest['外汇长线']:.4f}", help=latest['外汇信号'])
cr.caption(f"判定：**{latest['外汇信号']}**")

st.divider()
st.subheader("⚡ 日内短线交易信号")
n1, n2 = st.columns(2)
n1.metric("日内信号1", f"{latest['日内1']:.4f}", help=latest['日内信号1'])
n1.caption(f"操作建议：**{latest['日内信号1']}**")
n2.metric("日内信号2", f"{latest['日内2']:.4f}", help=latest['日内信号2'])
n2.caption(f"操作建议：**{latest['日内信号2']}**")

st.divider()
st.subheader("📜 历史数据回溯 (3/10 - 3/13)")
show = res[["日期", "美债收益率", "美元指数", "VIX", "实际利率", "黄金信号", "外汇信号", "日内信号1", "日内信号2"]]
st.dataframe(show, use_container_width=True, hide_index=True)

