import streamlit as st
import re
from utils.storage import save_content_to_github as save_content
from utils.storage import load_content_from_github as load_content

try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    QUILL_AVAILABLE = False

def _init_content_state():
    if "blog_content" not in st.session_state:
        st.session_state.blog_content = load_content()
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = {}

def auto_embed_images(html: str) -> str:
    if not html:
        return html

    def replace_a(match):
        href = match.group(1)
        inner = match.group(2)
        if '<img' in inner.lower():
            return match.group(0)
        return f'<img src="{href}" style="max-width:100%;height:auto;" />'

    html = re.sub(
        r'<a[^>]+href="(https?://[^\s"]+\.(?:png|jpe?g|gif))"[^>]*>(.*?)</a>',
        replace_a,
        html,
        flags=re.IGNORECASE | re.DOTALL
    )

    def replace_url(match):
        url = match.group(0)
        if re.search(r'src=[\'"]{}[\'"]'.format(re.escape(url)), html):
            return url
        return f'<img src="{url}" style="max-width:100%;height:auto;" />'

    html = re.sub(
        r'https?://[^\s"<]+\.(?:png|jpe?g|gif)',
        replace_url,
        html,
        flags=re.IGNORECASE
    )

    return html

def render_editable_page(section_name: str):
    _init_content_state()

    if not QUILL_AVAILABLE:
        st.error("Ошибка, обратитесь к администратору")
        return

    if st.session_state.edit_mode.get(section_name, False):

        if "save_clicked" not in st.session_state:
            st.session_state.save_clicked = False

        if "cancel_clicked" not in st.session_state:
            st.session_state.cancel_clicked = False

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("💾", key=f"save_{section_name}"):
                st.session_state.save_clicked = True
        with col2:
            if st.button("❌", key=f"cancel_{section_name}"):
                st.session_state.cancel_clicked = True

        msg_container = st.empty()
        
        current_html = st.session_state.blog_content.get(section_name, "")
        html = st_quill(value=current_html, html=True, placeholder="Введите текст…", key=f"quill_{section_name}")

        if st.session_state.save_clicked:
            sanitized = auto_embed_images(html or "")
            st.session_state.blog_content[section_name] = sanitized
            save_content(st.session_state.blog_content)
            st.session_state.edit_mode[section_name] = False
            st.session_state.save_clicked = False
            msg_container.success("Сохранено ✅")

        if st.session_state.cancel_clicked:
            st.session_state.edit_mode[section_name] = False
            st.session_state.cancel_clicked = False
            msg_container.info("Редактирование отменено")

    else:
        if st.button("✏️ ", key=f"edit_{section_name}"):
            st.session_state.edit_mode[section_name] = True

        st.markdown(
            f"""
            <div style="font-size:16px; line-height:1.6; padding:0.5em;
                        border-left:4px solid #4CAF50; cursor:text;">
                {st.session_state.blog_content.get(section_name, "")}
            </div>
            """,
            unsafe_allow_html=True
        )