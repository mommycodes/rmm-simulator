import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from .markov_chain import CryptoMarkovChain
from .data_fetcher import CryptoDataFetcher
import plotly.graph_objects as go
import plotly.express as px

def render_markov_analysis():
    """Главный интерфейс для анализа цепей Маркова"""
    
    st.markdown("## 🧠 Анализ цепей Маркова для криптовалют")
    st.info("""
    **Цепь Маркова** — это математическая модель для прогнозирования будущих состояний на основе текущего состояния.
    
    В контексте криптовалют мы анализируем:
    - 📈 **Тренды** (рост, падение, боковик)
    - 📊 **Волатильность** (низкая, средняя, высокая) 
    - 🎯 **RSI** (перепроданность, нейтрально, перекупленность)
    - 📦 **Объем торгов** (низкий, средний, высокий)
    """)
    
    # Используем только автоматический режим анализа
    render_automatic_analysis()

def render_automatic_analysis():
    """Режим автоматического анализа с API данными"""
    st.markdown("### ⚙️ Настройки автоматического анализа")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Выбор криптовалюты
        data_fetcher = CryptoDataFetcher()
        crypto_options = data_fetcher.get_available_symbols()
        
        selected_crypto = st.selectbox(
            "🪙 Выберите криптовалюту",
            list(crypto_options.keys()),
            index=0
        )
        symbol = crypto_options[selected_crypto]
    
    with col2:
        # Период данных
        period_options = {
            '1 месяц': '1mo',
            '3 месяца': '3mo', 
            '6 месяцев': '6mo',
            '1 год': '1y',
            '2 года': '2y'
        }
        
        selected_period = st.selectbox(
            "📅 Период данных",
            list(period_options.keys()),
            index=2
        )
        period = period_options[selected_period]
    
    with col3:
        # Количество прогнозов
        forecast_steps = st.number_input(
            "🔮 Шагов прогноза",
            min_value=1,
            max_value=20,
            value=5,
            help="На сколько шагов вперед делать прогноз"
        )
    
    # === Загрузка данных ===
    st.markdown("---")
    st.markdown("### 📊 Загрузка и анализ данных")
    
    if st.button("🚀 Начать анализ", use_container_width=True):
        with st.spinner("Загружаем данные и строим модель..."):
            # Создаем экземпляр класса
            markov_chain = CryptoMarkovChain()
            
            # Загружаем данные
            data = markov_chain.fetch_crypto_data(symbol, period)
            
            if data is not None and not data.empty:
                # Сохраняем в session state
                st.session_state.markov_data = data
                st.session_state.markov_chain = markov_chain
                st.session_state.symbol = symbol
                st.session_state.period = period
                
                st.success(f"✅ Данные загружены! Получено {len(data)} записей")
                
                # Показываем краткую статистику
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📈 Начальная цена", f"${data['Close'].iloc[0]:.2f}")
                with col2:
                    st.metric("📊 Конечная цена", f"${data['Close'].iloc[-1]:.2f}")
                with col3:
                    price_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
                    st.metric("📉 Изменение", f"{price_change:+.2f}%")
                with col4:
                    st.metric("📊 Волатильность", f"{data['Close'].std():.2f}")
            else:
                st.error("❌ Не удалось загрузить данные")
    
    # === Анализ состояний ===
    if "markov_chain" in st.session_state and "markov_data" in st.session_state:
        markov_chain = st.session_state.markov_chain
        data = st.session_state.markov_data
        
        st.markdown("---")
        st.markdown("### 🔍 Анализ состояний")
        
        # Определяем состояния
        with st.spinner("Определяем состояния..."):
            states = markov_chain.define_states(data)
            st.success(f"✅ Определено {len(set(states.values()))} уникальных состояний")
        
        # Строим матрицу переходов
        with st.spinner("Строим матрицу переходов..."):
            transition_matrix = markov_chain.build_transition_matrix(data)
            st.success("✅ Матрица переходов построена")
        
        # === Визуализация состояний ===
        st.markdown("#### 📊 Частота состояний")
        markov_chain.plot_state_frequency()
        
        # === Матрица переходов ===
        st.markdown("#### 🔄 Матрица переходов")
        st.caption("""
        Матрица показывает вероятность перехода из одного состояния в другое.
        Чем темнее цвет — тем выше вероятность перехода.
        """)
        markov_chain.plot_transition_heatmap()
        
        # === Анализ состояний в таблице ===
        st.markdown("#### 📋 Детальный анализ состояний")
        freq_data = markov_chain.analyze_state_frequency()
        st.dataframe(freq_data, use_container_width=True)
        
        # === Прогнозирование ===
        st.markdown("---")
        st.markdown("### 🔮 Прогнозирование")
        
        # Выбор текущего состояния
        if st.session_state.get('markov_chain'):
            state_names = markov_chain.state_names
            
            if state_names:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    selected_state = st.selectbox(
                        "🎯 Выберите текущее состояние для прогноза",
                        state_names,
                        help="Выберите состояние, из которого хотите сделать прогноз"
                    )
                
                with col2:
                    if st.button("🔮 Сделать прогноз", use_container_width=True):
                        with st.spinner("Генерируем прогноз..."):
                            predictions = markov_chain.predict_next_states(selected_state, forecast_steps)
                            st.session_state.predictions = predictions
                            st.session_state.selected_state = selected_state
                
                # === Отображение прогнозов ===
                if "predictions" in st.session_state:
                    predictions = st.session_state.predictions
                    selected_state = st.session_state.selected_state
                    
                    st.markdown(f"#### 🎯 Прогноз из состояния: {selected_state}")
                    st.caption(f"Описание: {markov_chain.get_state_description(selected_state)}")
                    
                    # Таблица прогнозов
                    forecast_data = []
                    for pred in predictions:
                        forecast_data.append({
                            'Шаг': pred['step'],
                            'Состояние': pred['state'],
                            'Описание': markov_chain.get_state_description(pred['state']),
                            'Вероятность': f"{pred['probability']:.1%}",
                            'Уверенность': '🟢 Высокая' if pred['probability'] > 0.5 else '🟡 Средняя' if pred['probability'] > 0.3 else '🔴 Низкая'
                        })
                    
                    forecast_df = pd.DataFrame(forecast_data)
                    st.dataframe(forecast_df, use_container_width=True)
                    
                    # График уверенности
                    st.markdown("#### 📈 Уверенность в прогнозах")
                    markov_chain.plot_prediction_confidence(predictions)
                    
                    # === Детальный анализ вероятностей ===
                    st.markdown("#### 🔍 Детальный анализ вероятностей")
                    
                    with st.expander("📊 Показать все вероятности для каждого шага"):
                        for i, pred in enumerate(predictions):
                            st.markdown(f"**Шаг {pred['step']}:**")
                            
                            # Сортируем по вероятности
                            sorted_probs = sorted(
                                pred['all_probabilities'].items(), 
                                key=lambda x: x[1], 
                                reverse=True
                            )
                            
                            # Показываем топ-5 наиболее вероятных состояний
                            top_states = sorted_probs[:5]
                            
                            cols = st.columns(len(top_states))
                            for j, (state, prob) in enumerate(top_states):
                                with cols[j]:
                                    st.metric(
                                        f"#{j+1}",
                                        f"{prob:.1%}",
                                        help=markov_chain.get_state_description(state)
                                    )
                                    st.caption(state)
                            
                            if i < len(predictions) - 1:
                                st.markdown("---")
        
        # === Детальные торговые рекомендации ===
        st.markdown("---")
        
        # Красивый заголовок с градиентом
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        ">
            <h2 style="color: white; margin: 0; font-size: 28px;">
                💡 Торговые рекомендации
            </h2>
            <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">
                Детальный анализ с точными уровнями входа и выхода
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if "predictions" in st.session_state:
            predictions = st.session_state.predictions
            
            # Получаем текущую цену для расчетов
            current_price = data['Close'].iloc[-1]
            
            # Генерируем детальные торговые сигналы
            trading_signals = markov_chain.generate_trading_signals(predictions, current_price)
            
            # Отображаем детальные торговые рекомендации
            markov_chain.display_trading_signals(trading_signals)
            
            # Показываем общий анализ рынка
            market_summary = markov_chain.get_market_summary(trading_signals)
            display_market_summary(market_summary)

def analyze_trading_signals(predictions, markov_chain):
    """Анализ прогнозов для генерации торговых сигналов"""
    
    signals = []
    confidences = []
    
    for pred in predictions:
        state = pred['state']
        probability = pred['probability']
        
        # Парсим состояние
        parts = state.split('_')
        trend = parts[0] if len(parts) > 0 else 'T1'
        volatility = parts[1] if len(parts) > 1 else 'V1'
        rsi = parts[2] if len(parts) > 2 else 'R1'
        volume = parts[3] if len(parts) > 3 else 'O1'
        
        # Определяем сигнал
        signal = "НЕЙТРАЛЬНО"
        
        if trend == 'T2' and rsi == 'R0':  # Рост + перепроданность
            signal = "🟢 ПОКУПКА"
        elif trend == 'T0' and rsi == 'R2':  # Падение + перекупленность  
            signal = "🔴 ПРОДАЖА"
        elif trend == 'T2' and volume == 'O2':  # Рост + высокий объем
            signal = "🟢 ПОКУПКА"
        elif trend == 'T0' and volume == 'O2':  # Падение + высокий объем
            signal = "🔴 ПРОДАЖА"
        
        signals.append(signal)
        confidences.append(probability)
    
    # Общий сигнал
    buy_signals = sum(1 for s in signals if "ПОКУПКА" in s)
    sell_signals = sum(1 for s in signals if "ПРОДАЖА" in s)
    
    if buy_signals > sell_signals:
        overall_signal = "🟢 ПОКУПКА"
    elif sell_signals > buy_signals:
        overall_signal = "🔴 ПРОДАЖА"
    else:
        overall_signal = "⚪ НЕЙТРАЛЬНО"
    
    # Средняя уверенность
    avg_confidence = np.mean(confidences)
    
    # Временной горизонт (сколько шагов с высокой уверенностью)
    high_confidence_steps = sum(1 for c in confidences if c > 0.5)
    
    # Детальные рекомендации
    details = []
    for i, (signal, conf) in enumerate(zip(signals, confidences)):
        step = i + 1
        if signal != "НЕЙТРАЛЬНО":
            details.append({
                'step': f"Шаг {step}",
                'description': f"{signal} (уверенность: {conf:.1%})"
            })
    
    return {
        'signal': overall_signal,
        'confidence': avg_confidence,
        'timeframe': high_confidence_steps,
        'details': details
    }

def display_market_summary(market_summary: Dict):
    """Отображение общего анализа рынка"""
    
    # Красивый заголовок
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    ">
        <h3 style="color: white; margin: 0; font-size: 24px; font-weight: bold;">
            📊 Общий анализ рынка
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Основные метрики в темных карточках
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        trend_emoji = "🟢" if market_summary['overall_trend'] == 'BULLISH' else "🔴" if market_summary['overall_trend'] == 'BEARISH' else "⚪"
        if market_summary['overall_trend'] == 'BULLISH':
            trend_bg = "linear-gradient(135deg, #065f46 0%, #10b981 100%)"
            trend_border = "#10b981"
        elif market_summary['overall_trend'] == 'BEARISH':
            trend_bg = "linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%)"
            trend_border = "#ef4444"
        else:
            trend_bg = "linear-gradient(135deg, #374151 0%, #6b7280 100%)"
            trend_border = "#6b7280"
        
        st.markdown(f"""
        <div style="
            background: {trend_bg};
            border: 2px solid {trend_border};
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h4 style="margin: 0; font-size: 16px; color: #ffffff;">📈 Общий тренд</h4>
            <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #ffffff;">
                {trend_emoji} {market_summary['overall_trend']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if market_summary['trend_strength'] > 0.6:
            strength_bg = "linear-gradient(135deg, #065f46 0%, #10b981 100%)"
            strength_border = "#10b981"
        elif market_summary['trend_strength'] > 0.3:
            strength_bg = "linear-gradient(135deg, #92400e 0%, #f59e0b 100%)"
            strength_border = "#f59e0b"
        else:
            strength_bg = "linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%)"
            strength_border = "#ef4444"
        
        st.markdown(f"""
        <div style="
            background: {strength_bg};
            border: 2px solid {strength_border};
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h4 style="margin: 0; font-size: 16px; color: #ffffff;">💪 Сила тренда</h4>
            <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #ffffff;">
                {market_summary['trend_strength']:.1%}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            border: 2px solid #3b82f6;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h4 style="margin: 0; font-size: 16px; color: #ffffff;">📊 Всего сигналов</h4>
            <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #ffffff;">
                {market_summary['total_signals']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_conf = market_summary['high_confidence']
        if high_conf > market_summary['total_signals'] * 0.5:
            conf_bg = "linear-gradient(135deg, #065f46 0%, #10b981 100%)"
            conf_border = "#10b981"
        elif high_conf > 0:
            conf_bg = "linear-gradient(135deg, #92400e 0%, #f59e0b 100%)"
            conf_border = "#f59e0b"
        else:
            conf_bg = "linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%)"
            conf_border = "#ef4444"
        
        st.markdown(f"""
        <div style="
            background: {conf_bg};
            border: 2px solid {conf_border};
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h4 style="margin: 0; font-size: 16px; color: #ffffff;">🎯 Высокая уверенность</h4>
            <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #ffffff;">
                {high_conf}/{market_summary['total_signals']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Детальная статистика в темных карточках
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        border: 2px solid #4b5563;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    ">
        <h4 style="margin: 0 0 15px 0; color: #ffffff; text-align: center; font-size: 18px;">
            📈 Детальная статистика
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
            border: 2px solid #374151;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">📊 Сигналы по типам</h5>
            <p style="margin: 5px 0; color: #34d399; font-weight: bold; font-size: 14px;">
                🟢 Покупки: {market_summary['buy_signals']}
            </p>
            <p style="margin: 5px 0; color: #f87171; font-weight: bold; font-size: 14px;">
                🔴 Продажи: {market_summary['sell_signals']}
            </p>
            <p style="margin: 5px 0; color: #9ca3af; font-weight: bold; font-size: 14px;">
                ⚪ Нейтрально: {market_summary['neutral_signals']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
            border: 2px solid #374151;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">🎯 Уверенность сигналов</h5>
            <p style="margin: 5px 0; color: #34d399; font-weight: bold; font-size: 14px;">
                🟢 Высокая: {market_summary['high_confidence']}
            </p>
            <p style="margin: 5px 0; color: #fbbf24; font-weight: bold; font-size: 14px;">
                🟡 Средняя: {market_summary['medium_confidence']}
            </p>
            <p style="margin: 5px 0; color: #f87171; font-weight: bold; font-size: 14px;">
                🔴 Низкая: {market_summary['low_confidence']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Рекомендации на основе анализа
        if market_summary['overall_trend'] == 'BULLISH':
            rec_text = "📈 Рекомендация: Фокус на покупках"
            rec_color = "#34d399"
            rec_icon = "✅"
        elif market_summary['overall_trend'] == 'BEARISH':
            rec_text = "📉 Рекомендация: Фокус на продажах"
            rec_color = "#f87171"
            rec_icon = "⚠️"
        else:
            rec_text = "⚪ Рекомендация: Осторожная торговля"
            rec_color = "#9ca3af"
            rec_icon = "ℹ️"
        
        quality_text = "✅ Качество сигналов: Хорошее" if market_summary['high_confidence'] > market_summary['low_confidence'] else "⚠️ Качество сигналов: Смешанное"
        quality_color = "#34d399" if market_summary['high_confidence'] > market_summary['low_confidence'] else "#fbbf24"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
            border: 2px solid #374151;
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">💡 Рекомендации</h5>
            <p style="margin: 5px 0; color: {rec_color}; font-weight: bold; font-size: 14px;">
                {rec_icon} {rec_text}
            </p>
            <p style="margin: 5px 0; color: {quality_color}; font-weight: bold; font-size: 14px;">
                {quality_text}
            </p>
        </div>
        """, unsafe_allow_html=True)
