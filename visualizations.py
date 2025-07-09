import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def plot_simulations(data, initial_balance):
    n = min(100, len(data))
    st.markdown(f"#### 📈 {n} симуляций капитала")
    st.caption("""
    Каждая линия — отдельная симуляция стратегии.  
    **Ось X** — номер сделки (временной шаг).  
    **Ось Y** — текущий баланс.  
    Показывает, как ведёт себя капитал по мере сделок. Нужен для визуальной оценки стабильности или волатильности.  
    🔴 **Красная линия** — стартовый капитал (уровень начального баланса).  
    🔵 **Синяя линия** — медиана итоговых балансов по всем симуляциям.
    """)

    st.info("""
    👉 **Как читать:**  
    Если большинство линий быстро падает вниз — стратегия **рискованная**.  
    Если большинство растёт или остаётся выше старта — стратегия **устойчива**.
    """)

    num_lines = st.number_input("📊 Сколько симуляций отобразить (до 100)", min_value=1, max_value=min(100, len(data)), value=min(100, len(data)), step=1)

    median_balance = np.median(data[:, -1])

    fig = go.Figure()

    for i in range(num_lines):
        fig.add_trace(go.Scatter(
            y=data[i],
            mode='lines',
            line=dict(width=1),
            name=None,
            opacity=0.4,
            hoverinfo='skip',
            showlegend=False
        ))

    # Стартовая линия
    fig.add_trace(go.Scatter(
        x=[0, len(data[0]) - 1],
        y=[initial_balance, initial_balance],
        mode="lines",
        line=dict(color="red", dash="dash"),
        name="Старт"
    ))
    # Медиана
    fig.add_trace(go.Scatter(
        x=[0, len(data[0]) - 1],
        y=[median_balance, median_balance],
        mode="lines",
        line=dict(color="blue", dash="dot"),
        name="Медиана"
    ))

    fig.update_layout(
        title="Траектории капитала",
        xaxis_title="Номер сделки",
        yaxis_title="Баланс",
        height=500,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_best_worst(data, balances):
    n = len(balances)
    half = min(10, n // 2)
    st.markdown(f"#### 🟢 {half} лучших | 🔻 {half} худших")

    st.caption("""
    **Зелёные линии** — симуляции с наибольшим итогом.  
    **Красные линии** — симуляции с наименьшим итогом.  
    **Ось X** — шаг (номер сделки),  
    **Ось Y** — текущий капитал.
    """)

    st.info("""
    👉 **Как использовать:**  
    Сравни лучшие и худшие случаи.  
    Если даже худшие не обнуляют баланс — стратегия надёжная.  
    Если худшие падают в 0 — задумайся о рисках.
    """)

    spread = np.max(balances) - np.min(balances)
    st.caption(f"📊 Разброс между лучшей и худшей симуляцией: **{spread:,.2f}$**")

    fig = go.Figure()

    best = balances.argsort()[-half:]
    worst = balances.argsort()[:half]

    for idx, i in enumerate(reversed(worst), 1):
        fig.add_trace(go.Scatter(
            y=data[i],
            mode='lines',
            name=f"❌ #{idx} худший — {balances[i]:,.2f}",
            line=dict(color='red'),
            opacity=0.6
        ))
        fig.add_trace(go.Scatter(
                x=[0],
                y=[data[i][0]],
                mode="markers",
                marker=dict(color="black", size=6),
                showlegend=False,
                hovertext=f"Старт: {data[i][0]:.2f}",
                hoverinfo="text"
            ))
        fig.add_trace(go.Scatter(
                x=[len(data[i]) - 1],
                y=[data[i][-1]],
                mode="markers",
                marker=dict(color="gold", size=6),
                showlegend=False,
                hovertext=f"Финиш: {data[i][-1]:.2f}",
                hoverinfo="text"
            ))
    for idx, i in enumerate(reversed(best), 1):
        fig.add_trace(go.Scatter(
            y=data[i],
            mode='lines',
            name=f"✅ #{idx} лучший — {balances[i]:,.2f}",
            line=dict(color='green'),
            opacity=0.6
        ))
        fig.add_trace(go.Scatter(
                x=[0],
                y=[data[i][0]],
                mode="markers",
                marker=dict(color="black", size=6),
                showlegend=False,
                hovertext=f"Старт: {data[i][0]:.2f}",
                hoverinfo="text"
            ))
        fig.add_trace(go.Scatter(
                x=[len(data[i]) - 1],
                y=[data[i][-1]],
                mode="markers",
                marker=dict(color="gold", size=6),
                showlegend=False,
                hovertext=f"Финиш: {data[i][-1]:.2f}",
                hoverinfo="text"
            ))

    fig.update_layout(
        title="Лучшие и худшие траектории капитала",
        xaxis_title="Номер сделки",
        yaxis_title="Баланс",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_distribution(balances, initial_balance):
    st.markdown("#### 📊 Распределение финальных балансов")
    st.caption("""
    **Ось X** — итоговый капитал по завершении симуляции.  
    **Ось Y** — сколько симуляций дали такой результат.  
    Это гистограмма, показывающая частоту различных итогов.
    """)

    st.info("""
    👉 **Интерпретация:**  
    Узкий пик = стратегия даёт стабильный результат.  
    Распределение смещено вправо = потенциал прибыли.  
    Много слева = риск потерять капитал.
    """)

    profitable = np.sum(balances > initial_balance)
    unprofitable = len(balances) - profitable
    volatility = np.std(balances)

    st.caption(f"🟢 В плюсе: **{profitable}** | 🔴 В минусе: **{unprofitable}** | 📉 Волатильность: **{volatility:.2f}$**")

    fig = px.histogram(
        x=balances,
        nbins=50,
        labels={"x": "Финальный баланс"},
        title="Гистограмма итогов по симуляциям",
        opacity=0.75
    )

    fig.add_vline(x=initial_balance, line_dash="dash", line_color="red", annotation_text="Старт", annotation_position="top right")

    fig.update_layout(
        title=f"Гистограмма итогов ({len(balances)} симуляций)",
        xaxis_title="Финальный баланс",
        yaxis_title="Количество симуляций",
        bargap=0.05,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_liquidation_distribution(liq_steps, num_trades):
    st.markdown("#### 💀 Распределение ликвидаций по сделкам")
    st.caption("""
    **Ось X** — номер сделки, на которой произошла ликвидация.  
    **Ось Y** — сколько симуляций были ликвидированы на этом шаге.
    """)

    st.info("""
    👉 **Анализ ликвидаций:**  
    Пики в начале — высокие риски в начале торговли.  
    Плавный спад — стратегия устойчива к случайным неудачам.
    """)

    if liq_steps:
        avg_liq = np.mean(liq_steps)
        st.caption(f"📍 Средний шаг ликвидации: **{avg_liq:.1f}**")
    else:
        st.caption("✅ Ни одна симуляция не была ликвидирована!")

    survived_pct = 100 * (1 - len(liq_steps) / len(data))
    st.caption(f"🧱 Симуляций без ликвидации: **{survived_pct:.1f}%**")

    fig = px.histogram(
        x=liq_steps,
        nbins=num_trades,
        labels={"x": "Шаг ликвидации"},
        title="Шаги, на которых происходили ликвидации",
        opacity=0.75
    )

    fig.update_layout(
        title=f"Шаги ликвидаций ({len(liq_steps)} из {num_trades} сделок)",
        xaxis_title="Номер сделки",
        yaxis_title="Кол-во ликвидаций",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_probability_heatmap(data, initial_balance):
    st.markdown("#### 🧠 Карта вероятностей (ниже стартового баланса)")
    st.caption("""
    **Ось X** — номер сделки (шаг симуляции).  
    **Ось Y** — доля симуляций, в которых баланс опустился ниже начального.
    """)

    st.info("""
    👉 **Как читать:**  
    Рост кривой — больше просадок на этом этапе.  
    Падение или плато — стратегия стабилизируется.
    """)

    heat = [np.sum(data[:, j] < initial_balance) / len(data) for j in range(1, data.shape[1])]

    max_risk_step = np.argmax(heat) + 1
    max_risk_value = np.max(heat)
    st.caption(f"🚨 Максимум просадок на шаге **{max_risk_step}** — в просадке были **{max_risk_value:.1%}** симуляций.")

    heat = [np.sum(data[:, j] < initial_balance) / len(data) for j in range(1, data.shape[1])]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(1, len(heat)+1)),
        y=heat,
        mode='lines',
        fill='tozeroy',
        name="Просадки",
        line=dict(color="purple")
    ))

    fig.update_layout(
         title=f"Доля просевших симуляций ({len(data)} штук на каждом шаге)",
        xaxis_title="Номер сделки",
        yaxis_title="Доля ниже стартового капитала",
        yaxis=dict(range=[0, 1]),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

