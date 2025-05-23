import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="FlowTick 工单系统", layout="wide")
st.title("📌 FlowTick 智能工单系统（原型）")

menu = st.sidebar.radio("导航", ["创建工单", "我的工单", "仪表盘"])

if menu == "创建工单":
    st.header("🎫 创建新工单")
    template = st.selectbox("选择模板", ["新员工入职", "设备申请", "报销审批"])
    title = st.text_input("工单标题")
    desc = st.text_area("工单描述")
    assigned_to = st.text_input("分配给")
    if st.button("提交"):
        st.success("✅ 工单已创建（模拟）")

elif menu == "我的工单":
    st.header("🧾 我的提交记录")
    st.dataframe(pd.DataFrame({
        "工单编号": ["TKT-001", "TKT-002"],
        "标题": ["张三入职审批", "MacBook 报修"],
        "状态": ["进行中", "已完成"],
        "更新时间": ["2025-05-21", "2025-05-20"]
    }))

elif menu == "仪表盘":
    st.header("📊 工单统计分析")
    st.metric("平均处理时长", "3.2 天")
    st.bar_chart(pd.DataFrame({
        "市场部": [10, 8], "技术部": [7, 12]
    }, index=["未结", "已结"]))