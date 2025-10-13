import json
import math
from typing import Dict, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .data_fetcher import CryptoDataFetcher
import numpy as np


def fetch_fear_greed_index() -> Tuple[str, str]:
    """Получить индекс страха/жадности с alternative.me (бесплатно).

    Returns:
        value_text: строковое значение индекса (0-100)
        classification: текстовая классификация (Extreme Fear ... Extreme Greed)
    """
    try:
        import requests
        resp = requests.get("https://api.alternative.me/fng/?limit=1").json()
        data = resp.get("data", [{}])[0]
        return data.get("value", "-"), data.get("value_classification", "-")
    except Exception:
        return "-", "нет данных"


def determine_trend(df: pd.DataFrame) -> Tuple[str, float]:
    """Определить тренд по EMA50/EMA200 и их наклону."""
    price = df["Close"]
    ema50 = price.ewm(span=50).mean()
    ema200 = price.ewm(span=200).mean()

    slope50 = (ema50.iloc[-1] - ema50.iloc[-10]) / 10 if len(ema50) > 10 else 0.0
    slope200 = (ema200.iloc[-1] - ema200.iloc[-10]) / 10 if len(ema200) > 10 else 0.0

    bullish = price.iloc[-1] > ema200.iloc[-1] and ema50.iloc[-1] > ema200.iloc[-1] and slope50 > 0
    bearish = price.iloc[-1] < ema200.iloc[-1] and ema50.iloc[-1] < ema200.iloc[-1] and slope50 < 0

    if bullish:
        return "BULLISH", max(slope50, 0.0)
    if bearish:
        return "BEARISH", abs(min(slope50, 0.0))
    return "NEUTRAL", abs(slope50 - slope200)


def classify_market_state(df: pd.DataFrame) -> Dict[str, str]:
    """Классифицировать состояние рынка по RSI/Volatility/ADX."""
    rsi = df.get("RSI")
    adx = df.get("ADX")
    vol = df.get("Volatility")

    rsi_state = "нейтрально"
    if rsi is not None and not rsi.empty:
        last_rsi = float(rsi.iloc[-1])
        if last_rsi < 30:
            rsi_state = "перепроданность"
        elif last_rsi > 70:
            rsi_state = "перекупленность"

    trend_strength = "умеренный"
    if adx is not None and not adx.empty:
        last_adx = float(adx.iloc[-1])
        if last_adx >= 25:
            trend_strength = "сильный"
        elif last_adx <= 15:
            trend_strength = "слабый"

    volatility_state = "умеренная"
    if vol is not None and not vol.empty:
        last_vol = float(vol.iloc[-1])
        vol_ma = float(vol.rolling(50).mean().iloc[-1]) if len(vol) >= 50 else last_vol
        if last_vol > 1.5 * vol_ma:
            volatility_state = "высокая"
        elif last_vol < 0.7 * vol_ma:
            volatility_state = "низкая"

    return {
        "rsi": rsi_state,
        "trend_strength": trend_strength,
        "volatility": volatility_state,
    }


def plot_chart(df: pd.DataFrame, title: str) -> None:
    price = df["Close"]
    ema50 = price.ewm(span=50, adjust=False).mean()
    ema200 = price.ewm(span=200, adjust=False).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=ema50, name="EMA 50", line=dict(color="#22c55e", width=1.5)))
    fig.add_trace(go.Scatter(x=df.index, y=ema200, name="EMA 200", line=dict(color="#3b82f6", width=1.5)))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10), title=title)
    st.plotly_chart(fig, use_container_width=True)

def compute_trend_signal(df: pd.DataFrame) -> str:
    price = df['Close']
    ema50 = price.ewm(span=50, adjust=False).mean()
    ema200 = price.ewm(span=200, adjust=False).mean()
    if price.iloc[-1] > ema200.iloc[-1] and ema50.iloc[-1] > ema200.iloc[-1]:
        return 'BULL'
    if price.iloc[-1] < ema200.iloc[-1] and ema50.iloc[-1] < ema200.iloc[-1]:
        return 'BEAR'
    return 'NEUTRAL'


def render_coin_summary() -> None:
    st.markdown("## 🧭 Сводка по монете")

    fetcher = CryptoDataFetcher()
    options = fetcher.get_available_symbols()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_name = st.selectbox("Выберите монету (USDT пары)", list(options.keys()), index=0)
    with col2:
        period = st.selectbox("Период", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
    with col3:
        timeframe = st.selectbox(
            "Интервал",
            ["1h", "4h", "1d"],
            index=2,
            help="Интервал свечей"
        )
    st.caption("Пояснение: Период — сколько истории загрузить (например, 3mo = три месяца данных). Интервал — длительность одной свечи (например, 1h = часовая свеча).")

    symbol = options[selected_name]

    st.markdown("---")
    with st.spinner("Загружаем данные..."):
        df = fetcher.fetch_data(symbol, period=period, interval=timeframe)

    if df is None or df.empty:
        st.error("Не удалось получить данные")
        return

    trend, strength_val = determine_trend(df)
    market = classify_market_state(df)
    fear_val, fear_class = fetch_fear_greed_index()

    last_price = float(df["Close"].iloc[-1])
    price_str = f"${last_price:,.2f}" if last_price >= 1 else f"${last_price:.6f}"

    # Метрики
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Текущая цена", price_str)
    with col2:
        st.metric("Тренд", trend)
    with col3:
        st.metric("Состояние RSI", market["rsi"]) 
    with col4:
        st.metric("Страх/Жадность", f"{fear_val} ({fear_class})")

    # Доп. состояние
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success(f"Сила тренда: {market['trend_strength']}")
    with c2:
        st.warning(f"Волатильность: {market['volatility']}")
    with c3:
        rsi_val = df['RSI'].iloc[-1] if 'RSI' in df.columns else None
        if rsi_val is not None:
            st.info(f"RSI(14): {rsi_val:.1f}")

    # Объяснение индекса страха/жадности
    st.markdown("---")
    st.markdown("### 🧠 Индекс страха и жадности — что это и как использовать")

    if fear_val.isdigit():
        score = int(fear_val)
        st.progress(score / 100)
    else:
        score = None

    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("""
        - 0–24: Экстремальный страх
        - 25–49: Страх
        - 50: Нейтрально
        - 51–74: Жадность
        - 75–100: Экстремальная жадность
        """)
    with col2:
        st.write("""
        Индекс агрегирует несколько факторов рынка (волатильность, объёмы,
        тренд и соц.метрики) и сводит их к шкале 0–100.
        
        Практика применения:
        - При страхе рынок часто перепродаётся → искать подтверждённые лонги.
        - При жадности рынок часто перегрет → искать подтверждённые шорты/фиксацию.
        - Не использовать в одиночку — комбинировать с трендом (EMA200), RSI, уровнями/паттернами.
        """)

    with st.expander("Пример интерпретации для текущей монеты"):
        bullet = []
        if score is not None:
            if score <= 25:
                bullet.append("На рынке доминирует страх — повышенная вероятность ложных пробоев вниз и отскоков.")
            elif score >= 75:
                bullet.append("Доминирует жадность — высок риск резких разворотов, следите за дивергенциями.")
            else:
                bullet.append("Баланс участников близок к нейтральному — сигналов от индекса меньше, ориентируйтесь на тренд.")
        bullet.append(f"Тренд по EMA: {trend}. Сила: {market['trend_strength']}.")
        bullet.append(f"RSI: {market['rsi']}. Волатильность: {market['volatility']}.")
        st.write("\n".join([f"- {b}" for b in bullet]))

    st.markdown("---")
    plot_chart(df, title=f"{selected_name} / USDT")

    # Дополнительные инструменты анализа
    st.markdown("### 🧰 Дополнительные инструменты")
    tool_tabs = st.tabs(["EMA/MA", "RSI", "Боллинджер", "ATR", "Карта ликвидности (оценка)"])
    

    with tool_tabs[0]:
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        ema200 = df['Close'].ewm(span=200, adjust=False).mean()
        st.line_chart(pd.DataFrame({"Close": df['Close'], "EMA20": ema20, "EMA50": ema50, "EMA200": ema200}))
        st.caption("EMA20/50/200 — оценка кратко/средне/долгосрочного тренда")
        with st.expander("Как использовать"):
            st.markdown("""
            - EMA20 выше EMA50/200 ⇒ краткосрочный импульс вверх.
            - EMA50 над EMA200 ⇒ среднесрочный бычий тренд; ниже ⇒ медвежий.
            - Пересечения EMA50/EMA200 — ориентир смены среднесрочного тренда.
            """)

    with tool_tabs[1]:
        st.line_chart(pd.DataFrame({"RSI(14)": df['RSI']}))
        st.caption("RSI(14): <30 — перепроданность, >70 — перекупленность")
        with st.expander("Как использовать"):
            st.markdown("""
            - На тренде RSI держится в крайних зонах — не контртрендуйте без подтверждений.
            - Дивергенции RSI у уровней усиливают разворотные сценарии.
            - С EMA200 фильтруйте направления входов.
            """)

    with tool_tabs[2]:
        bb_mid = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        bb_up = bb_mid + 2 * bb_std
        bb_lo = bb_mid - 2 * bb_std
        st.line_chart(pd.DataFrame({"Middle": bb_mid, "Upper": bb_up, "Lower": bb_lo}))
        st.caption("Полосы Боллинджера (20, 2σ) — волатильность и крайние зоны")
        with st.expander("Как использовать"):
            st.markdown("""
            - Касание Upper/Lower на флете часто ведёт к возврату к Middle.
            - Сужение полос ⇒ сжатие; пробой после сжатия — сигнал начала импульса.
            - Расширение полос ⇒ рост волатильности.
            """)

    with tool_tabs[3]:
        st.line_chart(pd.DataFrame({"ATR(14)": df['ATR']}))
        st.caption("ATR(14) — средний истинный диапазон, мера волатильности")
        with st.expander("Как использовать"):
            st.markdown("""
            - Ставьте стопы кратно ATR (например, 1–2×ATR) — адаптивно к волатильности.
            - Рост ATR — повышенная турбулентность, снижайте размер позиции.
            - Падение ATR — рынок сжимается, ждите выхода из диапазона.
            """)

    with tool_tabs[4]:
        st.caption("Мини‑теплокарта: тренд по интервалам (EMA50/EMA200)")
        intervals = ["1h", "4h", "1d"]
        heat = {}
        fetcher = CryptoDataFetcher()
        for iv in intervals:
            data_iv = fetcher.fetch_data(symbol, period=period, interval=iv)
            if data_iv is not None and not data_iv.empty:
                heat[iv] = compute_trend_signal(data_iv)
            else:
                heat[iv] = 'N/A'

        cols = st.columns(len(intervals))
        for i, iv in enumerate(intervals):
            val = heat[iv]
            if val == 'BULL':
                cols[i].success(f"{iv}: BULL")
            elif val == 'BEAR':
                cols[i].error(f"{iv}: BEAR")
            elif val == 'NEUTRAL':
                cols[i].warning(f"{iv}: NEUTRAL")
            else:
                cols[i].info(f"{iv}: N/A")

    # Карта ликвидности (оценка)
    with tool_tabs[4]:
        st.caption("Оценка скоплений ликвидности по экстремумам и импульсной волатильности. Это не Coinglass, но полезная проекция.")
        window = st.slider("Окно экстремумов, баров", 5, 100, 20)
        close = df['Close']
        high = df['High']
        low = df['Low']

        # Найдем локальные максимумы/минимумы
        def rolling_extrema(series: pd.Series, w: int) -> pd.Series:
            return series[(series.shift(1) < series) & (series.shift(-1) < series)]

        swing_highs = (high == high.rolling(window, center=True).max())
        swing_lows = (low == low.rolling(window, center=True).min())

        levels = []
        for idx in df.index:
            if swing_highs.loc[idx]:
                levels.append((idx, float(high.loc[idx]), 'H'))
            if swing_lows.loc[idx]:
                levels.append((idx, float(low.loc[idx]), 'L'))

        # Строим горизонтальные зоны +-ATR от уровней
        atr = df['ATR']
        if not atr.isna().all():
            last_atr = float(atr.iloc[-1])
        else:
            last_atr = float(close.diff().abs().rolling(14).mean().iloc[-1])

        if levels:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=high, low=low, close=close, name='OHLC'))
            for _, lvl, typ in levels[-50:]:
                color = '#ef4444' if typ == 'H' else '#22c55e'
                fig.add_hrect(y0=lvl - 0.5 * last_atr, y1=lvl + 0.5 * last_atr, line_width=0, fillcolor=color, opacity=0.15)
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("Как использовать"):
                st.markdown("""
                - Красные зоны (H) — возможные кластеры стопов над свинг‑хаями; зелёные (L) — под свинг‑лоями.
                - Ширина ~0.5×ATR — ориентир глубины выноса; подбирайте под инструмент и ТФ.
                - Стратегия: ждать захода в зону + подтверждение (свеча/объём) и торговать возврат.
                """)
        else:
            st.info("Недостаточно данных для оценки уровней. Увеличьте период или уменьшите окно.")


