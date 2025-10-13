import streamlit as st
import pandas as pd


def render_signal_detector() -> None:
    """Простой детектор торговых сигналов на основе правил.

    Базовые сигналы: пересечение SMA, RSI зоны (если есть столбец RSI),
    пробои экстремумов.
    """

    st.markdown("## 🔍 Детектор сигналов")

    uploaded = st.file_uploader("Загрузите CSV с ценами (Date, Open, High, Low, Close)", type=["csv"])
    if uploaded is None:
        st.info("Загрузите данные, чтобы начать анализ")
        return

    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        st.error(f"Не удалось прочитать CSV: {exc}")
        return

    required = {"Close"}
    if not required.issubset(set(df.columns)):
        st.error("Минимально требуется столбец Close")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        sma_fast = st.number_input("SMA fast", min_value=2, max_value=200, value=9)
    with col2:
        sma_slow = st.number_input("SMA slow", min_value=3, max_value=400, value=21)
    with col3:
        use_breakouts = st.checkbox("Учитывать пробои High/Low", value=True)

    df = df.copy()
    df["SMA_fast"] = df["Close"].rolling(int(sma_fast)).mean()
    df["SMA_slow"] = df["Close"].rolling(int(sma_slow)).mean()

    signals: list[dict] = []

    # Сигналы по пересечению SMA
    for i in range(1, len(df)):
        prev_fast, prev_slow = df.loc[i - 1, ["SMA_fast", "SMA_slow"]]
        fast, slow = df.loc[i, ["SMA_fast", "SMA_slow"]]
        if pd.notna(prev_fast) and pd.notna(prev_slow) and pd.notna(fast) and pd.notna(slow):
            if prev_fast <= prev_slow and fast > slow:
                signals.append({"Индекс": i, "Сигнал": "🟢 Пересечение вверх (SMA)"})
            if prev_fast >= prev_slow and fast < slow:
                signals.append({"Индекс": i, "Сигнал": "🔴 Пересечение вниз (SMA)"})

    # Пробои экстремумов
    if use_breakouts and {"High", "Low"}.issubset(set(df.columns)):
        window = 20
        for i in range(window, len(df)):
            if df.loc[i, "Close"] > df.loc[i - window:i - 1, "High"].max():
                signals.append({"Индекс": i, "Сигнал": "📈 Пробой максимума"})
            if df.loc[i, "Close"] < df.loc[i - window:i - 1, "Low"].min():
                signals.append({"Индекс": i, "Сигнал": "📉 Пробой минимума"})

    if signals:
        st.success(f"Найдено сигналов: {len(signals)}")
        st.dataframe(pd.DataFrame(signals), use_container_width=True)
    else:
        st.info("Сигналы не обнаружены по текущим настройкам")


