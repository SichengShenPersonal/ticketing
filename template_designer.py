import streamlit as st
import json
from db import session
from models import TicketTemplate, TicketNodeTemplate
from auth import USER_DB

def render_template_designer(current_user):
    if USER_DB[current_user]["level"] != "admin":
        st.warning("❌ 权限不足，仅管理员可访问该页面")
        return

    st.header("🛠️ 工单模板设计器（动态节点、字段、字段默认值、节点可重命名）")

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
        node_count = len(st.session_state.node_data_list) + 1
        st.session_state.node_data_list.append({
            "name": f"节点{node_count}",
            "group": "",
            "fields": []
        })

    # 展示所有节点
    remove_node_indexes = []
    for i, node in enumerate(st.session_state.node_data_list):
        # 并排显示节点名称和删除按钮
        node_col1, node_col2 = st.columns([8, 1])
        with node_col1:
            node['name'] = st.text_input(
                "节点名称",
                value=node.get('name', f"节点{i+1}"),
                key=f"node_name_{i}"
            )
        with node_col2:
            if st.button("❌", key=f"del_node_{i}"):
                remove_node_indexes.append(i)
        with st.expander(node['name'], expanded=True):
            node["group"] = st.selectbox(
                f"节点接收群组",
                list({g for u in USER_DB.values() for g in u['groups']}),
                key=f"group_{i}"
            )

            # 字段列表初始化
            if f"fields_{i}" not in st.session_state:
                st.session_state[f"fields_{i}"] = []

            # 新增字段按钮
            if st.button(f"➕ 新增字段", key=f"add_field_{i}"):
                st.session_state[f"fields_{i}"].append({})

            # 字段并列排布，支持默认值
            remove_field_indexes = []
            for j, _ in enumerate(st.session_state[f"fields_{i}"]):
                # 第一行：字段名称 + 必填 + 删除按钮
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    fname = st.text_input(f"字段{j+1} 名称", key=f"fname_{i}_{j}")
                with col2:
                    is_required = st.checkbox("必填", value=True, key=f"freq_{i}_{j}")
                with col3:
                    if st.button("删除字段", key=f"del_field_{i}_{j}"):
                        remove_field_indexes.append(j)

                # 第二行：字段类型 + 默认值 + 可选项（仅select类型显示）
                col4, col5, col6 = st.columns([2, 2, 3])
                with col4:
                    ftype = st.selectbox(
                        "类型",
                        ["text", "number", "select", "date", "file", "textarea"],
                        key=f"ftype_{i}_{j}"
                    )
                with col5:
                    default_value = st.text_input("默认值", key=f"fdefault_{i}_{j}")
                with col6:
                    options = ""
                    if ftype == "select":
                        options = st.text_input("可选项(用逗号分隔)", key=f"fopt_{i}_{j}")

                # 保存字段
                st.session_state[f"fields_{i}"][j] = {
                    "field_name": fname,
                    "field_type": ftype,
                    "is_required": is_required,
                    "default_value": default_value,
                    "options": options if ftype == "select" else ""
                }

            # 删除多余字段（防止索引错乱，倒序删）
            for idx in sorted(remove_field_indexes, reverse=True):
                st.session_state[f"fields_{i}"].pop(idx)

            node["fields"] = st.session_state[f"fields_{i}"]

    # 删除多余节点（倒序删除防止索引错乱）
    for idx in sorted(remove_node_indexes, reverse=True):
        st.session_state.node_data_list.pop(idx)
        st.session_state.pop(f"fields_{idx}", None)
        st.experimental_rerun()

    # 保存模板
    if st.button("保存模板"):
        if not template_name or not allowed_groups or not st.session_state.node_data_list:
            st.error("模板名、群组和至少一个节点不能为空")
            return

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
                fields_json=json.dumps(node['fields']),
                node_name=node['name']
            )
            session.add(nt)
        session.commit()
        st.success("✅ 模板保存成功！")
        # 清空session状态以便下次重新设计
        st.session_state.node_data_list = []
        for k in list(st.session_state.keys()):
            if k.startswith("fields_"):
                st.session_state.pop(k)
