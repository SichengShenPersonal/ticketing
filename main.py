import streamlit as st
from auth import USER_DB
from template_designer import render_template_designer
# from create_ticket import render_create_ticket
# from ticket_views import render_my_tickets, render_group_tasks

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

# 路由到具体功能
if menu == "设计工单模板":
    render_template_designer(CURRENT_USER)
elif menu == "创建工单":
    pass  # render_create_ticket(CURRENT_USER)
elif menu == "我的工单":
    pass  # render_my_tickets(CURRENT_USER)
elif menu.startswith("群组任务"):
    pass  # render_group_tasks(CURRENT_USER)
elif menu == "仪表盘":
    st.write("📊 工单统计页面开发中...")
