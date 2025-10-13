"""
Расширенные методы анализа цепей Маркова для криптовалют
Включает анализ стационарности, эргодичности и другие продвинутые методы
"""
import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
import plotly.express as px
from markov_chain import CryptoMarkovChain

class AdvancedMarkovAnalysis:
    """Расширенный анализ цепей Маркова"""
    
    def __init__(self, markov_chain: CryptoMarkovChain):
        self.markov_chain = markov_chain
        self.stationary_distribution = None
        self.absorption_states = None
        self.communication_classes = None
    
    def analyze_stationarity(self) -> Dict:
        """
        Анализ стационарности цепи Маркова
        
        Returns:
            Словарь с результатами анализа стационарности
        """
        if self.markov_chain.transition_matrix is None:
            raise ValueError("Матрица переходов не построена")
        
        P = self.markov_chain.transition_matrix
        
        # Находим стационарное распределение (левые собственные векторы)
        eigenvalues, eigenvectors = np.linalg.eig(P.T)
        
        # Находим собственный вектор с собственным значением 1
        stationary_idx = np.argmin(np.abs(eigenvalues - 1.0))
        stationary_vector = np.real(eigenvectors[:, stationary_idx])
        stationary_vector = np.abs(stationary_vector)  # Берем модуль
        stationary_vector = stationary_vector / np.sum(stationary_vector)  # Нормализуем
        
        self.stationary_distribution = stationary_vector
        
        # Проверяем, является ли распределение стационарным
        # (P^T * pi = pi)
        is_stationary = np.allclose(P.T @ stationary_vector, stationary_vector, atol=1e-10)
        
        # Энтропия стационарного распределения
        entropy = -np.sum(stationary_vector * np.log(stationary_vector + 1e-10))
        
        return {
            'is_stationary': is_stationary,
            'stationary_distribution': stationary_vector,
            'entropy': entropy,
            'max_probability_state': self.markov_chain.state_names[np.argmax(stationary_vector)],
            'min_probability_state': self.markov_chain.state_names[np.argmin(stationary_vector)]
        }
    
    def find_absorption_states(self) -> List[int]:
        """
        Поиск поглощающих состояний
        
        Returns:
            Список индексов поглощающих состояний
        """
        if self.markov_chain.transition_matrix is None:
            raise ValueError("Матрица переходов не построена")
        
        P = self.markov_chain.transition_matrix
        absorption_states = []
        
        for i in range(len(P)):
            if P[i, i] == 1.0:  # Состояние поглощающее, если вероятность остаться в нем = 1
                absorption_states.append(i)
        
        self.absorption_states = absorption_states
        return absorption_states
    
    def find_communication_classes(self) -> List[List[int]]:
        """
        Поиск классов сообщающихся состояний
        
        Returns:
            Список классов сообщающихся состояний
        """
        if self.markov_chain.transition_matrix is None:
            raise ValueError("Матрица переходов не построена")
        
        P = self.markov_chain.transition_matrix
        n = len(P)
        visited = [False] * n
        classes = []
        
        def dfs(node, current_class):
            visited[node] = True
            current_class.append(node)
            
            for neighbor in range(n):
                if not visited[neighbor] and (P[node, neighbor] > 0 or P[neighbor, node] > 0):
                    dfs(neighbor, current_class)
        
        for i in range(n):
            if not visited[i]:
                current_class = []
                dfs(i, current_class)
                classes.append(current_class)
        
        self.communication_classes = classes
        return classes
    
    def calculate_hitting_times(self, target_states: List[int]) -> np.ndarray:
        """
        Расчет времени достижения целевых состояний
        
        Args:
            target_states: Список индексов целевых состояний
        
        Returns:
            Массив средних времен достижения для каждого состояния
        """
        if self.markov_chain.transition_matrix is None:
            raise ValueError("Матрица переходов не построена")
        
        P = self.markov_chain.transition_matrix
        n = len(P)
        
        # Создаем матрицу для решения системы уравнений
        A = np.eye(n) - P
        b = np.ones(n)
        
        # Для целевых состояний время достижения = 0
        for state in target_states:
            A[state, :] = 0
            A[state, state] = 1
            b[state] = 0
        
        try:
            hitting_times = np.linalg.solve(A, b)
            return hitting_times
        except np.linalg.LinAlgError:
            # Если система не имеет решения, используем итеративный метод
            hitting_times = np.zeros(n)
            for _ in range(1000):  # Максимум 1000 итераций
                new_times = np.ones(n)
                for i in range(n):
                    if i not in target_states:
                        new_times[i] = 1 + np.sum(P[i, :] * hitting_times)
                if np.allclose(hitting_times, new_times, atol=1e-6):
                    break
                hitting_times = new_times
            return hitting_times
    
    def calculate_expected_return_times(self) -> np.ndarray:
        """
        Расчет ожидаемых времен возврата в каждое состояние
        
        Returns:
            Массив ожидаемых времен возврата
        """
        if self.stationary_distribution is None:
            self.analyze_stationarity()
        
        return 1.0 / (self.stationary_distribution + 1e-10)
    
    def plot_stationary_distribution(self):
        """Визуализация стационарного распределения"""
        if self.stationary_distribution is None:
            self.analyze_stationarity()
        
        fig = px.bar(
            x=self.markov_chain.state_names,
            y=self.stationary_distribution,
            title="Стационарное распределение состояний",
            labels={'x': 'Состояние', 'y': 'Вероятность'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_hitting_times(self, target_states: List[int]):
        """Визуализация времен достижения"""
        hitting_times = self.calculate_hitting_times(target_states)
        
        fig = px.bar(
            x=self.markov_chain.state_names,
            y=hitting_times,
            title=f"Время достижения состояний {[self.markov_chain.state_names[i] for i in target_states]}",
            labels={'x': 'Исходное состояние', 'y': 'Ожидаемое время достижения'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def plot_expected_return_times(self):
        """Визуализация ожидаемых времен возврата"""
        return_times = self.calculate_expected_return_times()
        
        fig = px.bar(
            x=self.markov_chain.state_names,
            y=return_times,
            title="Ожидаемые времена возврата в состояния",
            labels={'x': 'Состояние', 'y': 'Ожидаемое время возврата'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def generate_trading_insights(self) -> Dict:
        """
        Генерация торговых инсайтов на основе анализа цепи Маркова
        
        Returns:
            Словарь с торговыми инсайтами
        """
        if self.stationary_distribution is None:
            self.analyze_stationarity()
        
        # Находим наиболее и наименее вероятные состояния
        max_prob_idx = np.argmax(self.stationary_distribution)
        min_prob_idx = np.argmin(self.stationary_distribution)
        
        max_prob_state = self.markov_chain.state_names[max_prob_idx]
        min_prob_state = self.markov_chain.state_names[min_prob_idx]
        
        # Анализируем состояния по компонентам
        insights = {
            'most_likely_state': {
                'state': max_prob_state,
                'probability': self.stationary_distribution[max_prob_idx],
                'description': self.markov_chain.get_state_description(max_prob_state)
            },
            'least_likely_state': {
                'state': min_prob_state,
                'probability': self.stationary_distribution[min_prob_idx],
                'description': self.markov_chain.get_state_description(min_prob_state)
            },
            'market_regime': self._analyze_market_regime(),
            'volatility_insights': self._analyze_volatility_patterns(),
            'trend_insights': self._analyze_trend_patterns()
        }
        
        return insights
    
    def _analyze_market_regime(self) -> str:
        """Анализ рыночного режима"""
        if self.stationary_distribution is None:
            return "Недостаточно данных"
        
        # Анализируем распределение по трендам
        trend_probs = {'T0': 0, 'T1': 0, 'T2': 0}  # Падение, Боковик, Рост
        
        for i, state in enumerate(self.markov_chain.state_names):
            if state.startswith('T'):
                trend = state.split('_')[0]
                if trend in trend_probs:
                    trend_probs[trend] += self.stationary_distribution[i]
        
        dominant_trend = max(trend_probs, key=trend_probs.get)
        
        if dominant_trend == 'T0':
            return "🐻 Медвежий рынок (преобладает падение)"
        elif dominant_trend == 'T2':
            return "🐂 Бычий рынок (преобладает рост)"
        else:
            return "🦘 Боковой рынок (преобладает консолидация)"
    
    def _analyze_volatility_patterns(self) -> str:
        """Анализ паттернов волатильности"""
        if self.stationary_distribution is None:
            return "Недостаточно данных"
        
        vol_probs = {'V0': 0, 'V1': 0, 'V2': 0}  # Низкая, Средняя, Высокая
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) > 1 and parts[1].startswith('V'):
                vol = parts[1]
                if vol in vol_probs:
                    vol_probs[vol] += self.stationary_distribution[i]
        
        dominant_vol = max(vol_probs, key=vol_probs.get)
        
        if dominant_vol == 'V0':
            return "📉 Низкая волатильность - стабильный рынок"
        elif dominant_vol == 'V2':
            return "📈 Высокая волатильность - нестабильный рынок"
        else:
            return "📊 Умеренная волатильность - сбалансированный рынок"
    
    def _analyze_trend_patterns(self) -> str:
        """Анализ паттернов трендов"""
        if self.stationary_distribution is None:
            return "Недостаточно данных"
        
        # Анализируем RSI паттерны
        rsi_probs = {'R0': 0, 'R1': 0, 'R2': 0}  # Перепроданность, Нейтрально, Перекупленность
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) > 2 and parts[2].startswith('R'):
                rsi = parts[2]
                if rsi in rsi_probs:
                    rsi_probs[rsi] += self.stationary_distribution[i]
        
        dominant_rsi = max(rsi_probs, key=rsi_probs.get)
        
        if dominant_rsi == 'R0':
            return "🟢 Преобладает перепроданность - потенциал для роста"
        elif dominant_rsi == 'R2':
            return "🔴 Преобладает перекупленность - риск коррекции"
        else:
            return "⚪ Нейтральные условия - ожидание сигналов"
    
    def analyze_market_phases(self) -> Dict:
        """Анализ рыночных фаз на основе расширенных состояний"""
        if self.stationary_distribution is None:
            self.analyze_stationarity()
        
        # Анализируем фазы по различным компонентам
        phases = {
            'trend_phases': self._analyze_trend_phases(),
            'volatility_phases': self._analyze_volatility_phases(),
            'momentum_phases': self._analyze_momentum_phases(),
            'volume_phases': self._analyze_volume_phases()
        }
        
        return phases
    
    def _analyze_trend_phases(self) -> Dict:
        """Анализ фаз тренда"""
        trend_probs = {'T0': 0, 'T1': 0, 'T2': 0}
        adx_probs = {'A0': 0, 'A1': 0, 'A2': 0}
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) >= 6:
                trend = parts[0]
                adx = parts[5]
                
                if trend in trend_probs:
                    trend_probs[trend] += self.stationary_distribution[i]
                if adx in adx_probs:
                    adx_probs[adx] += self.stationary_distribution[i]
        
        return {
            'trend_distribution': trend_probs,
            'trend_strength': adx_probs,
            'dominant_trend': max(trend_probs, key=trend_probs.get),
            'trend_quality': max(adx_probs, key=adx_probs.get)
        }
    
    def _analyze_volatility_phases(self) -> Dict:
        """Анализ фаз волатильности"""
        vol_probs = {'V0': 0, 'V1': 0, 'V2': 0}
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) >= 2:
                vol = parts[1]
                if vol in vol_probs:
                    vol_probs[vol] += self.stationary_distribution[i]
        
        return {
            'volatility_distribution': vol_probs,
            'dominant_volatility': max(vol_probs, key=vol_probs.get),
            'volatility_regime': self._classify_volatility_regime(vol_probs)
        }
    
    def _analyze_momentum_phases(self) -> Dict:
        """Анализ фаз моментума"""
        rsi_probs = {'R0': 0, 'R1': 0, 'R2': 0}
        macd_probs = {'M0': 0, 'M1': 0, 'M2': 0}
        stoch_probs = {'S0': 0, 'S1': 0, 'S2': 0}
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) >= 7:
                rsi = parts[2]
                macd = parts[4]
                stoch = parts[6]
                
                if rsi in rsi_probs:
                    rsi_probs[rsi] += self.stationary_distribution[i]
                if macd in macd_probs:
                    macd_probs[macd] += self.stationary_distribution[i]
                if stoch in stoch_probs:
                    stoch_probs[stoch] += self.stationary_distribution[i]
        
        return {
            'rsi_distribution': rsi_probs,
            'macd_distribution': macd_probs,
            'stochastic_distribution': stoch_probs,
            'momentum_consensus': self._calculate_momentum_consensus(rsi_probs, macd_probs, stoch_probs)
        }
    
    def _analyze_volume_phases(self) -> Dict:
        """Анализ фаз объема"""
        volume_probs = {'O0': 0, 'O1': 0, 'O2': 0}
        
        for i, state in enumerate(self.markov_chain.state_names):
            parts = state.split('_')
            if len(parts) >= 4:
                volume = parts[3]
                if volume in volume_probs:
                    volume_probs[volume] += self.stationary_distribution[i]
        
        return {
            'volume_distribution': volume_probs,
            'dominant_volume': max(volume_probs, key=volume_probs.get),
            'volume_regime': self._classify_volume_regime(volume_probs)
        }
    
    def _classify_volatility_regime(self, vol_probs: Dict) -> str:
        """Классификация режима волатильности"""
        if vol_probs['V2'] > 0.5:
            return "Высокая волатильность - нестабильный рынок"
        elif vol_probs['V0'] > 0.5:
            return "Низкая волатильность - стабильный рынок"
        else:
            return "Умеренная волатильность - сбалансированный рынок"
    
    def _classify_volume_regime(self, volume_probs: Dict) -> str:
        """Классификация режима объема"""
        if volume_probs['O2'] > 0.5:
            return "Высокий объем - активная торговля"
        elif volume_probs['O0'] > 0.5:
            return "Низкий объем - слабая активность"
        else:
            return "Умеренный объем - нормальная активность"
    
    def _calculate_momentum_consensus(self, rsi_probs: Dict, macd_probs: Dict, stoch_probs: Dict) -> str:
        """Расчет консенсуса моментума"""
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI
        if rsi_probs['R0'] > rsi_probs['R2']:
            bullish_signals += 1
        elif rsi_probs['R2'] > rsi_probs['R0']:
            bearish_signals += 1
        
        # MACD
        if macd_probs['M2'] > macd_probs['M0']:
            bullish_signals += 1
        elif macd_probs['M0'] > macd_probs['M2']:
            bearish_signals += 1
        
        # Stochastic
        if stoch_probs['S0'] > stoch_probs['S2']:
            bullish_signals += 1
        elif stoch_probs['S2'] > stoch_probs['S0']:
            bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            return "Бычий консенсус - преобладают восходящие сигналы"
        elif bearish_signals > bullish_signals:
            return "Медвежий консенсус - преобладают нисходящие сигналы"
        else:
            return "Смешанный консенсус - противоречивые сигналы"
    
    def generate_advanced_trading_insights(self) -> Dict:
        """Генерация продвинутых торговых инсайтов"""
        if self.stationary_distribution is None:
            self.analyze_stationarity()
        
        # Анализируем рыночные фазы
        phases = self.analyze_market_phases()
        
        # Генерируем инсайты
        insights = {
            'market_regime': self._analyze_market_regime(),
            'phases': phases,
            'trading_recommendations': self._generate_phase_based_recommendations(phases),
            'risk_assessment': self._assess_market_risk(phases),
            'optimal_strategies': self._suggest_optimal_strategies(phases)
        }
        
        return insights
    
    def _generate_phase_based_recommendations(self, phases: Dict) -> Dict:
        """Генерация рекомендаций на основе фаз"""
        recommendations = {
            'trend_strategy': self._get_trend_strategy(phases['trend_phases']),
            'volatility_strategy': self._get_volatility_strategy(phases['volatility_phases']),
            'momentum_strategy': self._get_momentum_strategy(phases['momentum_phases']),
            'volume_strategy': self._get_volume_strategy(phases['volume_phases'])
        }
        
        return recommendations
    
    def _get_trend_strategy(self, trend_phases: Dict) -> str:
        """Стратегия на основе тренда"""
        dominant_trend = trend_phases['dominant_trend']
        trend_quality = trend_phases['trend_quality']
        
        if dominant_trend == 'T2' and trend_quality == 'A2':
            return "Сильный восходящий тренд - агрессивные покупки"
        elif dominant_trend == 'T0' and trend_quality == 'A2':
            return "Сильный нисходящий тренд - агрессивные продажи"
        elif dominant_trend == 'T1':
            return "Боковой тренд - скальпинг и арбитраж"
        else:
            return "Слабый тренд - осторожная торговля"
    
    def _get_volatility_strategy(self, vol_phases: Dict) -> str:
        """Стратегия на основе волатильности"""
        vol_regime = vol_phases['volatility_regime']
        
        if "Высокая волатильность" in vol_regime:
            return "Высокая волатильность - широкие стоп-лоссы, быстрые тейк-профиты"
        elif "Низкая волатильность" in vol_regime:
            return "Низкая волатильность - узкие стоп-лоссы, долгосрочные позиции"
        else:
            return "Умеренная волатильность - стандартные настройки"
    
    def _get_momentum_strategy(self, momentum_phases: Dict) -> str:
        """Стратегия на основе моментума"""
        consensus = momentum_phases['momentum_consensus']
        
        if "Бычий консенсус" in consensus:
            return "Бычий консенсус - фокус на покупках"
        elif "Медвежий консенсус" in consensus:
            return "Медвежий консенсус - фокус на продажах"
        else:
            return "Смешанный консенсус - выборочная торговля"
    
    def _get_volume_strategy(self, volume_phases: Dict) -> str:
        """Стратегия на основе объема"""
        volume_regime = volume_phases['volume_regime']
        
        if "Высокий объем" in volume_regime:
            return "Высокий объем - можно увеличить размер позиций"
        elif "Низкий объем" in volume_regime:
            return "Низкий объем - уменьшить размер позиций"
        else:
            return "Умеренный объем - стандартные размеры позиций"
    
    def _assess_market_risk(self, phases: Dict) -> Dict:
        """Оценка рыночного риска"""
        risk_factors = []
        risk_level = "LOW"
        
        # Анализируем факторы риска
        if phases['volatility_phases']['dominant_volatility'] == 'V2':
            risk_factors.append("Высокая волатильность")
            risk_level = "HIGH"
        
        if phases['trend_phases']['trend_quality'] == 'A0':
            risk_factors.append("Слабый тренд")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        
        if phases['momentum_phases']['momentum_consensus'] == "Смешанный консенсус":
            risk_factors.append("Противоречивые сигналы")
            if risk_level == "LOW":
                risk_level = "MEDIUM"
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommended_position_size': self._get_recommended_position_size(risk_level)
        }
    
    def _get_recommended_position_size(self, risk_level: str) -> str:
        """Рекомендуемый размер позиции"""
        if risk_level == "HIGH":
            return "1-2% от депозита"
        elif risk_level == "MEDIUM":
            return "2-3% от депозита"
        else:
            return "3-5% от депозита"
    
    def _suggest_optimal_strategies(self, phases: Dict) -> List[str]:
        """Предложения оптимальных стратегий"""
        strategies = []
        
        # На основе тренда
        if phases['trend_phases']['trend_quality'] == 'A2':
            strategies.append("Трендовая торговля - следование за трендом")
        
        # На основе волатильности
        if phases['volatility_phases']['dominant_volatility'] == 'V2':
            strategies.append("Скальпинг - быстрые входы и выходы")
        elif phases['volatility_phases']['dominant_volatility'] == 'V0':
            strategies.append("Позиционная торговля - долгосрочные позиции")
        
        # На основе моментума
        if "консенсус" in phases['momentum_phases']['momentum_consensus']:
            strategies.append("Арбитраж - торговля на разнице цен")
        
        # На основе объема
        if phases['volume_phases']['dominant_volume'] == 'O2':
            strategies.append("Breakout торговля - торговля на пробоях")
        
        return strategies if strategies else ["Консервативная торговля - минимальные риски"]
