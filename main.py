import streamlit as st
import pandas as pd
import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TicketTemplate, CustomField  # ✅ 只从 models 导入

# SQLite 数据库初始化
engine = create_engine("sqlite:///data/example.db")
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

# --- 自动插入默认模板（如果是首次启动） ---
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

# --- Streamlit UI ---
st.set_page_config(page_title="FlowTick 工单系统", layout="wide")
st.title("📌 FlowTick 智能工单系统")

menu = st.sidebar.radio("导航", ["创建工单", "我的工单", "仪表盘"])

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
            st.success("✅ 工单已提交（当前为模拟提交）")
            st.json(field_data)

elif menu == "我的工单":
    st.header("🧾 我的提交记录（模拟）")
    st.dataframe(pd.DataFrame({
        "工单编号": ["TKT-001", "TKT-002"],
        "标题": ["张三入职审批", "MacBook 报修"],
        "状态": ["进行中", "已完成"],
        "更新时间": ["2025-05-21", "2025-05-20"]
    }))

elif menu == "仪表盘":
    st.header("📊 工单统计分析（模拟）")
    st.metric("平均处理时长", "3.2 天")
    st.bar_chart(pd.DataFrame({
        "市场部": [10, 8], "技术部": [7, 12]
    }, index=["未结", "已结"]))
