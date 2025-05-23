import streamlit as st
import json
from datetime import datetime
from db import session
from models import TicketTemplate, TicketNodeTemplate, TicketInstance, TicketStep
from auth import USER_DB

def render_create_ticket(current_user):
    st.header("🎫 创建新工单")

    user_groups = set(USER_DB[current_user]['groups'])
    templates = [
        t for t in session.query(TicketTemplate).all()
        if not t.allowed_groups or user_groups.intersection(set(t.allowed_groups.split(',')))
    ]

    if not templates:
        st.warning("⚠️ 没有可用的工单模板。")
        return

    template_names = {t.name: t.id for t in templates}
    template_name = st.selectbox("选择模板", list(template_names.keys()))
    template_id = template_names[template_name]

    # 读取第一个节点（node0）的字段
    node_template = session.query(TicketNodeTemplate).filter_by(template_id=template_id, step_order=0).first()
    field_data = {}
    error_flag = False

    if node_template:
        try:
            fields = json.loads(node_template.fields_json)
        except Exception as e:
            st.error(f"模板字段解析出错: {e}")
            fields = []

        for field in fields:
            fname = field.get("field_name", "")
            ftype = field.get("field_type", "")
            is_required = field.get("is_required", False)
            options = field.get("options", "")

            value = None
            if ftype == "text":
                value = st.text_input(fname)
            elif ftype == "number":
                value = st.number_input(fname)
            elif ftype == "textarea":
                value = st.text_area(fname)
            elif ftype == "date":
                value = st.date_input(fname)
            elif ftype == "select":
                option_list = [opt.strip() for opt in options.split(",") if opt.strip()] if options else []
                value = st.selectbox(fname, option_list) if option_list else ""
            elif ftype == "file":
                value = st.file_uploader(fname)

            # 校验必填
            if is_required and (value is None or value == "" or (ftype == "file" and value is None)):
                st.error(f"{fname} 是必填项！")
                error_flag = True

            field_data[fname] = value
    else:
        st.warning("该模板还没有字段，请先在模板设计器中添加字段。")
        return

    if st.button("提交工单"):
        if error_flag:
            st.error("请补全所有必填项后再提交！")
            return

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
            node_id=node_template.id if node_template else None,
            assigned_to=current_user,
            submitted_at=datetime.now(),
            data=field_data,
            status="完成"
        )
        session.add(step)
        session.commit()

        st.success("✅ 工单提交成功，已写入数据库！")
        st.json(field_data)
