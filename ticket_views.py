import streamlit as st
import pandas as pd
from db import session
from models import TicketInstance, TicketStep, TicketNodeTemplate
from auth import USER_DB
import json

def render_my_tickets(current_user):
    st.header("🧾 我提交的工单")
    tickets = session.query(TicketInstance).filter_by(created_by=current_user).all()
    if not tickets:
        st.info("你还没有提交任何工单")
        return

    data = []
    for t in tickets:
        data.append({
            "工单编号": f"TKT-{t.id:04d}",
            "标题": t.title,
            "状态": t.status,
            "提交人": t.created_by,
            "提交时间": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    st.dataframe(pd.DataFrame(data))

def render_group_tasks(current_user, show_all=False):
    st.header("👥 群组相关工单" if not show_all else "📂 所有工单总览")
    tickets = session.query(TicketInstance).all()
    visible = []

    for t in tickets:
        if show_all:
            visible.append(t)
            continue

        steps = session.query(TicketStep).filter_by(ticket_id=t.id).order_by(TicketStep.submitted_at.desc()).all()
        if steps:
            latest_step = steps[0]
            step_data = latest_step.data or {}
            dept = step_data.get("所属部门", None)
            if dept and dept in USER_DB[current_user]["groups"]:
                visible.append(t)

    if not visible:
        st.info("你所在群组没有可查看的工单" if not show_all else "暂无任何工单记录")
    else:
        data = []
        for t in visible:
            data.append({
                "工单编号": f"TKT-{t.id:04d}",
                "标题": t.title,
                "状态": t.status,
                "提交人": t.created_by,
                "提交时间": t.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        st.dataframe(pd.DataFrame(data))
