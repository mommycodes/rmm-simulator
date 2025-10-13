import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from .data_fetcher import CryptoDataFetcher
import warnings
warnings.filterwarnings('ignore')

class CryptoMarkovChain:
    """
    Класс для анализа и прогнозирования движения криптовалют 
    с использованием цепей Маркова
    """
    
    def __init__(self):
        self.transition_matrix = None
        self.states = {}
        self.state_names = []
        self.current_state = None
        self.historical_data = None
        self.data_fetcher = CryptoDataFetcher()
        
    def fetch_crypto_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Получение исторических данных криптовалюты
        
        Args:
            symbol: Символ криптовалюты (например, 'BTC-USD')
            period: Период данных ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        
        Returns:
            DataFrame с историческими данными
        """
        return self.data_fetcher.fetch_data(symbol, period)
    
    
    def define_states(self, data: pd.DataFrame) -> Dict[str, int]:
        """
        Определение состояний на основе технических индикаторов
        
        Состояния:
        - Тренд: 0=Падение, 1=Боковик, 2=Рост
        - Волатильность: 0=Низкая, 1=Средняя, 2=Высокая
        - RSI: 0=Перепроданность (<20), 1=Нейтрально (20-79), 2=Перекупленность (>=80)
        - Объем: 0=Низкий, 1=Средний, 2=Высокий
        - MACD: 0=Медвежий, 1=Нейтральный, 2=Бычий
        - ADX: 0=Слабый тренд (<25), 1=Умеренный тренд (25-50), 2=Сильный тренд (>50)
        - Stochastic: 0=Перепроданность (<20), 1=Нейтрально (20-80), 2=Перекупленность (>80)
        """
        states = {}
        
        # Тренд (на основе изменения цены за 5 дней)
        price_change = data['Close'].pct_change(5)
        trend = np.where(price_change > 0.02, 2,  # Рост > 2%
                        np.where(price_change < -0.02, 0, 1))  # Падение < -2%, иначе боковик
        
        # Волатильность (на основе стандартного отклонения)
        vol_percentiles = data['Volatility'].quantile([0.33, 0.67])
        volatility = np.where(data['Volatility'] <= vol_percentiles[0.33], 0,  # Низкая
                             np.where(data['Volatility'] <= vol_percentiles[0.67], 1, 2))  # Средняя, иначе высокая
        
        # RSI
        rsi = np.where(data['RSI'] < 20, 0,  # Перепроданность
                      np.where(data['RSI'] >= 80, 2, 1))  # Перекупленность, иначе нейтрально
        
        # Объем
        vol_percentiles = data['Volume_Norm'].quantile([0.33, 0.67])
        volume = np.where(data['Volume_Norm'] <= vol_percentiles[0.33], 0,  # Низкий
                         np.where(data['Volume_Norm'] <= vol_percentiles[0.67], 1, 2))  # Средний, иначе высокий
        
        # MACD
        macd_signal = np.where(data['MACD'] > data['MACD_Signal'], 2,  # Бычий
                              np.where(data['MACD'] < data['MACD_Signal'], 0, 1))  # Медвежий, иначе нейтральный
        
        # ADX (сила тренда)
        adx = np.where(data['ADX'] < 25, 0,  # Слабый тренд
                      np.where(data['ADX'] <= 50, 1, 2))  # Умеренный, иначе сильный
        
        # Stochastic
        stoch = np.where(data['Stoch_K'] < 20, 0,  # Перепроданность
                        np.where(data['Stoch_K'] <= 80, 1, 2))  # Нейтрально, иначе перекупленность
        
        # Создаем комбинированные состояния
        for i in range(len(data)):
            if (pd.isna(trend[i]) or pd.isna(volatility[i]) or pd.isna(rsi[i]) or 
                pd.isna(volume[i]) or pd.isna(macd_signal[i]) or pd.isna(adx[i]) or pd.isna(stoch[i])):
                continue
                
            state_key = f"T{trend[i]}_V{volatility[i]}_R{rsi[i]}_O{volume[i]}_M{macd_signal[i]}_A{adx[i]}_S{stoch[i]}"
            states[data.index[i]] = state_key
        
        self.states = states
        self.state_names = sorted(list(set(states.values())))
        
        return states
    
    def build_transition_matrix(self, data: pd.DataFrame) -> np.ndarray:
        """
        Построение матрицы переходов между состояниями
        """
        if not self.states:
            self.define_states(data)
        
        n_states = len(self.state_names)
        transition_matrix = np.zeros((n_states, n_states))
        
        # Подсчет переходов
        state_sequence = list(self.states.values())
        
        for i in range(len(state_sequence) - 1):
            current_state = state_sequence[i]
            next_state = state_sequence[i + 1]
            
            current_idx = self.state_names.index(current_state)
            next_idx = self.state_names.index(next_state)
            
            transition_matrix[current_idx, next_idx] += 1
        
        # Нормализация (преобразование в вероятности)
        row_sums = transition_matrix.sum(axis=1)
        for i in range(n_states):
            if row_sums[i] > 0:
                transition_matrix[i] = transition_matrix[i] / row_sums[i]
        
        self.transition_matrix = transition_matrix
        return transition_matrix
    
    def predict_next_states(self, current_state: str, steps: int = 5) -> List[Dict]:
        """
        Прогнозирование следующих состояний
        
        Args:
            current_state: Текущее состояние
            steps: Количество шагов для прогноза
        
        Returns:
            Список словарей с прогнозами
        """
        if self.transition_matrix is None:
            raise ValueError("Матрица переходов не построена. Сначала вызовите build_transition_matrix()")
        
        if current_state not in self.state_names:
            raise ValueError(f"Состояние {current_state} не найдено в списке состояний")
        
        current_idx = self.state_names.index(current_state)
        predictions = []
        
        # Начальное распределение вероятностей (все в текущем состоянии)
        state_probs = np.zeros(len(self.state_names))
        state_probs[current_idx] = 1.0
        
        for step in range(1, steps + 1):
            # Умножение на матрицу переходов
            state_probs = state_probs @ self.transition_matrix
            
            # Находим наиболее вероятное состояние
            most_likely_idx = np.argmax(state_probs)
            most_likely_state = self.state_names[most_likely_idx]
            probability = state_probs[most_likely_idx]
            
            predictions.append({
                'step': step,
                'state': most_likely_state,
                'probability': probability,
                'all_probabilities': dict(zip(self.state_names, state_probs))
            })
        
        return predictions
    
    def get_state_description(self, state: str) -> str:
        """Получение описания состояния"""
        if not state:
            return "Неизвестно"
        
        parts = state.split('_')
        descriptions = []
        
        # Тренд
        trend_map = {'T0': 'Падение', 'T1': 'Боковик', 'T2': 'Рост'}
        if parts[0] in trend_map:
            descriptions.append(f"Тренд: {trend_map[parts[0]]}")
        
        # Волатильность
        vol_map = {'V0': 'Низкая', 'V1': 'Средняя', 'V2': 'Высокая'}
        if parts[1] in vol_map:
            descriptions.append(f"Волатильность: {vol_map[parts[1]]}")
        
        # RSI
        rsi_map = {'R0': 'Перепроданность (<20)', 'R1': 'Нейтрально (20-79)', 'R2': 'Перекупленность (>=80)'}
        if parts[2] in rsi_map:
            descriptions.append(f"RSI: {rsi_map[parts[2]]}")
        
        # Объем
        vol_map = {'O0': 'Низкий', 'O1': 'Средний', 'O2': 'Высокий'}
        if parts[3] in vol_map:
            descriptions.append(f"Объем: {vol_map[parts[3]]}")
        
        # MACD
        if len(parts) > 4:
            macd_map = {'M0': 'Медвежий', 'M1': 'Нейтральный', 'M2': 'Бычий'}
            if parts[4] in macd_map:
                descriptions.append(f"MACD: {macd_map[parts[4]]}")
        
        # ADX
        if len(parts) > 5:
            adx_map = {'A0': 'Слабый тренд', 'A1': 'Умеренный тренд', 'A2': 'Сильный тренд'}
            if parts[5] in adx_map:
                descriptions.append(f"ADX: {adx_map[parts[5]]}")
        
        # Stochastic
        if len(parts) > 6:
            stoch_map = {'S0': 'Перепроданность', 'S1': 'Нейтрально', 'S2': 'Перекупленность'}
            if parts[6] in stoch_map:
                descriptions.append(f"Stochastic: {stoch_map[parts[6]]}")
        
        return " | ".join(descriptions)
    
    def get_compact_state_description(self, state: str) -> str:
        """Получение компактного описания состояния для темной темы"""
        if not state:
            return "Неизвестно"
        
        parts = state.split('_')
        
        # Тренд с эмодзи
        trend_map = {'T0': '📉 Падение', 'T1': '➡️ Боковик', 'T2': '📈 Рост'}
        trend = trend_map.get(parts[0], '❓')
        
        # RSI с эмодзи
        rsi_map = {'R0': '🔴 Перепроданность', 'R1': '⚪ Нейтрально', 'R2': '🟢 Перекупленность'}
        rsi = rsi_map.get(parts[2], '❓')
        
        # MACD с эмодзи
        macd_map = {'M0': '🔴 Медвежий', 'M1': '⚪ Нейтральный', 'M2': '🟢 Бычий'}
        macd = macd_map.get(parts[4] if len(parts) > 4 else 'M1', '❓')
        
        # Объем с эмодзи
        vol_map = {'O0': '📉 Низкий', 'O1': '📊 Средний', 'O2': '📈 Высокий'}
        volume = vol_map.get(parts[3], '❓')
        
        return f"{trend} • {rsi} • {macd} • {volume}"
    
    def analyze_state_frequency(self) -> pd.DataFrame:
        """Анализ частоты состояний"""
        if not self.states:
            return pd.DataFrame()
        
        state_counts = {}
        for state in self.states.values():
            state_counts[state] = state_counts.get(state, 0) + 1
        
        total_states = len(self.states)
        frequency_data = []
        
        for state, count in state_counts.items():
            frequency_data.append({
                'Состояние': state,
                'Описание': self.get_state_description(state),
                'Количество': count,
                'Частота (%)': (count / total_states) * 100
            })
        
        return pd.DataFrame(frequency_data).sort_values('Частота (%)', ascending=False)
    
    def plot_transition_heatmap(self):
        """Визуализация матрицы переходов"""
        if self.transition_matrix is None:
            st.error("Матрица переходов не построена")
            return
        
        fig = go.Figure(data=go.Heatmap(
            z=self.transition_matrix,
            x=self.state_names,
            y=self.state_names,
            colorscale='Blues',
            hoverongaps=False,
            text=np.round(self.transition_matrix, 3),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Матрица переходов между состояниями",
            xaxis_title="Следующее состояние",
            yaxis_title="Текущее состояние",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_state_frequency(self):
        """Визуализация частоты состояний"""
        freq_data = self.analyze_state_frequency()
        
        if freq_data.empty:
            st.error("Нет данных о частоте состояний")
            return
        
        fig = px.bar(
            freq_data, 
            x='Частота (%)', 
            y='Состояние',
            orientation='h',
            title="Частота встречаемости состояний",
            hover_data=['Описание', 'Количество']
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_prediction_confidence(self, predictions: List[Dict]):
        """Визуализация уверенности в прогнозах"""
        steps = [p['step'] for p in predictions]
        probabilities = [p['probability'] for p in predictions]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=steps,
            y=probabilities,
            mode='lines+markers',
            name='Вероятность',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Уверенность в прогнозах по шагам",
            xaxis_title="Шаг прогноза",
            yaxis_title="Вероятность (%)",
            yaxis=dict(tickformat='.1%'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def generate_trading_signals(self, predictions: List[Dict], current_price: float) -> List[Dict]:
        """
        Генерация торговых сигналов на основе прогнозов
        
        Args:
            predictions: Список прогнозов
            current_price: Текущая цена
        
        Returns:
            Список торговых сигналов с детальными рекомендациями
        """
        trading_signals = []
        
        for pred in predictions:
            state = pred['state']
            probability = pred['probability']
            step = pred['step']
            
            # Анализируем состояние для определения сигнала
            signal_analysis = self._analyze_state_for_trading(state, probability)
            
            # Генерируем торговые рекомендации
            trading_plan = self._generate_trading_plan(
                state, probability, step, current_price, signal_analysis
            )
            
            trading_signals.append({
                'step': step,
                'state': state,
                'probability': probability,
                'signal': signal_analysis['signal'],
                'confidence': signal_analysis['confidence'],
                'reasoning': signal_analysis['reasoning'],
                'trading_plan': trading_plan
            })
        
        return trading_signals
    
    def _analyze_state_for_trading(self, state: str, probability: float) -> Dict:
        """Анализ состояния для торговых решений"""
        
        parts = state.split('_')
        if len(parts) < 4:
            return {
                'signal': 'NEUTRAL',
                'confidence': 'LOW',
                'reasoning': 'Неизвестное состояние'
            }
        
        trend = parts[0]  # T0, T1, T2
        volatility = parts[1]  # V0, V1, V2
        rsi = parts[2]  # R0, R1, R2
        volume = parts[3]  # O0, O1, O2
        macd = parts[4] if len(parts) > 4 else 'M1'  # M0, M1, M2
        adx = parts[5] if len(parts) > 5 else 'A1'  # A0, A1, A2
        stoch = parts[6] if len(parts) > 6 else 'S1'  # S0, S1, S2
        
        # Определяем основной сигнал по тренду
        if trend == 'T2':  # Рост
            base_signal = 'BUY'
            base_reasoning = "Тренд восходящий"
        elif trend == 'T0':  # Падение
            base_signal = 'SELL'
            base_reasoning = "Тренд нисходящий"
        else:  # T1 - Боковик
            base_signal = 'NEUTRAL'
            base_reasoning = "Тренд боковой"
        
        # Корректируем сигнал на основе RSI
        if rsi == 'R0':  # Перепроданность
            if base_signal == 'SELL':
                base_signal = 'BUY'  # Разворот вверх
                base_reasoning += " + RSI перепроданность (разворот)"
            elif base_signal == 'NEUTRAL':
                base_signal = 'BUY'
                base_reasoning += " + RSI перепроданность"
        elif rsi == 'R2':  # Перекупленность
            if base_signal == 'BUY':
                base_signal = 'SELL'  # Разворот вниз
                base_reasoning += " + RSI перекупленность (разворот)"
            elif base_signal == 'NEUTRAL':
                base_signal = 'SELL'
                base_reasoning += " + RSI перекупленность"
        
        # Корректируем на основе объема
        if volume == 'O2':  # Высокий объем
            base_reasoning += " + Высокий объем (подтверждение)"
        elif volume == 'O0':  # Низкий объем
            base_reasoning += " + Низкий объем (слабое подтверждение)"
        
        # Корректируем на основе волатильности
        if volatility == 'V2':  # Высокая волатильность
            base_reasoning += " + Высокая волатильность (осторожно)"
        elif volatility == 'V0':  # Низкая волатильность
            base_reasoning += " + Низкая волатильность (стабильно)"
        
        # Корректируем на основе MACD
        if macd == 'M2':  # Бычий MACD
            if base_signal == 'BUY':
                base_reasoning += " + MACD бычий (подтверждение)"
            elif base_signal == 'SELL':
                base_signal = 'NEUTRAL'  # Противоречие
                base_reasoning += " + MACD бычий (противоречие)"
        elif macd == 'M0':  # Медвежий MACD
            if base_signal == 'SELL':
                base_reasoning += " + MACD медвежий (подтверждение)"
            elif base_signal == 'BUY':
                base_signal = 'NEUTRAL'  # Противоречие
                base_reasoning += " + MACD медвежий (противоречие)"
        
        # Корректируем на основе ADX (сила тренда)
        if adx == 'A2':  # Сильный тренд
            base_reasoning += " + Сильный тренд (надежный сигнал)"
        elif adx == 'A0':  # Слабый тренд
            base_reasoning += " + Слабый тренд (ненадежный сигнал)"
            if base_signal != 'NEUTRAL':
                base_signal = 'NEUTRAL'  # Слабый тренд = нейтрально
        
        # Корректируем на основе Stochastic
        if stoch == 'S0':  # Перепроданность
            if base_signal == 'SELL':
                base_signal = 'BUY'  # Разворот вверх
                base_reasoning += " + Stochastic перепроданность (разворот)"
            elif base_signal == 'NEUTRAL':
                base_signal = 'BUY'
                base_reasoning += " + Stochastic перепроданность"
        elif stoch == 'S2':  # Перекупленность
            if base_signal == 'BUY':
                base_signal = 'SELL'  # Разворот вниз
                base_reasoning += " + Stochastic перекупленность (разворот)"
            elif base_signal == 'NEUTRAL':
                base_signal = 'SELL'
                base_reasoning += " + Stochastic перекупленность"
        
        # Определяем уверенность на основе всех факторов
        confidence_factors = 0
        total_factors = 0
        
        # Тренд
        if trend in ['T0', 'T2']:
            confidence_factors += 1
        total_factors += 1
        
        # RSI
        if rsi in ['R0', 'R2']:
            confidence_factors += 1
        total_factors += 1
        
        # MACD
        if macd in ['M0', 'M2']:
            confidence_factors += 1
        total_factors += 1
        
        # ADX
        if adx == 'A2':
            confidence_factors += 1
        total_factors += 1
        
        # Stochastic
        if stoch in ['S0', 'S2']:
            confidence_factors += 1
        total_factors += 1
        
        # Объем
        if volume == 'O2':
            confidence_factors += 1
        total_factors += 1
        
        # Определяем уверенность
        factor_ratio = confidence_factors / total_factors if total_factors > 0 else 0
        combined_confidence = (probability + factor_ratio) / 2
        
        if combined_confidence > 0.7:
            confidence = 'HIGH'
        elif combined_confidence > 0.5:
            confidence = 'MEDIUM'
        else:
            confidence = 'LOW'
        
        return {
            'signal': base_signal,
            'confidence': confidence,
            'reasoning': base_reasoning
        }
    
    def _generate_trading_plan(self, state: str, probability: float, step: int, 
                              current_price: float, signal_analysis: Dict) -> Dict:
        """Генерация детального торгового плана"""
        
        signal = signal_analysis['signal']
        confidence = signal_analysis['confidence']
        
        # Базовые уровни риска
        risk_percent = 0.02  # 2% риска
        reward_risk_ratio = 2.0  # Соотношение прибыль/риск 2:1
        
        if signal == 'BUY':
            entry_price = current_price
            stop_loss = current_price * (1 - risk_percent)
            take_profit_1 = current_price * (1 + risk_percent * reward_risk_ratio)
            take_profit_2 = current_price * (1 + risk_percent * reward_risk_ratio * 1.5)
            
            # Корректируем уровни в зависимости от уверенности
            if confidence == 'HIGH':
                risk_percent = 0.03  # Больше риска при высокой уверенности
                reward_risk_ratio = 2.5
            elif confidence == 'LOW':
                risk_percent = 0.015  # Меньше риска при низкой уверенности
                reward_risk_ratio = 1.5
            
            # Пересчитываем с учетом корректировки
            stop_loss = current_price * (1 - risk_percent)
            take_profit_1 = current_price * (1 + risk_percent * reward_risk_ratio)
            take_profit_2 = current_price * (1 + risk_percent * reward_risk_ratio * 1.5)
            
            strategy = {
                'action': 'ПОКУПКА',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'risk_percent': risk_percent * 100,
                'reward_risk_ratio': reward_risk_ratio,
                'position_size': f"2-5% от депозита",
                'timeframe': f"{step} торговых дней",
                'risk_level': confidence
            }
            
        elif signal == 'SELL':
            entry_price = current_price
            stop_loss = current_price * (1 + risk_percent)
            take_profit_1 = current_price * (1 - risk_percent * reward_risk_ratio)
            take_profit_2 = current_price * (1 - risk_percent * reward_risk_ratio * 1.5)
            
            # Корректируем уровни в зависимости от уверенности
            if confidence == 'HIGH':
                risk_percent = 0.03
                reward_risk_ratio = 2.5
            elif confidence == 'LOW':
                risk_percent = 0.015
                reward_risk_ratio = 1.5
            
            # Пересчитываем с учетом корректировки
            stop_loss = current_price * (1 + risk_percent)
            take_profit_1 = current_price * (1 - risk_percent * reward_risk_ratio)
            take_profit_2 = current_price * (1 - risk_percent * reward_risk_ratio * 1.5)
            
            strategy = {
                'action': 'ПРОДАЖА',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'risk_percent': risk_percent * 100,
                'reward_risk_ratio': reward_risk_ratio,
                'position_size': f"2-5% от депозита",
                'timeframe': f"{step} торговых дней",
                'risk_level': confidence
            }
            
        else:  # NEUTRAL
            strategy = {
                'action': 'НЕЙТРАЛЬНО',
                'entry_price': current_price,
                'stop_loss': None,
                'take_profit_1': None,
                'take_profit_2': None,
                'risk_percent': 0,
                'reward_risk_ratio': 0,
                'position_size': "Не торговать",
                'timeframe': f"{step} торговых дней",
                'risk_level': confidence
            }
        
        return strategy
    
    def display_trading_signals(self, trading_signals: List[Dict]):
        """Отображение торговых сигналов с детальными рекомендациями"""
        
        for signal in trading_signals:
            step = signal['step']
            state = signal['state']
            probability = signal['probability']
            signal_type = signal['signal']
            confidence = signal['confidence']
            reasoning = signal['reasoning']
            plan = signal['trading_plan']
            
            # Красивая карточка сигнала
            if signal_type == 'BUY':
                card_color = "#d4edda"
                border_color = "#28a745"
                text_color = "#155724"
                signal_emoji = "🟢"
            elif signal_type == 'SELL':
                card_color = "#f8d7da"
                border_color = "#dc3545"
                text_color = "#721c24"
                signal_emoji = "🔴"
            else:
                card_color = "#e2e3e5"
                border_color = "#6c757d"
                text_color = "#495057"
                signal_emoji = "⚪"
            
            # Заголовок карточки с темными цветами
            if signal_type == 'BUY':
                card_bg = "linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)"
                text_color = "#ffffff"
                border_color = "#3b82f6"
            elif signal_type == 'SELL':
                card_bg = "linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%)"
                text_color = "#ffffff"
                border_color = "#ef4444"
            else:
                card_bg = "linear-gradient(135deg, #374151 0%, #4b5563 100%)"
                text_color = "#ffffff"
                border_color = "#6b7280"
            
            st.markdown(f"""
            <div style="
                background: {card_bg};
                border: 3px solid {border_color};
                border-radius: 12px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            ">
                <h3 style="margin: 0; color: {text_color}; text-align: center; font-size: 24px; font-weight: bold;">
                    {signal_emoji} День {step} - {signal_type}
                </h3>
                <p style="margin: 10px 0 0 0; color: {text_color}; text-align: center; font-size: 16px; opacity: 0.9;">
                    {self.get_compact_state_description(state)}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Основные метрики в компактном виде
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                confidence_emoji = "🟢" if confidence == 'HIGH' else "🟡" if confidence == 'MEDIUM' else "🔴"
                confidence_color = "#10b981" if confidence == 'HIGH' else "#f59e0b" if confidence == 'MEDIUM' else "#ef4444"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    border: 2px solid {confidence_color};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">
                    <h4 style="margin: 0; color: #ffffff; font-size: 14px;">📈 Уверенность</h4>
                    <p style="margin: 5px 0 0 0; color: {confidence_color}; font-size: 20px; font-weight: bold;">
                        {probability:.1%}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                quality_color = "#10b981" if confidence == 'HIGH' else "#f59e0b" if confidence == 'MEDIUM' else "#ef4444"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    border: 2px solid {quality_color};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">
                    <h4 style="margin: 0; color: #ffffff; font-size: 14px;">⚡ Качество</h4>
                    <p style="margin: 5px 0 0 0; color: {quality_color}; font-size: 18px; font-weight: bold;">
                        {confidence_emoji} {confidence}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    border: 2px solid #6366f1;
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">
                    <h4 style="margin: 0; color: #ffffff; font-size: 14px;">⏰ Срок</h4>
                    <p style="margin: 5px 0 0 0; color: #6366f1; font-size: 20px; font-weight: bold;">
                        {step} дней
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                risk_color = "#10b981" if plan['risk_percent'] < 3 else "#f59e0b" if plan['risk_percent'] < 5 else "#ef4444"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    border: 2px solid {risk_color};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    margin: 5px 0;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">
                    <h4 style="margin: 0; color: #ffffff; font-size: 14px;">📊 Риск</h4>
                    <p style="margin: 5px 0 0 0; color: {risk_color}; font-size: 20px; font-weight: bold;">
                        {plan['risk_percent']:.1f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Торговый план (только если не нейтрально)
            if plan['action'] != 'НЕЙТРАЛЬНО':
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    border: 2px solid #4b5563;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 15px 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                ">
                    <h4 style="margin: 0 0 15px 0; color: #ffffff; text-align: center; font-size: 18px;">
                        📋 Торговый план
                    </h4>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                        border: 2px solid #374151;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    ">
                        <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">💰 Уровни входа и выхода</h5>
                        <p style="margin: 5px 0; color: #60a5fa; font-weight: bold; font-size: 14px;">
                            🎯 Вход: ${plan['entry_price']:,.2f}
                        </p>
                        <p style="margin: 5px 0; color: #f87171; font-weight: bold; font-size: 14px;">
                            🛑 Стоп-лосс: ${plan['stop_loss']:,.2f}
                        </p>
                        <p style="margin: 5px 0; color: #34d399; font-weight: bold; font-size: 14px;">
                            🎯 Тейк-профит 1: ${plan['take_profit_1']:,.2f}
                        </p>
                        <p style="margin: 5px 0; color: #34d399; font-weight: bold; font-size: 14px;">
                            🎯 Тейк-профит 2: ${plan['take_profit_2']:,.2f}
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
                        margin: 10px 0;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    ">
                        <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">📊 Параметры сделки</h5>
                        <p style="margin: 5px 0; color: #a78bfa; font-weight: bold; font-size: 14px;">
                            ⚖️ Соотношение: 1:{plan['reward_risk_ratio']:.1f}
                        </p>
                        <p style="margin: 5px 0; color: #fbbf24; font-weight: bold; font-size: 14px;">
                            💼 Размер: {plan['position_size']}
                        </p>
                        <p style="margin: 5px 0; color: #60a5fa; font-weight: bold; font-size: 14px;">
                            ⏰ Горизонт: {plan['timeframe']}
                        </p>
                        <p style="margin: 5px 0; color: #f87171; font-weight: bold; font-size: 14px;">
                            🎯 Риск: {plan['risk_level']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Краткие рекомендации
                self._show_simple_recommendations(plan, step, confidence)
                
            else:
                st.markdown("""
                <div style="
                    background: #e2e3e5;
                    border: 2px solid #6c757d;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 15px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #495057;">⚪ НЕЙТРАЛЬНО</h4>
                    <p style="margin: 10px 0 0 0; color: #495057;">
                        Рекомендуется не торговать в этом направлении
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def _show_simple_recommendations(self, plan: Dict, step: int, confidence: str):
        """Показывает упрощенные рекомендации"""
        
        # Определяем цвет и текст для рекомендаций
        if confidence == 'HIGH':
            rec_color = "#28a745"
            rec_text = "✅ Высокая уверенность - можно увеличить размер позиции"
        elif confidence == 'MEDIUM':
            rec_color = "#ffc107"
            rec_text = "⚠️ Средняя уверенность - используйте стандартный размер"
        else:
            rec_color = "#dc3545"
            rec_text = "❌ Низкая уверенность - уменьшите размер позиции"
        
        # Определяем тип сигнала
        if step == 1:
            time_text = "⚡ Краткосрочный - для скальпинга"
        elif step <= 3:
            time_text = "📊 Среднесрочный - для свинг-торговли"
        else:
            time_text = "📈 Долгосрочный - для позиционной торговли"
        
        # Краткие рекомендации в одной карточке для темной темы
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
            border: 2px solid #374151;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            <h5 style="margin: 0 0 10px 0; color: #ffffff; font-size: 16px;">💡 Рекомендации</h5>
            <p style="margin: 5px 0; color: {rec_color}; font-weight: bold; font-size: 14px;">
                {rec_text}
            </p>
            <p style="margin: 5px 0; color: #60a5fa; font-weight: bold; font-size: 14px;">
                {time_text}
            </p>
            <p style="margin: 5px 0; color: #a78bfa; font-size: 14px;">
                🎯 Вход: {'Покупайте на откатах' if plan['action'] == 'ПОКУПКА' else 'Продавайте на отскоках'}
            </p>
            <p style="margin: 5px 0; color: #34d399; font-size: 14px;">
                📊 Выход: Закройте 50% на первой цели, остальное с трейлингом
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _show_additional_recommendations(self, plan: Dict, step: int, confidence: str):
        """Показывает дополнительные рекомендации"""
        
        st.markdown("**🔍 Дополнительные рекомендации:**")
        
        # Рекомендации по управлению рисками
        if confidence == 'HIGH':
            st.success("✅ **Высокая уверенность** - можно увеличить размер позиции до 5% от депозита")
        elif confidence == 'MEDIUM':
            st.warning("⚠️ **Средняя уверенность** - используйте стандартный размер позиции 2-3%")
        else:
            st.error("❌ **Низкая уверенность** - уменьшите размер позиции до 1-2% или не торгуйте")
        
        # Рекомендации по времени
        if step == 1:
            st.info("⚡ **Краткосрочный сигнал** - подходит для скальпинга и внутридневной торговли")
        elif step <= 3:
            st.info("📊 **Среднесрочный сигнал** - подходит для свинг-торговли")
        else:
            st.info("📈 **Долгосрочный сигнал** - подходит для позиционной торговли")
        
        # Рекомендации по входу
        if plan['action'] == 'ПОКУПКА':
            st.markdown("• **Вход:** Покупайте на откатах к поддержке")
            st.markdown("• **Подтверждение:** Дождитесь пробоя сопротивления")
            st.markdown("• **Стоп-лосс:** Разместите ниже локального минимума")
        else:
            st.markdown("• **Вход:** Продавайте на отскоках к сопротивлению")
            st.markdown("• **Подтверждение:** Дождитесь пробоя поддержки")
            st.markdown("• **Стоп-лосс:** Разместите выше локального максимума")
        
        # Рекомендации по выходу
        st.markdown("• **Тейк-профит 1:** Закройте 50% позиции при достижении первой цели")
        st.markdown("• **Тейк-профит 2:** Переместите стоп-лосс в безубыток при достижении первой цели")
        st.markdown("• **Трейлинг:** Используйте трейлинг-стоп для максимизации прибыли")
    
    def get_market_summary(self, trading_signals: List[Dict]) -> Dict:
        """Получение общего анализа рынка"""
        
        if not trading_signals:
            return {'summary': 'Нет данных для анализа'}
        
        # Анализируем общий тренд
        buy_signals = [s for s in trading_signals if s['signal'] == 'BUY']
        sell_signals = [s for s in trading_signals if s['signal'] == 'SELL']
        neutral_signals = [s for s in trading_signals if s['signal'] == 'NEUTRAL']
        
        total_signals = len(trading_signals)
        
        # Определяем общий тренд
        if len(buy_signals) > len(sell_signals):
            overall_trend = 'BULLISH'
            trend_strength = len(buy_signals) / total_signals
        elif len(sell_signals) > len(buy_signals):
            overall_trend = 'BEARISH'
            trend_strength = len(sell_signals) / total_signals
        else:
            overall_trend = 'SIDEWAYS'
            trend_strength = len(neutral_signals) / total_signals
        
        # Анализируем уверенность
        high_confidence = [s for s in trading_signals if s['confidence'] == 'HIGH']
        medium_confidence = [s for s in trading_signals if s['confidence'] == 'MEDIUM']
        low_confidence = [s for s in trading_signals if s['confidence'] == 'LOW']
        
        return {
            'overall_trend': overall_trend,
            'trend_strength': trend_strength,
            'total_signals': total_signals,
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'neutral_signals': len(neutral_signals),
            'high_confidence': len(high_confidence),
            'medium_confidence': len(medium_confidence),
            'low_confidence': len(low_confidence),
            'summary': f"Общий тренд: {overall_trend}, Сила: {trend_strength:.1%}"
        }
