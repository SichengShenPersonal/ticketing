import streamlit as st
import json
from db import session
from models import TicketTemplate, TicketNodeTemplate
from auth import USER_DB

def render_template_designer(current_user):
    if USER_DB[current_user]["level"] != "admin":
        st.warning("❌ 权限不足，仅管理员可访问该页面")
        return

    st.header("🛠️ 工单模板设计器（最多支持 8 个流程节点）")
    template_name = st.text_input("模板名称")
    description = st.text_area("模板描述")
    allowed_groups = st.multiselect("谁可以发起这个工单？", ["ALL"] + list({g for u in USER_DB.values() for g in u['groups']}))

    node_data = []
    for i in range(8):
        with st.expander(f"🧩 配置节点 node{i}", expanded=(i == 0)):
            group = st.selectbox(f"Node{i} 接收群组", list({g for u in USER_DB.values() for g in u['groups']}), key=f"group_{i}")
            field_count = st.number_input(f"Node{i} 字段数量", 0, 10, 1, key=f"fcount_{i}")
            fields = []
            for j in range(int(field_count)):
                fname = st.text_input(f"字段{j+1} 名称", key=f"fname_{i}_{j}")
                ftype = st.selectbox(f"字段{j+1} 类型", ["text", "number", "select", "date", "file", "textarea"], key=f"ftype_{i}_{j}")
                is_required = st.checkbox(f"字段{j+1} 是否必填", value=True, key=f"freq_{i}_{j}")
                options = ""
                if ftype == "select":
                    options = st.text_input(f"字段{j+1} 可选项（逗号分隔）", key=f"fopt_{i}_{j}")
                fields.append({"field_name": fname, "field_type": ftype, "is_required": is_required, "options": options})
            node_data.append({"step": i, "group": group, "fields": fields})

    if st.button("保存模板"):
        t = TicketTemplate(name=template_name, description=description, allowed_groups=",".join(allowed_groups))
        session.add(t)
        session.commit()
        for node in node_data:
            nt = TicketNodeTemplate(
                template_id=t.id,
                step_order=node['step'],
                group=node['group'],
                fields_json=json.dumps(node['fields'])
            )
            session.add(nt)
        session.commit()
        st.success("✅ 模板保存成功！")
