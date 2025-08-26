import streamlit as st
import time
from datetime import datetime, timedelta

def render_checklist_entry():
    st.markdown("## 🛡️ Вход в сделку")
    st.caption("⚡ Заполни чек-лист, подожди 10 минут и только потом входи в сделку - не спеши, ликвидация всегда приходит незаметно")
    st.image("https://i.postimg.cc/rsPGT5JB/2025-08-09-113211.png", use_column_width=True)

    # --- Инициализация состояния ---
    if "checklist" not in st.session_state:
        st.session_state.checklist = {
            "Пробитие наклонки": False,
            "Обязательно выход ОБЪЕМОВ": False,
            "Дивергенция на 1ч ТФ": False,
            "CCI в зоне ~200 или -200": False,
            "CCRSII в зоне ~20 или ~80": False,
            "Прошло 5 волн в 261,8%": False,
            "НЕ ЛОВИМ КИНЖАЛЫ": False,
        }
    if "all_done" not in st.session_state:
        st.session_state.all_done = False
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_started" not in st.session_state:
        st.session_state.timer_started = False

    # --- Чеклист ---
    if not st.session_state.all_done:
        st.markdown("### 📋 Чек-лист")
        for key in st.session_state.checklist.keys():
            checkbox = st.checkbox(
                f"✅ {key}" if st.session_state.checklist[key] else f"⚠️ {key}",
                value=st.session_state.checklist[key],
                key=key
            )
            st.session_state.checklist[key] = checkbox

        # Проверяем выполненность
        if all(st.session_state.checklist.values()):
            st.session_state.all_done = True
            st.success("🎯 Все условия выполнены!")
    
    # --- Кнопка запуска таймера ---
    if st.session_state.all_done and not st.session_state.timer_started:
        if st.button("🚀 Запустить таймер ⏳"):
            st.session_state.timer_end = datetime.now() + timedelta(minutes=1)
            st.session_state.timer_started = True

    # --- Таймер с обратным отсчетом ---
    if st.session_state.timer_started and st.session_state.timer_end:
        st.markdown("### ⏳ Таймер")
        timer_container = st.empty()
        progress_container = st.empty()

        remaining = st.session_state.timer_end - datetime.now()
        if remaining.total_seconds() > 0:
            for seconds_left in range(int(remaining.total_seconds()), -1, -1):
                mins, secs = divmod(seconds_left, 60)
                progress = 1 - seconds_left / (1 * 60)
                progress_container.progress(progress)
                timer_container.markdown(
                    f"""
                    <div style='
                        text-align:center; 
                        font-size:1.8rem; 
                        color:#2e7d32; 
                        font-weight:bold;
                        margin-top:0.5em;
                    '>
                        ⏳ Ожидаем <b>{mins:02d}:{secs:02d}</b> минут
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                time.sleep(1)

        # По окончании
        timer_container.empty()
        progress_container.empty()
        st.success("🚀 Все условия выполнены! Можно входить в сделку.")