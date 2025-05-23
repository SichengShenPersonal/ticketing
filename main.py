import streamlit as st
import pandas as pd
from auth import USER_DB
from template_designer import render_template_designer
from create_ticket import render_create_ticket
from ticket_views import render_my_tickets, render_group_tasks

st.set_page_config(page_title="FlowTick 工单系统", layout="wide")
st.title("📌 FlowTick 智能工单系统")

with st.sidebar:
    st.subheader("🔐 登录")
    CURRENT_USER = st.selectbox("选择账号", list(USER_DB.keys()))
    st.write(f"权限等级: `{USER_DB[CURRENT_USER]['level']}`")
    st.write(f"所属群组: {', '.join(USER_DB[CURRENT_USER]['groups'])}")

with st.sidebar.expander("📂 导航菜单", expanded=True):
    menu = st.radio("功能选择", [
        "设计工单模板", 
        "创建工单", 
        "我的工单", 
        "群组任务 - 我的群组", 
        "群组任务 - 所有", 
        "仪表盘"
    ])

if menu == "设计工单模板":
    render_template_designer(CURRENT_USER)
elif menu == "创建工单":
    render_create_ticket(CURRENT_USER)
elif menu == "我的工单":
    render_my_tickets(CURRENT_USER)
elif menu == "群组任务 - 我的群组":
    render_group_tasks(CURRENT_USER, show_all=False)
elif menu == "群组任务 - 所有":
    render_group_tasks(CURRENT_USER, show_all=True)
elif menu == "仪表盘":
    st.header("📊 工单统计分析（模拟）")
    st.metric("平均处理时长", "3.2 天")
    st.bar_chart(pd.DataFrame({
        "市场部": [10, 8], "技术部": [7, 12]
    }, index=["未结", "已结"]))
