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

st.set_page_config(
    layout="wide", 
    page_title="RMM Trading Tools",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #ddd;
        background-color: #f8f9fa;
        color: #333;
        font-weight: 500;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
    }
    
    .stButton > button:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stNumberInput > div > div > input {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSlider > div > div > div {
        background-color: #f8f9fa;
    }
    
    .stCheckbox > div > label > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stRadio > div > label > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stExpander > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stTabs > div > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stDataFrame > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stProgress > div > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stMetric > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stAlert > div {
        border-radius: 8px;
    }
    
    .stSuccess > div {
        border-radius: 8px;
    }
    
    .stWarning > div {
        border-radius: 8px;
    }
    
    .stError > div {
        border-radius: 8px;
    }
    
    .stInfo > div {
        border-radius: 8px;
    }
    
    .stCaption {
        color: #666;
        font-size: 0.875rem;
    }
    
    .stMarkdown {
        color: #333;
    }
    
    .stHeader {
        color: #333;
        font-weight: 600;
    }
    
    .stSubheader {
        color: #333;
        font-weight: 600;
    }
    
    .stTitle {
        color: #333;
        font-weight: 700;
    }
    
    .stCode {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stJson {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stPlotlyChart {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stImage {
        border-radius: 8px;
    }
    
    .stVideo {
        border-radius: 8px;
    }
    
    .stAudio {
        border-radius: 8px;
    }
    
    .stFileUploader > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stDownloadButton > button {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar > div > div {
        background-color: #f8f9fa;
    }
    
    .stSidebar .stButton > button {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stNumberInput > div > div > input {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stTextInput > div > div > input {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stSlider > div > div > div {
        background-color: #f8f9fa;
    }
    
    .stSidebar .stCheckbox > div > label > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stRadio > div > label > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stExpander > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stTabs > div > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stDataFrame > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stProgress > div > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stMetric > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stSidebar .stAlert > div {
        border-radius: 8px;
    }
    
    .stSidebar .stSuccess > div {
        border-radius: 8px;
    }
    
    .stSidebar .stWarning > div {
        border-radius: 8px;
    }
    
    .stSidebar .stError > div {
        border-radius: 8px;
    }
    
    .stSidebar .stInfo > div {
        border-radius: 8px;
    }
    
    .stSidebar .stCaption {
        color: #666;
        font-size: 0.875rem;
    }
    
    .stSidebar .stMarkdown {
        color: #333;
    }
    
    .stSidebar .stHeader {
        color: #333;
        font-weight: 600;
    }
    
    .stSidebar .stSubheader {
        color: #333;
        font-weight: 600;
    }
    
    .stSidebar .stTitle {
        color: #333;
        font-weight: 700;
    }
    
    .stSidebar .stCode {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stSidebar .stJson {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stSidebar .stPlotlyChart {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stSidebar .stImage {
        border-radius: 8px;
    }
    
    .stSidebar .stVideo {
        border-radius: 8px;
    }
    
    .stSidebar .stAudio {
        border-radius: 8px;
    }
    
    .stSidebar .stFileUploader > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    .stSidebar .stDownloadButton > button {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🎯 RMM Trading Tools")
st.markdown("## Ваш персональный трейдинг-ассистент")

st.markdown("### 🧮 Калькуляторы")
if st.button("📊 Калькулятор входа", use_container_width=True):
    render_rmm_calculators()

st.markdown("### 🎲 Симулятор стратегий")
if st.button("🎯 Симулятор Монте-Карло", use_container_width=True):
    render_monte_carlo()

st.markdown("### 🧠 Цепи Маркова")
if st.button("📈 Анализ цепей Маркова", use_container_width=True):
    render_markov_analysis()

st.markdown("### 📊 Анализ паттернов")
if st.button("🔍 Детектор паттернов", use_container_width=True):
    render_pattern_analyzer()

st.markdown("### 🔍 Детектор сигналов")
if st.button("📡 Детектор сигналов", use_container_width=True):
    render_signal_detector()

st.markdown("### 🧭 Сводка по монете")
if st.button("📋 Сводка по монете", use_container_width=True):
    render_coin_summary()

st.markdown("### ✏️ Редактор")
if st.button("📝 Редактор страниц", use_container_width=True):
    render_editable_page("Редактор")

st.markdown("---")
st.markdown("### 📬 Обратная связь")
st.markdown("""
<div style='display: flex; align-items: center; gap: 1rem;'>
    <img src='https://avatars.githubusercontent.com/u/134078363?v=4' width='60' height='60' style='border-radius: 50%; border: 2px solid #ccc;' />
    <div>
        <p style='margin: 0; font-size: 16px;'>
            Разработчик: <b>@mommycodes</b>  
        </p>
        <p style='margin: 0; font-size: 14px;'>
            📬 Telegram: <a href='https://t.me/mommycodes' target='_blank'>связаться</a> |
            🐙 GitHub: <a href='https://github.com/mommycodes/rmm-simulator/issues' target='_blank'>создать issue</a>
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.caption("💡 Обратная связь помогает сделать симулятор лучше. Спасибо за тестирование!")