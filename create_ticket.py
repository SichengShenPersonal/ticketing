import streamlit as st
from db import session
from models import TicketTemplate, TicketNodeTemplate
from auth import USER_DB

def render_create_ticket(current_user):
    st.header("🎫 创建工单")

    # 1. 获取可用模板
    templates = session.query(TicketTemplate).all()
    template_dict = {t.name: t for t in templates}

    # 2. 模板选择（默认不选任何模板）
    selected_template_name = st.selectbox("请选择工单模板", [""] + list(template_dict.keys()))
    if not selected_template_name:
        st.info("请先选择模板，选择后可填写工单")
        return

    # 3. 只有选了模板才显示后续内容
    template = template_dict[selected_template_name]
    # 取第一个节点为发起节点
    node = (
        session.query(TicketNodeTemplate)
        .filter_by(template_id=template.id)
        .order_by(TicketNodeTemplate.step_order)
        .first()
    )
    if not node:
        st.error("模板未配置节点")
        return

    # 4. 加载字段
    fields = node.fields_json
    if isinstance(fields, str):
        import json
        fields = json.loads(fields)

    st.markdown("#### 请填写工单信息")

    # 5. 字段输入（每行最多3个字段）
    field_values = {}
    cols = [None, None, None]  # 缓存当前行的3列
    for idx, field in enumerate(fields):
        if idx % 3 == 0:
            cols = st.columns(3)
        col = cols[idx % 3]
        with col:
            field_name = field["field_name"]
            ftype = field.get("field_type", "text")
            required = field.get("is_required", False)
            default = field.get("default_value", "")
            options = field.get("options", "")

            label = f"{field_name}{' *' if required else ''}"
            key = f"ticket_field_{idx}"

            if ftype == "text":
                value = st.text_input(label, value=default, key=key)
            elif ftype == "number":
                value = st.number_input(label, value=float(default) if default else 0, key=key)
            elif ftype == "select":
                opts = [opt.strip() for opt in options.split(",") if opt.strip()]
                value = st.selectbox(label, opts, key=key)
            elif ftype == "date":
                value = st.date_input(label, key=key)
            elif ftype == "file":
                value = st.file_uploader(label, key=key)
            elif ftype == "textarea":
                value = st.text_area(label, value=default, key=key, height=100)
            else:
                value = st.text_input(label, value=default, key=key)

            field_values[field_name] = value

    # 6. 提交按钮和校验
    if st.button("提交工单"):
        # 检查必填
        missing = []
        for idx, field in enumerate(fields):
            if field.get("is_required", False):
                v = field_values[field["field_name"]]
                # 对于文件、文本等有不同判断
                if field["field_type"] == "file":
                    if v is None:
                        missing.append(field["field_name"])
                elif isinstance(v, str) and not v.strip():
                    missing.append(field["field_name"])
                elif v is None:
                    missing.append(field["field_name"])
        if missing:
            st.error(f"请填写所有必填字段：{', '.join(missing)}")
            return

        # 保存工单逻辑示例（你可根据实际业务逻辑调整）
        st.success("工单已成功提交！")
        # 可以在此处添加数据库保存等后续操作

# 如果你用 Streamlit 运行时这样调用
if __name__ == '__main__':
    # 这里你可以根据登录态等情况传递当前用户
    render_create_ticket(current_user="your_user_name")
