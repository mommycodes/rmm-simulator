import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from simulator import run_simulation
from visualizations import plot_simulations, plot_best_worst, plot_distribution, plot_liquidation_distribution, plot_probability_heatmap

st.set_page_config(layout="wide")
st.title("🎯 Торговый симулятор стратегии")

# === Ввод параметров ===
with st.sidebar:
    st.header("⚙️ Входные параметры")
    initial_balance = st.number_input("💰 Начальный баланс ($)", value=100.0, min_value=1.0, help="Сумма, с которой начинается каждая симуляция")
    num_trades = st.number_input("🔁 Кол-во сделок", value=50, min_value=1, max_value=1000, help="Сколько подряд сделок будет совершено в одной симуляции")
    risk_pct = st.number_input("🔥 Риск на сделку (%)", value=2.0, min_value=0.1, max_value=100.0, help="Процент капитала, которым вы рискуете в каждой сделке")
    st.caption(f"📌 Текущий RR: **{risk_pct:.1f}:1** — прибыль в {risk_pct:.1f} раза больше убытка")
    rr = st.number_input("⚖️ Reward/Risk (RR)", value=2.0, min_value=0.1, help="Соотношение прибыли к риску. RR = 2 означает, что потенциальная прибыль в 2 раза больше риска")
    winrate = st.slider("🎯 Winrate (%)", min_value=0, max_value=100, value=50, help="Как часто стратегия приносит прибыль. Например, 60% означает 6 из 10 сделок — прибыльные")
    simulations = st.number_input("📊 Кол-во симуляций", value=100, min_value=1, max_value=10000, help="Сколько разных траекторий капитала будет смоделировано")
    liquidation_pct = st.number_input("💀 Порог ликвидации (%)", value=1.0, min_value=0.0, max_value=100.0, help="Если баланс падает ниже этого процента от начального — считается, что произошла ликвидация")

# === Алгоритм Манименеджмента ===
with st.container():
    st.markdown("### 📘 Алгоритм манименеджмента")
    st.markdown("""
1. ❌ **Стоп-торги** после **3 убыточных сделок**
2. ⚖️ **RR минимум 3:1** — каждая прибыль минимум в 3 раза больше убытка
3. 📋 **Торговый план на день** (по чек-листу)
4. 📓 **Ведение дневника сделок** и статистики
5. 💵 **Один и тот же риск в $** на сделку (**2%**)
6. 📉 **Не превышать объём** — рисковать только малой частью депозита
7. 🧯 **Перерыв 2–3 недели** при просадке > **20% за месяц**
8. ✅ **Закрытие дня** при прибыли **2–5%**

> 🎯 **Цель**: не потерять депозит, остаться на рынке

### 📊 Минимально жизнеспособная стратегия:
- **RR ≥ 3:1**
- **Winrate ≥ 35%**

🧠 Даже при **65% убыточных сделках** можно выжить, если соблюдать соотношение риска и прибыли!
""")

if st.button("🚀 Начать симуляцию"):
    st.subheader("📊 Результаты симуляции")
    data, balances, liq_hits, liq_steps, drawdowns = run_simulation(
        initial_balance, num_trades, risk_pct, rr, winrate, simulations, liquidation_pct
    )

        # === Метрики
    st.markdown("### 📈 Общая статистика")
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Медианное значение", f"{np.median(balances):,.2f}", help="Медианное значение итогового баланса: у половины симуляций результат выше, у половины — ниже. Нужна, чтобы увидеть, какой результат даёт стратегия в типичном сценарии без влияния экстремумов.")

        col1.metric("📈 Средний итог", f"{np.mean(balances):,.2f}", help="Арифметическое среднее всех финальных балансов. Используется для оценки общей эффективности стратегии, но чувствительно к выбросам.")

        col2.metric("🔻 Минимальный результат", f"{np.min(balances):,.2f}", help="Наихудший результат среди всех симуляций. Помогает оценить потенциальные риски и просадки при неблагоприятных условиях.")

        col2.metric("🟢 Максимальный результат", f"{np.max(balances):,.2f}", help="Наилучший результат. Позволяет увидеть потенциал стратегии в идеальных условиях, но не гарантирует повторяемости.")

        col3.metric("🎲 Волатильность (Std Dev)", f"{np.std(balances):,.2f}", help="Стандартное отклонение от среднего. Чем выше — тем менее предсказуемая стратегия. Это важный показатель стабильности.")

        col3.metric("🔁 Кол-во симуляций", str(len(balances)), help="Общее число независимых симуляций стратегии. Чем их больше — тем надёжнее статистика.")

    st.metric("💀 Ликвидации", f"{liq_hits} из {len(balances)} ({liq_hits / len(balances) * 100:.1f}%)", help="Симуляции, в которых капитал опустился ниже установленного порога ликвидации. Важно для оценки риска полного обнуления депозита.")

     # === Дополнительно
    st.markdown("### 🧪 Доп. показатели")

    st.write(f"📉 Средняя просадка: **{np.mean(drawdowns) * 100:.2f}%**")
    st.caption("Показывает, сколько в среднем терялось от пикового баланса до локального минимума. Помогает оценить уровень дискомфорта, который придётся переживать.")

    st.write(f"💵 Итог > стартового капитала: **{np.sum(balances > initial_balance)} ({np.mean(balances > initial_balance) * 100:.1f}%)**")
    st.caption("Сколько симуляций завершились в плюсе. Полезно для оценки вероятности хотя бы умеренного успеха.")

    st.write(f"💰 Итог > 2× капитала: **{np.sum(balances > initial_balance * 2)} ({np.mean(balances > initial_balance * 2) * 100:.1f}%)**")
    st.caption("Симуляции с удвоением капитала и более. Показывает, насколько велика вероятность существенного роста депозита.")

    st.write(f"🚀 Итог > 10× капитала: **{np.sum(balances > initial_balance * 10)} ({np.mean(balances > initial_balance * 10) * 100:.1f}%)**")
    st.caption("Редкие, но вдохновляющие случаи. Помогает увидеть долгосрочный потенциал стратегии при идеальных условиях.")

    # === Статус стратегии
    if np.median(balances) > initial_balance:
        st.success("✅ Стратегия прибыльная")
    else:
        st.error("❌ Стратегия убыточная")

    # === Порог безубыточности
    min_wr = 100 / (1 + rr)
    st.info(f"🎯 Минимальный Winrate для безубытка: **{min_wr:.2f}%**")
    st.caption("Минимальный процент побед, при котором стратегия хотя бы не теряет деньги. Используется для оценки жизнеспособности.")

    # === Графики ===
    plot_simulations(data, initial_balance)
    plot_best_worst(data, balances)
    plot_distribution(balances, initial_balance)
    plot_probability_heatmap(data, initial_balance)
    if liq_steps:
        plot_liquidation_distribution(liq_steps, num_trades)

    st.success("📊 Симуляция завершена!")
