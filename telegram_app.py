import streamlit as st
import os
from modules.calculators import render_rmm_calculators
from modules.montecarlo import render_monte_carlo
from modules.editor import render_editable_page
from modules.markov_interface import render_markov_analysis
from modules.pattern_analyzer import render_pattern_analyzer
from modules.signal_detector import render_signal_detector
from modules.coin_summary import render_coin_summary
from dotenv import load_dotenv

load_dotenv()

# Конфигурация для Telegram Web App
st.set_page_config(
    layout="wide", 
    page_title="RMM Trading Tools",
    initial_sidebar_state="collapsed"  # Скрываем сайдбар для мобильных устройств
)

# Стили для мобильных устройств
st.markdown("""
<style>
    /* Стили для Telegram Web App */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Адаптивные кнопки */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-size: 16px;
        padding: 0.5rem 1rem;
    }
    
    /* Адаптивные метрики */
    .metric-container {
        margin-bottom: 1rem;
    }
    
    /* Скрываем элементы Streamlit для Telegram */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Стили для мобильных устройств */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem;
        }
        
        .stNumberInput > div > div > input {
            font-size: 16px; /* Предотвращает зум на iOS */
        }
    }
</style>
""", unsafe_allow_html=True)

# Получаем параметры из URL для определения страницы
query_params = st.query_params
page = query_params.get('page', ['calculators'])[0]

# Проверяем, запущено ли приложение в Telegram
def is_telegram_webapp():
    """Проверяем, запущено ли приложение в Telegram Web App"""
    user_agent = st.get_option("server.headless")
    return user_agent or "telegram" in str(st.get_option("server.headless"))

# Упрощенная навигация для Telegram
if page == "calculators":
    st.markdown("## 🧮 Калькуляторы RMM")
    render_rmm_calculators()
    
elif page == "ta":
    st.markdown("## 📊 Технический анализ")
    render_editable_page("Технический анализ — Общие понятия")
    
elif page == "waves":
    st.markdown("## 🌊 Волновой анализ")
    render_editable_page("Волновой анализ")
    
elif page == "simulator":
    st.markdown("## 🎲 Симулятор стратегий")
    render_monte_carlo()
    
elif page == "markov":
    st.markdown("## 🧠 Цепи Маркова")
    render_markov_analysis()
    
elif page == "coin_summary":
    st.markdown("## 🧭 Сводка по монете")
    render_coin_summary()
    
else:
    # По умолчанию показываем калькуляторы
    st.markdown("## 🧮 Калькуляторы RMM")
    render_rmm_calculators()

# Добавляем кнопку "Назад" для навигации в Telegram
if is_telegram_webapp():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Главная", key="nav_home"):
            st.query_params.page = "calculators"
            st.rerun()
    
    with col2:
        if st.button("📊 Анализ", key="nav_analysis"):
            st.query_params.page = "ta"
            st.rerun()
    
    with col3:
        if st.button("🎲 Симулятор", key="nav_simulator"):
            st.query_params.page = "simulator"
            st.rerun()
