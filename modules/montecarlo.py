import streamlit as st
import numpy as np
import pandas as pd

# Внешние модули проекта
from simulator import run_simulation
from visualizations import (
    plot_simulations,
    plot_best_worst,
    plot_distribution,
    plot_liquidation_distribution,
    plot_probability_heatmap,
)

# ===============================
# Раздел: Симулятор Монте-Карло
# ===============================
def render_monte_carlo():
    st.markdown("## 🎯 Торговый симулятор стратегии")
    
    # === Ввод параметров ===
    st.markdown("### ⚙️ Входные параметры")
    colA, colB, colC = st.columns(3)
    with colA:
        initial_balance = st.number_input("💰 Начальный баланс ($)", value=100.0, min_value=1.0, help="Сумма, с которой начинается каждая симуляция")
        num_trades = st.number_input("🔁 Кол-во сделок", value=50, min_value=1, max_value=1000, help="Сколько подряд сделок будет совершено в одной симуляции")
        liquidation_pct = st.number_input("💀 Порог ликвидации (%)", value=1.0, min_value=0.0, max_value=100.0, help="Если баланс падает ниже этого процента от начального — считается, что произошла ликвидация")
    with colB:    
        risk_mode = st.radio("📌 Выберите метод расчёта риска:", ["Риск на сделку (%)", "Риск на день (%)"], index=0)
        if risk_mode == "Риск на сделку (%)":
            risk_pct = st.number_input("🔥 Риск на сделку (%)", value=2.0, min_value=0.1, max_value=100.0,
                                    help="Процент капитала, которым вы рискуете в каждой сделке")
            risk_dollars = initial_balance * risk_pct / 100
            st.caption(f"⚠️ Риск на сделку: **{risk_pct:.2f}%** ≈ ${risk_dollars:.2f}")
        else:
            day_risk_pct = st.number_input("📉 Риск на день (%)", value=2.0, min_value=0.1, max_value=100.0,
                                        help="Сколько процентов капитала вы готовы потерять за день")
            risk_pct = day_risk_pct / num_trades
            risk_dollars = initial_balance * risk_pct / 100
            st.caption(f"⚠️ Риск на сделку: **{risk_pct:.2f}%** ≈ ${risk_dollars:.2f} из {day_risk_pct:.1f}% на день")
    with colC:    
        stop_pct = st.number_input("🛑 Стоп-лосс (%)", value=1.0, min_value=0.1, max_value=100.0, help="Процент от пикового баланса, при котором сделка закрывается в убыток")
        rr = st.number_input("⚖️ Reward/Risk (RR)", value=2.0, min_value=0.1, help="Соотношение прибыли к убытку. RR = 2 означает, что при стопе 1% вы берёте профит 2%.")
        if stop_pct > 0:
            tp_pct = stop_pct * rr
            st.caption(f"📌 Текущий RR: **{rr:.1f}:1** — стоп: {stop_pct:.1f}%, профит: {tp_pct:.1f}%")
        else:
            st.caption("📌 Текущий RR: **{rr:.1f}:1** — ожидается ненулевой стоп для вычисления профита.")
        winrate = st.slider("🎯 Winrate (%)", min_value=0, max_value=100, value=50, help="Как часто стратегия приносит прибыль. Например, 60% означает 6 из 10 сделок — прибыльные")
        simulations = st.number_input("📊 Кол-во симуляций", value=100, min_value=1, max_value=10000, help="Сколько разных траекторий капитала будет смоделировано")

    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>🚀 <b>Начать симуляцию</b></h3>", unsafe_allow_html=True)
    start = st.button("▶️ Старт", use_container_width=True)

    if start:
        data, balances, liq_hits, liq_steps, drawdowns, all_trades = run_simulation(
            initial_balance, num_trades, risk_pct, rr, winrate, simulations, liquidation_pct, stop_pct
        )
        st.session_state.sim_data   = data
        st.session_state.balances   = balances
        st.session_state.liq_hits   = liq_hits
        st.session_state.liq_steps  = liq_steps
        st.session_state.drawdowns  = drawdowns
        st.session_state.all_trades = all_trades

    if "sim_data" in st.session_state:
        data       = st.session_state.sim_data
        balances   = st.session_state.balances
        liq_hits   = st.session_state.liq_hits
        liq_steps  = st.session_state.liq_steps
        drawdowns  = st.session_state.drawdowns
        all_trades = st.session_state.all_trades

        st.subheader("📊 Результаты симуляции")

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
        st.markdown("## 📊 Визуализация симуляций")
        st.caption("""
        Графики помогут **наглядно оценить поведение стратегии**:  
        где риски максимальны, насколько результат стабилен и как часто происходят критические просадки.
        """)
        with st.container():
            st.markdown("### 1. Траектории капитала")
            plot_simulations(data, initial_balance)

        st.markdown("---")

        with st.container():
            st.markdown("### 2. Лучшие и худшие случаи")
            plot_best_worst(data, balances)

        st.markdown("---")

        with st.container():
            st.markdown("### 3. Гистограмма итогов")
            plot_distribution(balances, initial_balance)

        st.markdown("---")

        with st.container():
            st.markdown("### 4. Карта вероятностей просадок")
            plot_probability_heatmap(data, initial_balance)

        if liq_steps:
            st.markdown("---")
            with st.container():
                st.markdown("### 5. Ликвидации по шагам")
                plot_liquidation_distribution(data, liq_steps, num_trades)

        st.markdown("---")
        st.markdown("### 🎛 Sensitivity Analysis (3D-карта)")

        with st.expander("📊 Показать карту по winrate × RR"):
            st.caption("""
            Здесь можно увидеть, **при каких условиях стратегия становится прибыльной**.  
            Выберите диапазон `Winrate` и `RR`, и симулятор построит 3D-карту средней доходности.
            """)
            winrate_range = st.slider("🎯 Диапазон Winrate", 10, 100, (30, 70), step=5)
            rr_range = st.slider("⚖️ Диапазон RR", 0.5, 5.0, (1.0, 3.0), step=0.5)

            winrates = list(range(winrate_range[0], winrate_range[1] + 1, 5))
            rrs = list(np.round(np.arange(rr_range[0], rr_range[1] + 0.1, 0.5), 2))

            sim_count = st.number_input("🔁 Симуляций на каждую точку", min_value=10, max_value=1000, value=100)

            if st.button("🚀 Построить карту"):
                from visualizations import plot_sensitivity_analysis
                plot_sensitivity_analysis(
                    initial_balance=initial_balance,
                    num_trades=num_trades,
                    risk_pct=risk_pct,
                    winrates=winrates,
                    rrs=rrs,
                    simulations=sim_count,
                    liquidation_pct=liquidation_pct,
                    stop_pct=stop_pct
                )

        # === Вывод симуляции для разбора
        st.markdown("---")
        st.markdown("### 📋 Детальный разбор симуляции")
        st.info("""
        🔍 *Здесь вы можете проанализировать любую симуляцию по шагам:*  
        каждый параметр: **PnL**, 📉 *просадка*, 📊 *динамика капитала* — перед вами!

        **Выберите** интересующую симуляцию из выпадающего списка ниже ⬇️
        """)

        # Индексы лучшей и худшей
        best_idx = np.argmax(balances)
        worst_idx = np.argmin(balances)

        # Список для выбора
        options = {
            f"🔥 Лучшая симуляция — {balances[best_idx]:,.2f}": best_idx,
            f"🧊 Худшая симуляция — {balances[worst_idx]:,.2f}": worst_idx,
        }
        # Все симуляции по номерам
        for i in range(len(balances)):
            options[f"📈 Симуляция #{i+1} — {balances[i]:,.2f}"] = i

        # Выбор симуляции
        selected_label = st.selectbox("🔍 **Выберите симуляцию для просмотра**", list(options.keys()))
        selected_index = options[selected_label]

        # Построение таблицы
        one_sim = data[selected_index]
        peak = one_sim[0]
        trades = []
        trades_raw = st.session_state.all_trades[selected_index]

        for i in range(1, len(one_sim)):
            pre_balance = one_sim[i - 1]
            post_balance = one_sim[i]
            pnl = post_balance - pre_balance
            peak = max(peak, post_balance)
            drawdown = (peak - post_balance) / peak if peak > 0 else 0

            trade_data = trades_raw[i - 1] 
            position_size = trade_data["position_size"]
            stop_loss_dollars = trade_data["sl"]
            take_profit_dollars = trade_data["tp"]

            trades.append({
                "№": i,
                "🏁 Исход": "✅ Win" if pnl > 0 else "❌ Loss",
                "💼 До сделки": f"{pre_balance:,.2f}",
                "💸 PnL": f"{pnl:+.2f}",
                "📊 После сделки": f"{post_balance:,.2f}",
                "📉 Просадка": f"{drawdown:.0%}",
                "🏔 Пик": f"{peak:,.2f}",
                "📦 Объём входа ($)": f"{position_size:,.2f}",
                "🛑 SL ($)": f"{stop_loss_dollars:,.2f}",
                "🎯 TP ($)": f"{take_profit_dollars:,.2f}",
            })

        df_trades = pd.DataFrame(trades)

        # Вывод
        with st.expander(f"📋 _Показать таблицу шагов выбранной симуляции_"):
            st.markdown("""
        **📑 Что видно в таблице:**
        - _**🔢 №**_ — номер сделки по порядку
        - _**🏁 Исход**_ — победа ✅ или поражение ❌
        - _**💸 PnL ($)**_ — прибыль или убыток в долларах по каждой сделке
        - _**💼 До сделки / 📊 После сделки**_ — баланс до и после каждой сделки
        - _**📉 Просадка**_ — снижение от максимального баланса до текущего
        - _**🏔 Пик**_ — самый высокий баланс, достигнутый к этому моменту
        - _**📦 Объём входа ($)**_ — сумма, на которую была открыта сделка  
        👉 `вход = риск на сделку / стоп % × 100`
        - _**🛑 SL ($)**_ — потенциальный убыток при срабатывании стопа  
        👉 `SL = вход × стоп %`
        - _**🎯 TP ($)**_ — прибыль при достижении тейк-профита  
        👉 `TP = SL × RR`

        👉 Используйте таблицу для анализа поведения стратегии на каждом этапе!
        """)
            st.dataframe(df_trades, use_container_width=True)