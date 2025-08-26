import streamlit as st
import re
from utils.storage import save_content, load_content

try:
    from streamlit_quill import st_quill
    QUILL_AVAILABLE = True
except Exception:
    QUILL_AVAILABLE = False


# -----------------------------
# Вспомогательные функции
# -----------------------------
def _init_content_state():
    """Инициализация хранилища текстов по разделам."""
    if "blog_content" not in st.session_state:
        st.session_state.blog_content = load_content()
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = {}  # dict: section_name -> bool


def auto_embed_images(html: str) -> str:
    """Авто-вклейка картинок по ссылке."""
    if not html:
        return html
    html = re.sub(
        r'<a[^>]+href="(https?://[^\s"]+\.(?:png|jpe?g|gif))"[^>]*>.*?</a>',
        r'<img src="\1" style="max-width:100%;height:auto;" />',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'(?P<url>https?://[^\s"<]+?\.(?:png|jpe?g|gif))',
        r'<img src="\g<url>" style="max-width:100%;height:auto;" />',
        html,
        flags=re.IGNORECASE,
    )
    return html


def render_editable_page(section_name: str):
    """Редактируемая страница"""
    _init_content_state()

    if not QUILL_AVAILABLE:
        st.error("Ошибка, обратитесь к администратору")
        return

    # --- Режим редактирования ---
    if st.session_state.edit_mode.get(section_name, False):
        col1, col2 = st.columns([1, 1])
        with col1:
            save_clicked = st.button("💾", type="primary", key=f"save_{section_name}")
        with col2:
            cancel_clicked = st.button("❌", key=f"cancel_{section_name}")

        # Редактор Quill
        current_html = st.session_state.blog_content.get(section_name, "")
        html = st_quill(
            value=current_html,
            html=True,
            placeholder="Введите текст…",
            key=f"quill_{section_name}",
        )

        if save_clicked:
            sanitized = auto_embed_images(html or "")
            st.session_state.blog_content[section_name] = sanitized
            save_content(st.session_state.blog_content)
            st.session_state.edit_mode[section_name] = False
            st.success("Сохранено ✅")

        if cancel_clicked:
            st.session_state.edit_mode[section_name] = False
            st.info("Редактирование отменено")

    else:
        # --- Режим просмотра ---
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