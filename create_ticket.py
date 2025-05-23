import streamlit as st
import json
from datetime import datetime
import pandas as pd
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
            default_value = field.get("default_value", "")

            value = None
            label = f"{fname}{' *' if is_required else ''}"

            if ftype == "text":
                value = st.text_input(label, value=default_value)
            elif ftype == "number":
                try:
                    value = st.number_input(label, value=float(default_value) if default_value else 0)
                except Exception:
                    value = st.number_input(label, value=0)
            elif ftype == "textarea":
                value = st.text_area(label, value=default_value)
            elif ftype == "date":
                try:
                    # 支持字符串或datetime
                    val = pd.to_datetime(default_value).date() if default_value else datetime.now().date()
                except Exception:
                    val = datetime.now().date()
                value = st.date_input(label, value=val)
            elif ftype == "select":
                option_list = [opt.strip() for opt in options.split(",") if opt.strip()] if options else []
                default_idx = option_list.index(default_value) if default_value in option_list else 0
                value = st.selectbox(label, option_list, index=default_idx) if option_list else ""
            elif ftype == "file":
                value = st.file_uploader(label)

            if is_required and (value is None or value == "" or (ftype == "file" and value is None)):
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
