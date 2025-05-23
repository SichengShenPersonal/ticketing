import streamlit as st
import json
from db import session
from models import TicketTemplate, TicketNodeTemplate
from auth import USER_DB

def render_template_designer(current_user):
    if USER_DB[current_user]["level"] != "admin":
        st.warning("❌ 权限不足，仅管理员可访问该页面")
        return

    st.header("🛠️ 工单模板设计器（支持动态节点与字段）")

    template_name = st.text_input("模板名称")
    description = st.text_area("模板描述")
    allowed_groups = st.multiselect(
        "谁可以发起这个工单？",
        ["ALL"] + list({g for u in USER_DB.values() for g in u['groups']})
    )

    # 动态节点列表
    if "node_data_list" not in st.session_state:
        st.session_state.node_data_list = []

    # 添加节点按钮
    if st.button("➕ 新增节点"):
        st.session_state.node_data_list.append({"group": "", "fields": []})

    # 展示所有节点
    for i, node in enumerate(st.session_state.node_data_list):
        with st.expander(f"节点 {i+1}", expanded=True):
            node["group"] = st.selectbox(
                f"节点{i+1} 接收群组",
                list({g for u in USER_DB.values() for g in u['groups']}),
                key=f"group_{i}"
            )

            # 动态添加字段
            if f"fields_{i}" not in st.session_state:
                st.session_state[f"fields_{i}"] = []

            if st.button(f"➕ 节点{i+1}新增字段", key=f"add_field_{i}"):
                st.session_state[f"fields_{i}"].append({})

            # 展示所有字段（用columns并列布局）
            for j, _ in enumerate(st.session_state[f"fields_{i}"]):
                cols = st.columns([2, 1, 1, 2, 2])  # 名称/必填 | 类型 | 默认值 | 选项 | 删除按钮
                with cols[0]:
                    fname = st.text_input(f"字段{j+1} 名称", key=f"fname_{i}_{j}")
                with cols[1]:
                    is_required = st.checkbox("必填", value=True, key=f"freq_{i}_{j}")
                with cols[2]:
                    ftype = st.selectbox(
                        "类型",
                        ["text", "number", "select", "date", "file", "textarea"],
                        key=f"ftype_{i}_{j}"
                    )
                with cols[3]:
                    default_value = st.text_input("默认值", key=f"fdefault_{i}_{j}")
                with cols[4]:
                    options = ""
                    if ftype == "select":
                        options = st.text_input("可选项(逗号分隔)", key=f"fopt_{i}_{j}")

                # 保存字段数据
                st.session_state[f"fields_{i}"][j] = {
                    "field_name": fname,
                    "field_type": ftype,
                    "is_required": is_required,
                    "default_value": default_value,
                    "options": options if ftype == "select" else ""
                }

                # 删除字段按钮
                if st.button("删除字段", key=f"del_field_{i}_{j}"):
                    st.session_state[f"fields_{i}"].pop(j)
                    st.experimental_rerun()

            node["fields"] = st.session_state[f"fields_{i}"]

        # 删除节点按钮
        if st.button(f"❌ 删除节点{i+1}", key=f"del_node_{i}"):
            st.session_state.node_data_list.pop(i)
            st.session_state.pop(f"fields_{i}", None)
            st.experimental_rerun()

    # 保存模板
    if st.button("保存模板"):
        t = TicketTemplate(
            name=template_name,
            description=description,
            allowed_groups=",".join(allowed_groups)
        )
        session.add(t)
        session.commit()
        for idx, node in enumerate(st.session_state.node_data_list):
            nt = TicketNodeTemplate(
                template_id=t.id,
                step_order=idx,
                group=node['group'],
                fields_json=json.dumps(node['fields'])
            )
            session.add(nt)
        session.commit()
        st.success("✅ 模板保存成功！")
        # 清空session状态以便下次重新设计
        st.session_state.node_data_list = []
        for k in list(st.session_state.keys()):
            if k.startswith("fields_"):
                st.session_state.pop(k)
