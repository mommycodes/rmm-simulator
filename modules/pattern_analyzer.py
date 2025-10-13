import streamlit as st
import pandas as pd


def render_pattern_analyzer() -> None:
    """Интерфейс анализатора паттернов свечей и фигур.

    Минимальная версия: загрузка/ввод данных + выбор типа паттернов + таблица результатов.
    """

    st.markdown("## 📊 Анализатор паттернов")

    mode = st.radio(
        "Источник данных:",
        ["📤 Загрузить CSV", "✍️ Ввести вручную"],
        horizontal=True,
    )

    df: pd.DataFrame | None = None

    if mode == "📤 Загрузить CSV":
        uploaded = st.file_uploader("Загрузите файл с котировками (OHLC)", type=["csv"])
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
            except Exception as exc:
                st.error(f"Не удалось прочитать CSV: {exc}")
    else:
        st.caption("Минимальный пример данных (Date, Open, High, Low, Close)")
        sample = "Date,Open,High,Low,Close\n2024-01-01,100,110,95,108\n2024-01-02,108,112,101,105"
        text = st.text_area("Вставьте данные CSV", sample, height=140)
        try:
            df = pd.read_csv(pd.io.common.StringIO(text))
        except Exception:
            df = None

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        detect_candles = st.checkbox("Свечные паттерны", value=True)
    with col2:
        detect_patterns = st.checkbox("Фигуры ТА (пробои, клин и т.д.)", value=False)
    with col3:
        min_bars = st.number_input("Мин. длина паттерна", min_value=1, max_value=200, value=3)

    if st.button("🔎 Найти паттерны", use_container_width=True):
        if df is None or df.empty:
            st.warning("Загрузите или введите данные перед анализом")
            return

        required_cols = {"Open", "High", "Low", "Close"}
        if not required_cols.issubset(set(df.columns)):
            st.error("В данных должны быть столбцы: Open, High, Low, Close")
            return

        results: list[dict] = []

        if detect_candles:
            # Примеры простых свечных условий
            for idx in range(1, len(df)):
                o, h, l, c = df.loc[idx, ["Open", "High", "Low", "Close"]]
                prev_c = df.loc[idx - 1, "Close"]

                is_bullish_engulfing = (c > o) and (c >= prev_c) and (o <= df.loc[idx - 1, "Open"]) and (c - o > (o - c if o > c else 0))
                is_bearish_engulfing = (c < o) and (c <= prev_c) and (o >= df.loc[idx - 1, "Open"]) and (o - c > (c - o if c > o else 0))

                if is_bullish_engulfing:
                    results.append({
                        "Индекс": idx,
                        "Тип": "Свечной",
                        "Паттерн": "Bullish Engulfing",
                    })
                if is_bearish_engulfing:
                    results.append({
                        "Индекс": idx,
                        "Тип": "Свечной",
                        "Паттерн": "Bearish Engulfing",
                    })

        if detect_patterns:
            # Заглушка для фигур ТА: ищем локальные пробои High/Low на окне min_bars
            for idx in range(min_bars, len(df)):
                window = df.iloc[idx - min_bars:idx]
                if df.loc[idx, "Close"] > window["High"].max():
                    results.append({"Индекс": idx, "Тип": "Фигура", "Паттерн": "Пробой вверх"})
                if df.loc[idx, "Close"] < window["Low"].min():
                    results.append({"Индекс": idx, "Тип": "Фигура", "Паттерн": "Пробой вниз"})

        if results:
            st.success(f"Найдено совпадений: {len(results)}")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("Совпадений не найдено по указанным условиям")


