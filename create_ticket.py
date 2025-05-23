import streamlit as st
import json
from datetime import datetime
from db import session
from models import TicketTemplate, CustomField, TicketInstance, TicketStep

def render_create_ticket(current_user):
    st.header("🎫 创建新工单")

    templates = session.query(TicketTemplate).all()
    if not templates:
        st.warning("⚠️ 没有任何工单模板。")
        return

    template_names = {t.name: t.id for t in templates}
    template_name = st.selectbox("选择模板", list(template_names.keys()))
    template_id = template_names[template_name]

    fields = session.query(CustomField).filter_by(template_id=template_id).all()
    field_data = {}

    for field in fields:
        fname = field.field_name
        ftype = field.field_type
        if ftype == "text":
            field_data[fname] = st.text_input(fname)
        elif ftype == "number":
            field_data[fname] = st.number_input(fname)
        elif ftype == "textarea":
            field_data[fname] = st.text_area(fname)
        elif ftype == "date":
            field_data[fname] = st.date_input(fname)
        elif ftype == "select":
            options = json.loads(field.options_json or "[]")
            field_data[fname] = st.selectbox(fname, options)
        elif ftype == "file":
            field_data[fname] = st.file_uploader(fname)

    if st.button("提交工单"):
        ticket = TicketInstance(
            template_id=template_id,
            title=f"{template_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            status="新建",
            created_by=current_user,
            created_at=datetime.now()
        )
        session.add(ticket)
        session.commit()

        step = TicketStep(
            ticket_id=ticket.id,
            node_id=None,
            assigned_to=current_user,
            submitted_at=datetime.now(),
            data=field_data,
            status="完成"
        )
        session.add(step)
        session.commit()

        st.success("✅ 工单提交成功，已写入数据库！")
        st.json(field_data)
