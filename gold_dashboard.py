import streamlit as st

# 页面配置
st.set_page_config(page_title="黄金外汇日内趋势表", page_icon="📊")

# 标题（和你的表格名保持一致）
st.title("📊 黄金外汇日内趋势表")
st.subheader("实时数据")

# --- 核心指标（和表格最新一行完全对应）---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("美债收益率", "4.25")
with col2:
    st.metric("美元指数", "100.00")
with col3:
    st.metric("VIX", "24.26")
with col4:
    st.metric("实际利率", "1.87")

col5, col6, col7 = st.columns(3)
with col5:
    st.metric("黄金ETF", "1075.8")
with col6:
    st.metric("期货持仓", "209000")
with col7:
    st.metric("亏平衡通胀", "2.38")

# --- 信号与预期 ---
st.subheader("信号与预期")
col8, col9, col10 = st.columns(3)
with col8:
    st.metric("降息预期分值", "10")
with col9:
    st.metric("黄金长线信号", "-0.3495")
with col10:
    st.metric("外汇长线信号", "-0.843")
