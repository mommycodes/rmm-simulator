"""
Упрощенный и понятный модуль анализа цепей Маркова для криптовалют
С фокусом на практическое применение в торговле
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from .markov_chain import CryptoMarkovChain
from .data_fetcher import CryptoDataFetcher

class SimplifiedMarkovAnalysis:
    """Упрощенный анализ цепей Маркова с понятными объяснениями"""
    
    def __init__(self):
        self.markov_chain = CryptoMarkovChain()
        self.data_fetcher = CryptoDataFetcher()
        self.current_price = None
        self.price_change_24h = None
        
    def render_simplified_interface(self):
        """Главный упрощенный интерфейс"""
        
        st.markdown("## 🧠 Анализ цепей Маркова")
        
        # Объяснение простыми словами
        st.info("""
        **🤔 Что это такое?**
        
        Пусть рынок криптовалют - это машина с состояниями:
        - 📈 **Рост** (цена идет вверх)
        - 📉 **Падение** (цена идет вниз) 
        - ➡️ **Боковик** (цена стоит на месте)
        
        Система изучает, как часто рынок переходит из одного состояния в другое,
        и предсказывает, что произойдет дальше.
        """)
        
        # Показываем сохраненные данные анализа, если они есть
        if "analysis_data" in st.session_state:
            st.markdown("### 📊 Результаты анализа")
            self._display_saved_analysis()
            st.markdown("---")
        
        # Выбор криптовалюты
        st.markdown("### 🪙 Выберите криптовалюту")
        
        crypto_options = self.data_fetcher.get_available_symbols()
        selected_crypto = st.selectbox(
            "Криптовалюта:",
            list(crypto_options.keys()),
            index=0
        )
        symbol = crypto_options[selected_crypto]
        
        # Показываем текущую цену
        self._show_current_price(symbol)
        
        # Кнопка анализа
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 Анализировать рынок", use_container_width=True):
                with st.spinner("Анализируем рынок..."):
                    self._run_analysis(symbol)
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Очистить все данные", use_container_width=True):
                # Очищаем все сохраненные данные
                keys_to_clear = [
                    "analysis_data", "analysis_states", "analysis_unique_states", 
                    "analysis_symbol", "predictions", "selected_state", "symbol"
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    def _show_current_price(self, symbol: str):
        """Показываем текущую цену для проверки точности данных"""
        try:
            # Получаем последние данные
            data = self.data_fetcher.fetch_data(symbol, "5d")
            if data is not None and len(data) > 0:
                current_price = data['Close'].iloc[-1]
                prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
                price_change = ((current_price - prev_price) / prev_price) * 100
                
                self.current_price = current_price
                self.price_change_24h = price_change
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Текущая цена", f"${current_price:,.2f}")
                with col2:
                    st.metric("📊 Изменение за день", f"{price_change:+.2f}%")
                with col3:
                    if price_change > 0:
                        st.metric("📈 Направление", "🟢 Рост")
                    elif price_change < 0:
                        st.metric("📉 Направление", "🔴 Падение")
                    else:
                        st.metric("➡️ Направление", "⚪ Боковик")
                
                st.success("✅ Данные актуальны! Можно анализировать.")
            else:
                st.error("❌ Не удалось получить данные")
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
    
    def _run_analysis(self, symbol: str):
        """Запуск анализа"""
        # Загружаем данные
        data = self.data_fetcher.fetch_data(symbol, "1y")
        
        if data is None or data.empty:
            st.error("❌ Не удалось загрузить данные")
            return
        
        # Определяем состояния
        states = self.markov_chain.define_states(data)
        unique_states = list(set(states.values()))
        
        # Строим матрицу переходов
        transition_matrix = self.markov_chain.build_transition_matrix(data)
        
        st.success(f"✅ Анализ завершен! Найдено {len(unique_states)} состояний рынка")
        
        # Сохраняем данные в session_state
        st.session_state.analysis_data = data
        st.session_state.analysis_states = states
        st.session_state.analysis_unique_states = unique_states
        st.session_state.analysis_symbol = symbol
        
        # Показываем результаты
        self._show_market_analysis(data, states, unique_states)
        self._show_trading_predictions(symbol, unique_states)
        self._show_wave_analysis(data)
    
    def _show_market_analysis(self, data: pd.DataFrame, states: Dict, unique_states: List[str]):
        """Показываем анализ рынка простыми словами"""
        
        st.markdown("---")
        st.markdown("### 📊 Анализ рынка")
        
        # Анализируем текущее состояние
        if len(data) > 0:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # Определяем текущее состояние
            current_state = self._get_current_state(data.iloc[-1])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Текущее состояние рынка")
                st.write(f"**Цена:** ${current_price:,.2f}")
                st.write(f"**Изменение:** {price_change:+.2f}%")
                st.write(f"**Состояние:** {self._explain_state(current_state)}")
            
            with col2:
                st.markdown("#### 📈 Статистика за год")
                total_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
                volatility = data['Close'].pct_change().std() * 100
                
                st.write(f"**Общее изменение:** {total_change:+.1f}%")
                st.write(f"**Волатильность:** {volatility:.1f}%")
                st.write(f"**Максимум:** ${data['High'].max():,.2f}")
                st.write(f"**Минимум:** ${data['Low'].min():,.2f}")
        
        # Показываем частоту состояний
        self._show_state_frequency(unique_states, states)
    
    def _get_current_state(self, last_row: pd.Series) -> str:
        """Определяем текущее состояние на основе последних данных"""
        # Простое определение состояния
        price_change = last_row['Close'] - last_row['Open']
        price_change_pct = (price_change / last_row['Open']) * 100
        
        if price_change_pct > 2:
            return "Рост"
        elif price_change_pct < -2:
            return "Падение"
        else:
            return "Боковик"
    
    def _explain_state(self, state: str) -> str:
        """Объясняем состояние простыми словами"""
        if state == "Рост":
            return "🟢 Рынок растет - покупатели сильнее продавцов"
        elif state == "Падение":
            return "🔴 Рынок падает - продавцы сильнее покупателей"
        else:
            return "⚪ Рынок в боковике - покупатели и продавцы в равновесии"
    
    def _show_state_frequency(self, unique_states: List[str], states: Dict):
        """Показываем частоту состояний"""
        st.markdown("#### 📊 Частота состояний рынка")
        
        # Считаем частоту
        state_counts = {}
        for state in states.values():
            state_counts[state] = state_counts.get(state, 0) + 1
        
        total = len(states)
        
        # Показываем топ-5 состояний
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
        
        st.write("**Самые частые состояния:**")
        for i, (state, count) in enumerate(sorted_states[:5]):
            percentage = (count / total) * 100
            st.write(f"{i+1}. {self._explain_state_simple(state)} - {percentage:.1f}% времени")
    
    def _explain_state_simple(self, state: str) -> str:
        """Простое объяснение состояния"""
        if "T2" in state:
            return "📈 Рост"
        elif "T0" in state:
            return "📉 Падение"
        else:
            return "➡️ Боковик"
    
    def _show_trading_predictions(self, symbol: str, unique_states: List[str]):
        """Показываем торговые прогнозы с подробными объяснениями"""
        
        st.markdown("---")
        st.markdown("### 🔮 Торговые прогнозы")
        
        st.info("""
        **🤔 Что означают прогнозы?**
        
        Система предсказывает, что произойдет с рынком в ближайшие дни:
        - **1 шаг** = завтра (следующий торговый день)
        - **2 шаг** = послезавтра
        - **3 шаг** = через 3 дня
        - И так далее...
        
        **Процент** показывает, насколько уверена система в прогнозе.
        """)
        
        # Показываем сохраненные прогнозы, если они есть
        if "predictions" in st.session_state and "selected_state" in st.session_state:
            st.markdown("#### 📊 Сохраненные прогнозы")
            self._display_saved_predictions()
            st.markdown("---")
        
        # Выбор состояния для прогноза
        if unique_states:
            selected_state = st.selectbox(
                "🎯 Выберите состояние для прогноза:",
                unique_states,
                help="Выберите состояние, из которого хотите сделать прогноз"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔮 Сделать прогноз", use_container_width=True):
                    self._generate_detailed_predictions(selected_state, symbol)
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Очистить прогнозы", use_container_width=True):
                    if "predictions" in st.session_state:
                        del st.session_state.predictions
                    if "selected_state" in st.session_state:
                        del st.session_state.selected_state
                    if "symbol" in st.session_state:
                        del st.session_state.symbol
                    st.rerun()
    
    def _generate_detailed_predictions(self, selected_state: str, symbol: str):
        """Генерируем детальные прогнозы с объяснениями"""
        
        # Получаем прогнозы
        predictions = self.markov_chain.predict_next_states(selected_state, 5)
        
        # Получаем текущую цену
        current_price = self._get_current_price(symbol)
        
        # Генерируем торговые сигналы
        trading_signals = self.markov_chain.generate_trading_signals(predictions, current_price)
        
        # Сохраняем в session_state
        st.session_state.predictions = predictions
        st.session_state.trading_signals = trading_signals
        st.session_state.selected_state = selected_state
        st.session_state.symbol = symbol
        
        st.markdown(f"#### 📊 Прогноз из состояния: {self._explain_state_simple(selected_state)}")
        
        # Показываем детальные торговые рекомендации
        self.markov_chain.display_trading_signals(trading_signals)
        
        # Показываем общий анализ рынка
        market_summary = self.markov_chain.get_market_summary(trading_signals)
        self._display_market_summary(market_summary)
    
    def _display_saved_predictions(self):
        """Отображаем сохраненные прогнозы"""
        predictions = st.session_state.predictions
        selected_state = st.session_state.selected_state
        symbol = st.session_state.symbol
        
        st.markdown(f"**Состояние:** {self._explain_state_simple(selected_state)}")
        st.markdown(f"**Криптовалюта:** {symbol}")
        
        # Показываем каждый прогноз
        for i, pred in enumerate(predictions):
            step = pred['step']
            state = pred['state']
            probability = pred['probability']
            
            # Определяем торговый сигнал
            signal = self._get_trading_signal(state)
            
            # Создаем карточку прогноза
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.markdown(f"**День {step}**")
                
                with col2:
                    st.markdown(f"**{self._explain_state_simple(state)}**")
                    st.markdown(f"Уверенность: {probability:.1%}")
                
                with col3:
                    st.markdown(f"**{signal['emoji']} {signal['action']}**")
                
                # Подробное объяснение
                st.markdown(f"**💡 Объяснение:** {signal['explanation']}")
                
                # Торговые рекомендации
                if signal['action'] != "НЕЙТРАЛЬНО":
                    self._show_trading_recommendations(step, signal, symbol)
                
                st.markdown("---")
    
    def _display_saved_analysis(self):
        """Отображаем сохраненные данные анализа"""
        data = st.session_state.analysis_data
        states = st.session_state.analysis_states
        unique_states = st.session_state.analysis_unique_states
        symbol = st.session_state.analysis_symbol
        
        st.markdown(f"**Криптовалюта:** {symbol}")
        st.markdown(f"**Найдено состояний:** {len(unique_states)}")
        
        # Показываем краткую статистику
        if len(data) > 0:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Текущая цена", f"${current_price:,.2f}")
            with col2:
                st.metric("📊 Изменение за день", f"{price_change:+.2f}%")
            with col3:
                if price_change > 0:
                    st.metric("📈 Направление", "🟢 Рост")
                elif price_change < 0:
                    st.metric("📉 Направление", "🔴 Падение")
                else:
                    st.metric("➡️ Направление", "⚪ Боковик")
        
        # Показываем частоту состояний
        state_counts = {}
        for state in states.values():
            state_counts[state] = state_counts.get(state, 0) + 1
        
        total = len(states)
        sorted_states = sorted(state_counts.items(), key=lambda x: x[1], reverse=True)
        
        st.markdown("**Самые частые состояния:**")
        for i, (state, count) in enumerate(sorted_states[:3]):
            percentage = (count / total) * 100
            st.write(f"{i+1}. {self._explain_state_simple(state)} - {percentage:.1f}% времени")
    
    def _get_trading_signal(self, state: str) -> Dict:
        """Определяем торговый сигнал на основе состояния"""
        parts = state.split('_')
        
        # Анализируем компоненты состояния
        trend = parts[0] if len(parts) > 0 else 'T1'
        volatility = parts[1] if len(parts) > 1 else 'V1'
        rsi = parts[2] if len(parts) > 2 else 'R1'
        volume = parts[3] if len(parts) > 3 else 'O1'
        
        # Определяем сигнал
        if trend == 'T2' and rsi == 'R0':  # Рост + перепроданность
            return {
                'action': 'ПОКУПКА',
                'emoji': '🟢',
                'explanation': 'Рынок растет, но RSI показывает перепроданность - хороший момент для входа',
                'strength': 'Сильный'
            }
        elif trend == 'T0' and rsi == 'R2':  # Падение + перекупленность
            return {
                'action': 'ПРОДАЖА',
                'emoji': '🔴',
                'explanation': 'Рынок падает, RSI показывает перекупленность - время закрывать позиции',
                'strength': 'Сильный'
            }
        elif trend == 'T2' and volume == 'O2':  # Рост + высокий объем
            return {
                'action': 'ПОКУПКА',
                'emoji': '🟢',
                'explanation': 'Рост с высоким объемом - сильный сигнал на покупку',
                'strength': 'Очень сильный'
            }
        elif trend == 'T0' and volume == 'O2':  # Падение + высокий объем
            return {
                'action': 'ПРОДАЖА',
                'emoji': '🔴',
                'explanation': 'Падение с высоким объемом - сильный сигнал на продажу',
                'strength': 'Очень сильный'
            }
        else:
            return {
                'action': 'НЕЙТРАЛЬНО',
                'emoji': '⚪',
                'explanation': 'Смешанные сигналы - лучше подождать более четких указаний',
                'strength': 'Слабый'
            }
    
    def _show_trading_recommendations(self, step: int, signal: Dict, symbol: str):
        """Показываем детальные торговые рекомендации"""
        
        if signal['action'] == 'НЕЙТРАЛЬНО':
            return
        
        st.markdown("#### 💰 Торговые рекомендации")
        
        # Получаем текущую цену для расчетов
        if self.current_price is None:
            st.warning("⚠️ Не удалось получить текущую цену для расчетов")
            return
        
        current_price = self.current_price
        
        # Рассчитываем уровни
        if signal['action'] == 'ПОКУПКА':
            # Для покупки
            entry_price = current_price
            stop_loss = current_price * 0.95  # -5% стоп-лосс
            take_profit_1 = current_price * 1.10  # +10% первый тейк-профит
            take_profit_2 = current_price * 1.20  # +20% второй тейк-профит
            
            st.markdown("**📈 Стратегия покупки:**")
            st.write(f"• **Вход:** ${entry_price:,.2f}")
            st.write(f"• **Стоп-лосс:** ${stop_loss:,.2f} (-5%)")
            st.write(f"• **Тейк-профит 1:** ${take_profit_1:,.2f} (+10%)")
            st.write(f"• **Тейк-профит 2:** ${take_profit_2:,.2f} (+20%)")
            st.write(f"• **Риск/Прибыль:** 1:2 (хорошее соотношение)")
            
        elif signal['action'] == 'ПРОДАЖА':
            # Для продажи
            entry_price = current_price
            stop_loss = current_price * 1.05  # +5% стоп-лосс
            take_profit_1 = current_price * 0.90  # -10% первый тейк-профит
            take_profit_2 = current_price * 0.80  # -20% второй тейк-профит
            
            st.markdown("**📉 Стратегия продажи:**")
            st.write(f"• **Вход:** ${entry_price:,.2f}")
            st.write(f"• **Стоп-лосс:** ${stop_loss:,.2f} (+5%)")
            st.write(f"• **Тейк-профит 1:** ${take_profit_1:,.2f} (-10%)")
            st.write(f"• **Тейк-профит 2:** ${take_profit_2:,.2f} (-20%)")
            st.write(f"• **Риск/Прибыль:** 1:2 (хорошее соотношение)")
        
        # Объяснение стратегии
        st.markdown("**🎯 Почему именно эти уровни?**")
        st.write("• **Стоп-лосс 5%** - защищает от больших потерь")
        st.write("• **Тейк-профит 10%** - консервативная цель")
        st.write("• **Тейк-профит 20%** - амбициозная цель")
        st.write("• **Соотношение 1:2** - риск меньше потенциальной прибыли")
        
        # Предупреждения
        st.warning("⚠️ **Важно помнить:**")
        st.write("• Это прогноз, а не гарантия")
        st.write("• Всегда используйте стоп-лосс")
        st.write("• Не рискуйте больше 2% от депозита")
        st.write("• Следите за новостями и фундаментальными факторами")
    
    def _show_wave_analysis(self, data: pd.DataFrame):
        """Показываем волновой анализ"""
        
        st.markdown("---")
        st.markdown("### 🌊 Волновой анализ")
        
        st.info("""
        **🌊 Что такое волновой анализ?**
        
        Рынок движется волнами - подъемы и спады. 
        Мы ищем паттерны, которые повторяются, чтобы предсказать следующее движение.
        """)
        
        # Простой волновой анализ
        if len(data) >= 50:
            # Ищем локальные максимумы и минимумы
            highs = data['High'].rolling(window=5, center=True).max() == data['High']
            lows = data['Low'].rolling(window=5, center=True).min() == data['Low']
            
            # Считаем волны
            wave_count = highs.sum() + lows.sum()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🌊 Количество волн", wave_count)
            
            with col2:
                avg_wave_length = len(data) / wave_count if wave_count > 0 else 0
                st.metric("📏 Средняя длина волны", f"{avg_wave_length:.1f} дней")
            
            with col3:
                # Определяем текущую фазу
                recent_data = data.tail(10)
                if recent_data['Close'].iloc[-1] > recent_data['Close'].iloc[0]:
                    phase = "📈 Восходящая волна"
                elif recent_data['Close'].iloc[-1] < recent_data['Close'].iloc[0]:
                    phase = "📉 Нисходящая волна"
                else:
                    phase = "➡️ Консолидация"
                
                st.metric("🎯 Текущая фаза", phase)
            
            # Простой график волн
            fig = go.Figure()
            
            # Цена
            fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Цена',
                line=dict(color='blue', width=2)
            ))
            
            # Локальные максимумы
            if highs.any():
                fig.add_trace(go.Scatter(
                    x=data[highs].index,
                    y=data[highs]['High'],
                    mode='markers',
                    name='Вершины волн',
                    marker=dict(color='red', size=8, symbol='triangle-up')
                ))
            
            # Локальные минимумы
            if lows.any():
                fig.add_trace(go.Scatter(
                    x=data[lows].index,
                    y=data[lows]['Low'],
                    mode='markers',
                    name='Основания волн',
                    marker=dict(color='green', size=8, symbol='triangle-down')
                ))
            
            fig.update_layout(
                title="Волновой анализ цены",
                xaxis_title="Дата",
                yaxis_title="Цена",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Объяснение волн
            st.markdown("#### 📚 Как читать волны:")
            st.write("• **🔴 Красные треугольники** - вершины волн (максимумы)")
            st.write("• **🟢 Зеленые треугольники** - основания волн (минимумы)")
            st.write("• **📈 Восходящие волны** - цена растет от основания к вершине")
            st.write("• **📉 Нисходящие волны** - цена падает от вершины к основанию")
            
            # Торговые советы на основе волн
            st.markdown("#### 💡 Торговые советы:")
            if phase == "📈 Восходящая волна":
                st.success("🟢 **Покупайте на откатах** - цена может вернуться к основанию волны")
            elif phase == "📉 Нисходящая волна":
                st.warning("🔴 **Продавайте на отскоках** - цена может вернуться к вершине волны")
            else:
                st.info("⚪ **Ждите пробоя** - цена консолидируется перед новым движением")
    
    def _get_current_price(self, symbol: str) -> float:
        """Получаем текущую цену"""
        try:
            # Пытаемся получить из сохраненных данных
            if 'analysis_data' in st.session_state:
                return st.session_state.analysis_data['Close'].iloc[-1]
            
            # Если нет, загружаем последние данные
            data = self.data_fetcher.fetch_data(symbol, "5d")
            if data is not None and not data.empty:
                return data['Close'].iloc[-1]
            
            # Fallback цена
            return 50000.0
        except:
            return 50000.0
    
    def _display_market_summary(self, market_summary: Dict):
        """Отображаем общий анализ рынка"""
        
        st.markdown("### 📊 Общий анализ рынка")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            trend_emoji = "🟢" if market_summary['overall_trend'] == 'BULLISH' else "🔴" if market_summary['overall_trend'] == 'BEARISH' else "⚪"
            st.metric("📈 Общий тренд", f"{trend_emoji} {market_summary['overall_trend']}")
        
        with col2:
            st.metric("💪 Сила тренда", f"{market_summary['trend_strength']:.1%}")
        
        with col3:
            st.metric("📊 Всего сигналов", market_summary['total_signals'])
        
        with col4:
            high_conf = market_summary['high_confidence']
            st.metric("🎯 Высокая уверенность", f"{high_conf}/{market_summary['total_signals']}")
        
        # Детальная статистика
        st.markdown("**📈 Детальная статистика:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"🟢 **Покупки:** {market_summary['buy_signals']}")
            st.markdown(f"🔴 **Продажи:** {market_summary['sell_signals']}")
            st.markdown(f"⚪ **Нейтрально:** {market_summary['neutral_signals']}")
        
        with col2:
            st.markdown(f"🟢 **Высокая уверенность:** {market_summary['high_confidence']}")
            st.markdown(f"🟡 **Средняя уверенность:** {market_summary['medium_confidence']}")
            st.markdown(f"🔴 **Низкая уверенность:** {market_summary['low_confidence']}")
        
        with col3:
            # Рекомендации на основе анализа
            if market_summary['overall_trend'] == 'BULLISH':
                st.success("**📈 Рекомендация:** Фокус на покупках")
            elif market_summary['overall_trend'] == 'BEARISH':
                st.error("**📉 Рекомендация:** Фокус на продажах")
            else:
                st.info("**⚪ Рекомендация:** Осторожная торговля")
            
            if market_summary['high_confidence'] > market_summary['low_confidence']:
                st.success("**✅ Качество сигналов:** Хорошее")
            else:
                st.warning("**⚠️ Качество сигналов:** Смешанное")
