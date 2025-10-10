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

def get_app_key():
    key = os.getenv("APP_KEY")
    if key:
        return key
    try:
        return st.secrets["APP_KEY"]
    except Exception:
        return None

APP_KEY = get_app_key()

if not st.session_state.authenticated:
    # Мобильные стили
    st.markdown("""
    <style>
      .auth-card {max-width: 420px; margin: 8vh auto 0; padding: 16px;}
      @media (max-width: 480px) {
        .auth-card {margin-top: 6vh; padding: 12px;}
      }
    </style>
    """, unsafe_allow_html=True)

    if APP_KEY is None:
        st.error("APP_KEY не найден. Установите его в .env или .streamlit/secrets.toml")
        st.stop()

    with st.container():
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("### 🔑 Вход")
        with st.form("auth_form", clear_on_submit=False):
            pwd = st.text_input(
                "Код доступа",
                type="password",
                placeholder="Введите код",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Войти", use_container_width=True)
        if submitted:
            if pwd == APP_KEY:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Неверный код доступа ❌")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------
# Константы навигации
# -----------------------------
PAGES = [
    ("🚀 Главная", "home"),
    ("🛡️ ВХОД в сделку", "checklist"),
    ("🌊 Волновой анализ", "waves"),
    ("📊 Технический анализ", "ta"),
    ("📈 Индикаторы", "indicators"),
    ("🎯 Стратегии", "strategies"),
    ("🖼️ Библиотека скринов", "screens"),
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
    if key == "ta":
        # Подразделы Тех. анализа
        with st.sidebar.expander("📊 Технический анализ", expanded=(st.session_state.page.startswith("ta"))):
            if st.button("📘 Общие понятия", key="nav_ta_general", use_container_width=True):
                st.session_state.page = "ta_general"
            if st.button("🕯 Свечной анализ", key="nav_ta_candles", use_container_width=True):
                st.session_state.page = "ta_candles"
            if st.button("📈 Тренды и линии тренда", key="nav_ta_trends", use_container_width=True):
                st.session_state.page = "ta_trends"
            if st.button("💥 Пробои", key="nav_ta_breakouts", use_container_width=True):
                st.session_state.page = "ta_breakouts"
            if st.button("📏 Складной метр", key="nav_ta_ruler", use_container_width=True):
                st.session_state.page = "ta_ruler"
            if st.button("🔷 Фигуры тех. анализа", key="nav_ta_patterns", use_container_width=True):
                st.session_state.page = "ta_patterns"
    elif key == "waves":
        # Подразделы Волн. анализа
        with st.sidebar.expander("🌊 Волновой анализ", expanded=(st.session_state.page.startswith("waves"))):
            if st.button("📈 Импульс", key="nav_waves_impulse", use_container_width=True):
                st.session_state.page = "waves_impulse"
            if st.button("🔄 Коррекция", key="nav_waves_correction", use_container_width=True):
                st.session_state.page = "waves_correction"
            if st.button("📜 Общие правила", key="nav_waves_rules", use_container_width=True):
                st.session_state.page = "waves_rules"
            if st.button("🔢 Фибоначчи", key="nav_waves_fibo", use_container_width=True):
                st.session_state.page = "waves_fibo"
            if st.button("📐 Клины", key="nav_waves_wedges", use_container_width=True):
                st.session_state.page = "waves_wedges"
            if st.button("🎯 Сетапы", key="nav_waves_setups", use_container_width=True):
                st.session_state.page = "waves_setups"
    elif key == "screens":
        # Подразделы Библиотеки скринов
        with st.sidebar.expander("🖼️ Библиотека скринов", expanded=(st.session_state.page.startswith("screens"))):
            screen_subpages = [
                ("📊 Пятиволновки", "screens_5waves"),
                ("1️⃣–2️⃣ Волны", "screens_1_2"),
                ("3️⃣ Волна", "screens_3"),
                ("📐 Клины", "screens_wedges"),
                ("🔄 Коррекции", "screens_corrections"),
                ("🔷 Фигуры тех. анализа", "screens_patterns"),
                ("📈 Индикаторы", "screens_indicators"),
                ("📜 Правила", "screens_rules"),
                ("🔗 Зависимости", "screens_dependencies")
            ]
            for name, key_sub in screen_subpages:
                if st.button(name, key=f"nav_{key_sub}", use_container_width=True):
                    st.session_state.page = key_sub
    else:
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key


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

# === Определяем текущую страницу ===
current = st.session_state.page

if current == "home":
    render_home()
# --- Тех. анализ ---
elif current == "ta_general":
    render_editable_page("Технический анализ — Общие понятия")
elif current == "ta_candles":
    render_editable_page("Технический анализ — Свечной анализ")
elif current == "ta_trends":
    render_editable_page("Технический анализ — Тренды и линии тренда")
elif current == "ta_breakouts":
    render_editable_page("Технический анализ — Пробои")
elif current == "ta_ruler":
    render_editable_page("Технический анализ — Складной метр")
elif current == "ta_patterns":
    render_editable_page("Технический анализ — Фигуры тех. анализа")

# --- Индикаторы ---
elif current == "indicators":
    render_editable_page("Индикаторы")

# --- Волновой анализ ---
elif current == "waves_impulse":
    render_editable_page("Волновой анализ — Импульс")
elif current == "waves_correction":
    render_editable_page("Волновой анализ — Коррекция")
elif current == "waves_rules":
    render_editable_page("Волновой анализ — Общие правила")
elif current == "waves_fibo":
    render_editable_page("Волновой анализ — Фибоначчи")
elif current == "waves_wedges":
    render_editable_page("Волновой анализ — Клины")
elif current == "waves_setups":
    render_editable_page("Волновой анализ — Сетапы")

# --- Стратегии ---
elif current == "strategies":
    render_editable_page("Стратегии")

# --- Библиотека скринов ---
elif current.startswith("screens"):
    render_editable_page(f"Библиотека скринов — {current.split('_')[1].capitalize()}")

# --- Калькуляторы ---
elif current == "calculators":
    render_rmm_calculators()

# --- Симулятор ---
elif current == "simulator":
    render_monte_carlo()

# --- Чеклист ---
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
