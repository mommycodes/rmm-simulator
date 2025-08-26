# app.py
import streamlit as st
import os

from modules.calculators import render_rmm_calculators
from modules.montecarlo import render_monte_carlo
from modules.editor import render_editable_page
from dotenv import load_dotenv
from checklist import render_checklist_entry

load_dotenv()

# -----------------------------
# Общая конфигурация страницы
# -----------------------------
st.set_page_config(layout="wide", page_title="MOMMY CODES")


# === Проверка ключа при входе ===
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "key_input" not in st.session_state:
    st.session_state.key_input = ""
if "error_msg" not in st.session_state:
    st.session_state.error_msg = ""

APP_KEY = os.getenv("APP_KEY") or st.secrets.get("APP_KEY")

if not st.session_state.authenticated:
    st.title("🔑 Авторизация")
    st.markdown(f"<h2 style='text-align:center;'>{'*'*len(st.session_state.key_input)}</h2>", unsafe_allow_html=True)

    rows = [
        [1,2,3],
        [4,5,6],
        [7,8,9],
        ["⌫",0,"✅"]
    ]

    for row in rows:
        cols = st.columns(3)
        for i, val in enumerate(row):
            if cols[i].button(str(val)):
                if val == "⌫":
                    st.session_state.key_input = st.session_state.key_input[:-1]
                elif val == "✅":
                    if st.session_state.key_input == APP_KEY:
                        st.session_state.authenticated = True
                        st.session_state.error_msg = ""
                    else:
                        st.session_state.error_msg = "Неверный ключ ❌"
                        st.session_state.key_input = ""
                else:
                    st.session_state.key_input += str(val)

    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)

    st.stop()

# -----------------------------
# Константы навигации
# -----------------------------
PAGES = [
    ("🚀 Главная", "home"),
    ("🛡️ ВХОД в сделку", "checklist"),
    ("📊 Технический анализ", "ta"),
    ("🕯 Свечной анализ", "candles"),
    ("📈 Индикаторы", "indicators"),
    ("🌊 Волновой анализ", "waves"),
    ("🎯 Стратегии", "strategies"),
    ("🧮 Калькуляторы", "calculators"),
    ("🎲 Симулятор стратегий", "simulator"),
]

if "page" not in st.session_state:
    st.session_state.page = "home"

# -----------------------------
# Сайдбар: Кнопки разделов
# -----------------------------
st.sidebar.markdown("### 📚 Разделы")

for label, key in PAGES:
    if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
        st.session_state.page = key

current = st.session_state.page

# -----------------------------
# Рендер страниц
# -----------------------------
# app.py
def render_home():
    st.markdown("## 📘 Алгоритм манименеджмента")
    st.info("✨ Рекомендованный базовый свод правил")

    rules = [
        ("❌", "**Стоп-торги** после 3 убыточных сделок — останавливаем торговлю на день, чтобы не сгореть"),
        ("⚖️", "**RR минимум 3:1** — каждая прибыль минимум в 3 раза больше убытка"),
        ("📋", "**Торговый план на день** — оформляем по чек-листу"),
        ("📓", "**Ведение дневника сделок** и статистики"),
        ("💵", "**Один и тот же риск в $** на сделку (2%)"),
        ("📉", "**Не превышать объём** — рисковать только малой частью депозита"),
        ("🧯", "**Перерыв 2–3 недели** при просадке > 20% за месяц"),
        ("✅", "**Закрытие дня** при прибыли 2–5%")
    ]

    for emoji, text in rules:
        st.markdown(
            f"{emoji} {text}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 🎯 Минимально жизнеспособная стратегия")
    st.markdown(
        "<ul>"
        "<li>📈 <b>RR ≥ 3:1</b></li>"
        "<li>🎯 <b>Winrate ≥ 35%</b></li>"
        "</ul>",
        unsafe_allow_html=True
    )
    st.markdown(
        "🧠 Даже при <b>65% убыточных сделках</b> можно выжить, если соблюдать соотношение риска и прибыли!",
        unsafe_allow_html=True
    )

if current == "home":
    render_home()
elif current == "ta":
    render_editable_page("Технический анализ")
elif current == "candles":
    render_editable_page("Свечной анализ")
elif current == "indicators":
    render_editable_page("Индикаторы")
elif current == "waves":
    render_editable_page("Волновой анализ")
elif current == "strategies":
    render_editable_page("Стратегии")
elif current == "calculators":
    render_rmm_calculators()
elif current == "simulator":
    render_monte_carlo()
elif current == "checklist":
    render_checklist_entry()


# === Контакты
st.markdown("---")
st.markdown("### 📬 Обратная связь")
st.markdown("""
<div style='display: flex; align-items: center; gap: 1rem;'>
    <img src='https://avatars.githubusercontent.com/u/134078363?v=4' width='60' height='60' style='border-radius: 50%; border: 2px solid #ccc;' />
    <div>
        <p style='margin: 0; font-size: 16px;'>
            Разработчик: <b>@mommycodes39</b>  
        </p>
        <p style='margin: 0; font-size: 14px;'>
            📬 Telegram: <a href='https://t.me/mommycodes39' target='_blank'>связаться</a> |
            🐙 GitHub: <a href='https://github.com/mommycodes/rmm-simulator/issues' target='_blank'>создать issue</a>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("💡 Обратная связь помогает сделать симулятор лучше. Спасибо за тестирование!")
