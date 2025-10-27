import streamlit as st
import numpy as np
import pandas as pd

def render_rmm_calculators():
    st.markdown("## 🧮 Калькулятор входа")

    calc_deposit = st.number_input("💼 Депозит ($)", value=1000.0, key="calc_dep")
    calc_risk_pct = st.number_input("📉 Риск на день (%)", value=2.0, key="calc_risk")
    calc_num_trades = st.number_input("🔢 Сделок в день", value=3, key="calc_trades")
    calc_stop_pct = st.number_input("🛑 Стоп (%)", value=1.0, key="calc_stop")

    risk_per_trade = (calc_deposit * calc_risk_pct / 100) / calc_num_trades if calc_num_trades else 0
    position_size = risk_per_trade / (calc_stop_pct / 100) if calc_stop_pct else 0

    st.markdown(f"**⚠️ Риск на сделку:** ${risk_per_trade:.2f}")
    st.markdown(f"**🎯 Объём входа:** ${position_size:.2f}")
        
    st.markdown("---")
    st.markdown("## 📐 Калькулятор объема по SL (%)")

    dep_sl = st.number_input("💼 Депозит ($)", value=1000.0, min_value=0.0, key="slcalc_dep")
    risk_pct_input = st.number_input(
        "🔥 Фиксированный риск на сделку (%)",
        value=2.0, min_value=0.01, max_value=100.0, step=0.01, key="slcalc_risk_pct"
    )

    if dep_sl <= 0:
        st.warning("Укажи положительный депозит.")
    else:
        risk_dollar_direct = round(dep_sl * risk_pct_input / 100.0, 2)
        max_loss_pct_stop = round(risk_pct_input / 4.0, 2)
        max_loss_dollar_stop = round(dep_sl * (max_loss_pct_stop / 100.0), 2)
        risk_per_trade_dollar_for_table = round(max_loss_dollar_stop, 2)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Риск на сделку (%)", f"{risk_pct_input:.2f}%")
        c2.metric("Риск на сделку ($)", f"{risk_dollar_direct:.2f}$")
        c3.metric("Макс. потеря STOP-торги (%)", f"{max_loss_pct_stop:.2f}%")
        c4.metric("Макс. потеря STOP-торги ($)", f"{max_loss_dollar_stop:.2f}$")

        sl_min = 0.10
        sl_max = 10.0
        sl_step = 0.10

        sl_values = np.round(np.arange(sl_min, sl_max + 1e-9, sl_step), 2)

        entry_sizes_raw = risk_per_trade_dollar_for_table * 100.0 / sl_values
        entry_cap = 2.0 * dep_sl
        entry_sizes_capped = np.minimum(entry_sizes_raw, entry_cap)

        df_sl = pd.DataFrame({
            "SL (%)": sl_values,
            "Риск на сделку ($)": np.repeat(risk_per_trade_dollar_for_table, len(sl_values)),
            "Сумма входа ($)": np.round(entry_sizes_capped, 2),
        })

        st.dataframe(df_sl, use_container_width=True)