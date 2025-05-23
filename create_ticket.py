import streamlit as st
import json
from datetime import datetime
from db import session
from models import TicketTemplate, TicketNodeTemplate, TicketInstance, TicketStep
from auth import USER_DB

def render_create_ticket(current_user):
    st.header("🎫 创建新工单")

    # 获取用户所属群组
    user_groups = set(USER_DB[current_user]['groups'])

    # 只显示当前用户有权限发起的模板
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

            if ftype == "text":
                field_data[fname] = st.text_input(fname, value="")
            elif ftype == "number":
                field_data[fname] = st.number_input(fname, value=0)
            elif ftype == "textarea":
                field_data[fname] = st.text_area(fname, value="")
            elif ftype == "date":
                field_data[fname] = st.date_input(fname)
            elif ftype == "select":
                option_list = [opt.strip() for opt in options.split(",") if opt.strip()] if options else []
                if not option_list:
                    field_data[fname] = st.text_input(fname + "（请填写选项）", value="")
                else:
                    field_data[fname] = st.selectbox(fname, option_list)
            elif ftype == "file":
                field_data[fname] = st.file_uploader(fname)
            else:
                field_data[fname] = st.text_input(fname + "（未知类型）", value="")
    else:
        st.warning("该模板还没有字段，请先在模板设计器中添加字段。")
        return

    if st.button("提交工单"):
        # 保存工单实例
        ticket = TicketInstance(
            template_id=template_id,
            title=f"{template_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            status="新建",
            created_by=current_user,
            created_at=datetime.now()
        )
        session.add(ticket)
        session.commit()

        # 保存步骤（只保存第一个节点的填写数据）
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
