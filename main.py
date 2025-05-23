import streamlit as st
import pandas as pd
import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TicketTemplate, CustomField, TicketInstance, TicketStep

# SQLite 连接
engine = create_engine("sqlite:///data/example.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

# ✅ 用户权限配置
USER_DB = {
    "admin_user": {"level": "admin", "groups": ["市场部", "技术部", "行政部"]},
    "agent_1":    {"level": "agent", "groups": ["技术部"]},
    "viewer_1":   {"level": "viewer", "groups": ["行政部"]}
}

st.set_page_config(page_title="FlowTick 工单系统", layout="wide")
st.title("📌 FlowTick 智能工单系统")

# 登录逻辑
with st.sidebar:
    st.subheader("🔐 登录")
    CURRENT_USER = st.selectbox("选择账号", list(USER_DB.keys()))
    st.write(f"权限等级: `{USER_DB[CURRENT_USER]['level']}`")
    st.write(f"所属群组: {', '.join(USER_DB[CURRENT_USER]['groups'])}")

# 展开式任务导航
with st.sidebar.expander("📂 导航菜单", expanded=True):
    menu = st.radio("功能选择", ["创建工单", "我的工单", "群组任务 - 所有", "群组任务 - 我的群组", "仪表盘"])

# ✅ 自动插入默认模板与字段
if session.query(TicketTemplate).count() == 0:
    template = TicketTemplate(name="新员工入职审批", description="标准入职流程")
    session.add(template)
    session.commit()

    fields = [
        {"field_name": "员工姓名", "field_type": "text"},
        {"field_name": "入职日期", "field_type": "date"},
        {"field_name": "所属部门", "field_type": "select", "options": ["市场部", "技术部", "行政部"]}
    ]

    for f in fields:
        field = CustomField(
            template_id=template.id,
            field_name=f["field_name"],
            field_type=f["field_type"],
            is_required=True,
            options_json=json.dumps(f.get("options", []))
        )
        session.add(field)
    session.commit()

if menu == "创建工单":
    st.header("🎫 创建新工单")

    templates = session.query(TicketTemplate).all()
    if not templates:
        st.warning("⚠️ 没有任何工单模板。")
    else:
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
                created_by=CURRENT_USER,
                created_at=datetime.now()
            )
            session.add(ticket)
            session.commit()

            step = TicketStep(
                ticket_id=ticket.id,
                node_id=None,
                assigned_to=CURRENT_USER,
                submitted_at=datetime.now(),
                data=field_data,
                status="完成"
            )
            session.add(step)
            session.commit()

            st.success("✅ 工单提交成功，已写入数据库！")
            st.json(field_data)

elif menu == "我的工单":
    st.header("🧾 我提交的工单")

    tickets = session.query(TicketInstance).filter_by(created_by=CURRENT_USER).all()
    if not tickets:
        st.info("你还没有提交任何工单")
    else:
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

elif menu == "群组任务 - 我的群组":
    st.header("👥 我的群组工单")

    tickets = session.query(TicketInstance).all()
    visible = []
    for t in tickets:
        steps = session.query(TicketStep).filter_by(ticket_id=t.id).order_by(TicketStep.submitted_at.desc()).all()
        if steps:
            latest_step = steps[0]
            step_data = latest_step.data or {}
            dept = step_data.get("所属部门", None)
            if dept and dept in USER_DB[CURRENT_USER]["groups"]:
                visible.append(t)

    if not visible:
        st.info("你所在群组没有可查看的工单")
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

elif menu == "群组任务 - 所有":
    st.header("📂 所有工单总览")

    tickets = session.query(TicketInstance).all()
    if not tickets:
        st.info("暂无任何工单记录")
    else:
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

elif menu == "仪表盘":
    st.header("📊 工单统计分析（模拟）")
    st.metric("平均处理时长", "3.2 天")
    st.bar_chart(pd.DataFrame({
        "市场部": [10, 8], "技术部": [7, 12]
    }, index=["未结", "已结"]))
