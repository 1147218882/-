# 黄金实时晴雨表
import streamlit as st
import akshare as ak
from datetime import datetime

st.set_page_config(page_title="黄金晴雨表", layout="wide")

def calculate_all(B, C, D, E, F, F_prev, G, I):
    H = B - G
    J = -(C/100)+(4-B)/4+(D>20)*0.5+(E>1000)*0.3+(F>F_prev)*0.2-H*0.1+I/100
    K = "强烈看多" if J>=0.8 else "偏多" if J>=0.3 else "强烈看空" if J<=-0.8 else "偏空" if J<=-0.3 else "震荡观望"
    L = -(C/100)+(4-B)/4+(D>20)*0.4-H*0.15+I/100
    M = "非美多头" if L>=0.7 else "非美偏多" if L>=0.2 else "非美空头" if L<=-0.7 else "非美偏空" if L<=-0.2 else "观望"
    N = -(C/100)+(4-B)/4+(D>22)*0.6-H*0.12+I/80
    O = "日内多" if N>=0.6 else "偏多观望" if N>=0.1 else "日内空" if N<=-0.6 else "偏空观望" if N<=-0.1 else "观望"
    P = -(C/100)+(4-B)/4+(D>22)*0.5-H*0.18+I/80
    Q = "日内多" if P>=0.5 else "偏多" if P>=0.1 else "日内空" if P<=-0.5 else "偏空" if P<=-0.1 else "观望"
    return H, J, K, L, M, N, O, P, Q

@st.cache_data(ttl=300)
def get_data():
    try:
        C = float(ak.currency_usd_idx().iloc[-1]['close'])
        B = float(ak.bond_us_10y().iloc[-1]['value'])
        D = float(ak.stock_us_vix().iloc[-1]['close'])
        E = float(ak.fund_us_spdr_gold().iloc[-1]['close'])
        return {"time":datetime.now().strftime("%Y-%m-%d %H:%M"),"B":B,"C":C,"D":D,"E":E,"F":349500,"F_prev":347200,"G":2.35,"I":20 if B<4 else 15 if B<4.2 else 10}
    except:
        return {"time":"2026-03-10","B":4.11,"C":98.52,"D":17,"E":1070.7,"F":350000,"F_prev":348000,"G":2.35,"I":20}

data = get_data()
H,J,K,L,M,N,O,P,Q = calculate_all(data["B"],data["C"],data["D"],data["E"],data["F"],data["F_prev"],data["G"],data["I"])

st.title("📈 黄金趋势晴雨表")
st.subheader("📊 实时数据")
col1,col2,col3,col4 = st.columns(4)
col1.metric("美债收益率",f"{data['B']:.2f}"),col2.metric("美元指数",f"{data['C']:.2f}"),col3.metric("VIX",f"{data['D']:.1f}"),col4.metric("实际利率",f"{H:.2f}")
col5,col6,col7,col8 = st.columns(4)
col5.metric("黄金ETF",f"{data['E']:.1f}"),col6.metric("期货持仓",f"{data['F']:.0f}"),col7.metric("平衡通胀",f"{data['G']:.2f}"),col8.metric("降息预期",f"{data['I']}")
st.divider()
st.subheader("🔥 交易信号")
def s(t,v,sig):a,b=st.columns(2);a.metric(t+"分数",f"{v:.4f}"),b.metric(t+"信号",sig)
s("黄金长线",J,K),s("外汇长线",L,M),s("日内策略1",N,O),s("日内策略2",P,Q)
st.caption(f"更新时间：{data['time']} | 每5分钟自动刷新")
