import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def plot_simulations(data, initial_balance):
    st.markdown("#### 📈 100 симуляций капитала")
    st.caption("""
    Каждая линия — отдельная симуляция стратегии.  
    **Ось X** — номер сделки (временной шаг).  
    **Ось Y** — текущий баланс.  
    Показывает, как ведёт себя капитал по мере сделок. Нужен для визуальной оценки стабильности или волатильности.
    """)
    fig, ax = plt.subplots()
    for i in range(min(100, len(data))):
        ax.plot(data[i], alpha=0.5)
    ax.axhline(initial_balance, color='red', linestyle='--', label='Старт')
    ax.set_title("Траектории капитала (100 симуляций)")
    ax.legend()
    st.pyplot(fig)

def plot_best_worst(data, balances):
    st.markdown("#### 🟢 10 лучших | 🔻 10 худших")
    st.caption("""
    **Зелёные линии** — симуляции с наибольшим итогом.  
    **Красные линии** — симуляции с наименьшим итогом.  
    **Ось X** — шаг (номер сделки),  
    **Ось Y** — текущий капитал.  
    Этот график помогает сравнить крайние исходы и оценить уровень риска и награды.
    """)
    fig, ax = plt.subplots()
    best = balances.argsort()[-10:]
    worst = balances.argsort()[:10]
    for i in worst:
        ax.plot(data[i], color='red', alpha=0.6)
    for i in best:
        ax.plot(data[i], color='green', alpha=0.6)
    ax.set_title("Лучшие и худшие траектории капитала")
    st.pyplot(fig)

def plot_distribution(balances, initial_balance):
    st.markdown("#### 📊 Распределение финальных балансов")
    st.caption("""
    **Ось X** — итоговый капитал по завершении симуляции.  
    **Ось Y** — сколько симуляций дали такой результат.  
    Это гистограмма, показывающая частоту различных итогов. Позволяет понять, какие результаты были самыми типичными.
    """)
    fig, ax = plt.subplots()
    ax.hist(balances, bins=50, color='skyblue', edgecolor='black')
    ax.axvline(initial_balance, color='red', linestyle='--', label='Стартовый баланс')
    ax.set_title("Гистограмма итогов по симуляциям")
    ax.legend()
    st.pyplot(fig)

def plot_liquidation_distribution(liq_steps, num_trades):
    st.markdown("#### 💀 Распределение ликвидаций по сделкам")
    st.caption("""
    **Ось X** — номер сделки, на которой произошла ликвидация.  
    **Ось Y** — сколько симуляций были ликвидированы на этом шаге.  
    Это помогает понять, в какие моменты стратегия наиболее уязвима и когда чаще всего происходят обнуления.
    """)
    fig, ax = plt.subplots()
    ax.hist(liq_steps, bins=num_trades, edgecolor='black')
    ax.set_title("Шаги, на которых происходили ликвидации")
    st.pyplot(fig)

def plot_probability_heatmap(data, initial_balance):
    st.markdown("#### 🧠 Карта вероятностей (ниже стартового баланса)")
    st.caption("""
    **Ось X** — номер сделки (шаг симуляции).  
    **Ось Y** — доля симуляций, в которых баланс опустился ниже начального.  
    Этот график показывает, когда большинство траекторий входят в просадку. Полезен для оценки устойчивости на разных фазах стратегии.
    """)
    heat = [np.sum(data[:, j] < initial_balance) / len(data) for j in range(1, data.shape[1])]
    fig, ax = plt.subplots()
    ax.plot(range(1, len(heat)+1), heat)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Шаг сделки")
    ax.set_ylabel("Вероятность < стартового капитала")
    ax.set_title("Доля просевших симуляций на каждом шаге")
    st.pyplot(fig)
