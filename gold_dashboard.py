import streamlit as st
import pandas as pd

# --- 页面配置 ---
st.set_page_config(page_title="黄金外汇日内趋势表", page_icon="📊", layout="wide")
st.title("📊 黄金外汇日内趋势表")
st.divider()

# ======================
# 你的真实表格数据
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
    B, C, D, E, F, G, I = row["B"], row["C"], row["D"], row["E"], row["F"], row["G"], row["I"]
    H = B - G # 实际利率
    
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
    J_txt = "强烈看多" if J>=0.8 else "偏多" if J>=0.3 else "强烈看空" if J<=-0.8 else "偏空" if J<=-0.3 else "震荡观望"
    L_txt = "非美多头" if L>=0.7 else "非美偏多" if L>=0.2 else "非美空头" if L<=-0.7 else "非美偏空" if L<=-0.2 else "观望"
    N_txt = "日内多" if N>=0.6 else "偏多观望" if N>=0.1 else "日内空" if N<=-0.6 else "偏空观望" if N<=-0.1 else "观望"
    P_txt = "日内多" if P>=0.5 else "偏多" if P>=0.1 else "日内空" if P<=-0.5 else "偏空" if P<=-0.1 else "观望"
    
    rows.append({"date":row["date"], "B":B,"C":C,"D":D,"E":E,"F":F,"G":G,"H":H,"I":I,"J":J,"J_txt":J_txt,"L":L,"L_txt":L_txt,"N":N,"N_txt":N_txt,"P":P,"P_txt":P_txt})

res = pd.DataFrame(rows)
latest = res.iloc[-1]

# ======================
# 页面展示
# ======================
st.subheader("最新核心指标 (3/13)")
c1,c2,c3,c4 = st.columns(4)
c1.metric("美债收益率", f"{latest['B']:.2f}")
c2.metric("美元指数", f"{latest['C']:.2f}")
c3.metric("VIX", f"{latest['D']:.2f}")
c4.metric("黄金ETF", f"{latest['E']:.1f}")

c5,c6,c7 = st.columns(3)
c5.metric("期货持仓", f"{latest['F']:.0f}")
c6.metric("亏平衡通胀", f"{latest['G']:.2f}")
c7.metric("实际利率", f"{latest['H']:.2f}")

st.divider()
st.subheader("完整信号体系")
cl, cr = st.columns(2)
cl.metric("黄金长线信号", f"{latest['J']:.4f}", help=latest['J_txt'])
cl.caption(f"判定：**{latest['J_txt']}**")
cr.metric("外汇长线信号", f"{latest['L']:.4f}", help=latest['L_txt'])
cr.caption(f"判定：**{latest['L_txt']}**")

st.divider()
st.subheader("⚡ 日内短线交易信号 (重点)")
n1, n2 = st.columns(2)
n1.metric("日内信号1", f"{latest['N']:.4f}", help=latest['N_txt'])
n1.caption(f"操作建议：**{latest['N_txt']}**")
n2.metric("日内信号2", f"{latest['P']:.4f}", help=latest['P_txt'])
n2.caption(f"操作建议：**{latest['P_txt']}**")

st.divider()
st.subheader("📜 历史数据回溯")
st.dataframe(res[["date", "B", "C", "D", "H", "J_txt", "L_txt", "N_txt", "P_txt"]], use_container_width=True, hide_index=True)
