"""
Модуль для анализа разных таймфреймов и фрактальности в цепях Маркова
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from .markov_chain import CryptoMarkovChain

class TimeframeAnalysis:
    """Класс для анализа цепей Маркова на разных таймфреймах"""
    
    def __init__(self):
        self.timeframes = {
            '1m': '1 минута',
            '5m': '5 минут', 
            '15m': '15 минут',
            '1h': '1 час',
            '4h': '4 часа',
            '1d': '1 день',
            '1w': '1 неделя'
        }
        self.markov_chains = {}
        self.fractal_analysis = {}
        
    def analyze_multiple_timeframes(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Анализ цепей Маркова на нескольких таймфреймах
        
        Args:
            data: Словарь с данными по таймфреймам {timeframe: DataFrame}
        
        Returns:
            Результаты анализа по всем таймфреймам
        """
        results = {}
        
        for timeframe, df in data.items():
            st.write(f"🔍 Анализируем таймфрейм: {self.timeframes.get(timeframe, timeframe)}")
            
            # Создаем цепь Маркова для этого таймфрейма
            markov_chain = CryptoMarkovChain()
            
            # Определяем состояния
            states = markov_chain.define_states(df)
            
            # Строим матрицу переходов
            transition_matrix = markov_chain.build_transition_matrix(df)
            
            # Анализируем стационарность
            stationary_analysis = self._analyze_stationarity(transition_matrix)
            
            # Анализируем фрактальность
            fractal_analysis = self._analyze_fractality(df, timeframe)
            
            results[timeframe] = {
                'markov_chain': markov_chain,
                'states': states,
                'transition_matrix': transition_matrix,
                'stationary_analysis': stationary_analysis,
                'fractal_analysis': fractal_analysis,
                'data_points': len(df),
                'unique_states': len(set(states.values()))
            }
            
            self.markov_chains[timeframe] = markov_chain
        
        return results
    
    def _analyze_stationarity(self, transition_matrix: np.ndarray) -> Dict:
        """Анализ стационарности матрицы переходов"""
        # Находим собственные значения
        eigenvalues, eigenvectors = np.linalg.eig(transition_matrix.T)
        
        # Находим стационарное распределение
        stationary_idx = np.argmin(np.abs(eigenvalues - 1.0))
        stationary_vector = np.real(eigenvectors[:, stationary_idx])
        stationary_vector = np.abs(stationary_vector)
        stationary_vector = stationary_vector / np.sum(stationary_vector)
        
        # Проверяем стационарность
        is_stationary = np.allclose(transition_matrix.T @ stationary_vector, stationary_vector, atol=1e-10)
        
        # Энтропия
        entropy = -np.sum(stationary_vector * np.log(stationary_vector + 1e-10))
        
        return {
            'is_stationary': is_stationary,
            'stationary_distribution': stationary_vector,
            'entropy': entropy,
            'max_probability': np.max(stationary_vector),
            'min_probability': np.min(stationary_vector)
        }
    
    def _analyze_fractality(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """Анализ фрактальности данных"""
        # Анализируем волатильность на разных масштабах
        volatility_scales = self._calculate_volatility_scales(data)
        
        # Анализируем корреляции между таймфреймами
        correlation_analysis = self._analyze_cross_timeframe_correlations(data, timeframe)
        
        # Анализируем самоподобие
        self_similarity = self._analyze_self_similarity(data)
        
        return {
            'volatility_scales': volatility_scales,
            'correlation_analysis': correlation_analysis,
            'self_similarity': self_similarity,
            'hurst_exponent': self._calculate_hurst_exponent(data['Close'])
        }
    
    def _calculate_volatility_scales(self, data: pd.DataFrame) -> Dict:
        """Расчет волатильности на разных временных масштабах"""
        scales = [1, 5, 10, 20, 50]  # Разные временные окна
        volatility_by_scale = {}
        
        for scale in scales:
            if len(data) >= scale:
                returns = data['Close'].pct_change(scale).dropna()
                volatility = returns.std() * np.sqrt(scale)  # Масштабируем
                volatility_by_scale[f'scale_{scale}'] = volatility
        
        return volatility_by_scale
    
    def _analyze_cross_timeframe_correlations(self, data: pd.DataFrame, timeframe: str) -> Dict:
        """Анализ корреляций между таймфреймами"""
        # Это упрощенная версия - в реальности нужны данные по всем таймфреймам
        correlations = {
            'intraday_patterns': self._analyze_intraday_patterns(data),
            'weekly_patterns': self._analyze_weekly_patterns(data),
            'monthly_patterns': self._analyze_monthly_patterns(data)
        }
        
        return correlations
    
    def _analyze_intraday_patterns(self, data: pd.DataFrame) -> Dict:
        """Анализ внутридневных паттернов"""
        if 'hour' not in data.index.names and hasattr(data.index, 'hour'):
            data_with_hour = data.copy()
            data_with_hour['hour'] = data_with_hour.index.hour
        else:
            return {'error': 'Нет данных о часах'}
        
        # Группируем по часам
        hourly_volatility = data_with_hour.groupby('hour')['Close'].std()
        hourly_returns = data_with_hour.groupby('hour')['Close'].mean()
        
        return {
            'hourly_volatility': hourly_volatility.to_dict(),
            'hourly_returns': hourly_returns.to_dict(),
            'peak_hour': hourly_volatility.idxmax(),
            'quiet_hour': hourly_volatility.idxmin()
        }
    
    def _analyze_weekly_patterns(self, data: pd.DataFrame) -> Dict:
        """Анализ недельных паттернов"""
        if hasattr(data.index, 'dayofweek'):
            data_with_dow = data.copy()
            data_with_dow['dayofweek'] = data_with_dow.index.dayofweek
        else:
            return {'error': 'Нет данных о днях недели'}
        
        # Группируем по дням недели
        daily_volatility = data_with_dow.groupby('dayofweek')['Close'].std()
        daily_returns = data_with_dow.groupby('dayofweek')['Close'].mean()
        
        day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        
        return {
            'daily_volatility': {day_names[i]: daily_volatility.get(i, 0) for i in range(7)},
            'daily_returns': {day_names[i]: daily_returns.get(i, 0) for i in range(7)},
            'most_volatile_day': day_names[daily_volatility.idxmax()],
            'least_volatile_day': day_names[daily_volatility.idxmin()]
        }
    
    def _analyze_monthly_patterns(self, data: pd.DataFrame) -> Dict:
        """Анализ месячных паттернов"""
        if hasattr(data.index, 'month'):
            data_with_month = data.copy()
            data_with_month['month'] = data_with_month.index.month
        else:
            return {'error': 'Нет данных о месяцах'}
        
        # Группируем по месяцам
        monthly_volatility = data_with_month.groupby('month')['Close'].std()
        monthly_returns = data_with_month.groupby('month')['Close'].mean()
        
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 
                      'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        
        return {
            'monthly_volatility': {month_names[i-1]: monthly_volatility.get(i, 0) for i in range(1, 13)},
            'monthly_returns': {month_names[i-1]: monthly_returns.get(i, 0) for i in range(1, 13)},
            'most_volatile_month': month_names[monthly_volatility.idxmax() - 1],
            'least_volatile_month': month_names[monthly_volatility.idxmin() - 1]
        }
    
    def _analyze_self_similarity(self, data: pd.DataFrame) -> Dict:
        """Анализ самоподобия (фрактальности)"""
        # Анализируем самоподобие на разных масштабах времени
        scales = [2, 4, 8, 16, 32]
        similarity_scores = {}
        
        for scale in scales:
            if len(data) >= scale * 2:
                # Берем каждую scale-ю точку
                sampled_data = data.iloc[::scale]
                if len(sampled_data) >= 10:
                    # Сравниваем статистики
                    original_vol = data['Close'].pct_change().std()
                    sampled_vol = sampled_data['Close'].pct_change().std()
                    
                    similarity = 1 - abs(original_vol - sampled_vol) / original_vol
                    similarity_scores[f'scale_{scale}'] = max(0, similarity)
        
        return {
            'similarity_scores': similarity_scores,
            'average_similarity': np.mean(list(similarity_scores.values())) if similarity_scores else 0,
            'is_fractal': np.mean(list(similarity_scores.values())) > 0.7 if similarity_scores else False
        }
    
    def _calculate_hurst_exponent(self, prices: pd.Series) -> float:
        """Расчет экспоненты Херста для определения фрактальности"""
        try:
            # Упрощенный расчет экспоненты Херста
            returns = prices.pct_change().dropna()
            
            # Разные временные окна
            windows = [2, 4, 8, 16, 32]
            if len(returns) < max(windows):
                return 0.5  # Случайное блуждание
            
            ranges = []
            scales = []
            
            for window in windows:
                if len(returns) >= window:
                    # Разбиваем на окна
                    n_windows = len(returns) // window
                    if n_windows > 0:
                        windowed_returns = returns[:n_windows * window].values.reshape(n_windows, window)
                        
                        # Вычисляем R/S для каждого окна
                        rs_values = []
                        for w in windowed_returns:
                            if len(w) > 1:
                                mean_w = np.mean(w)
                                deviations = w - mean_w
                                cumulative = np.cumsum(deviations)
                                R = np.max(cumulative) - np.min(cumulative)
                                S = np.std(w)
                                if S > 0:
                                    rs_values.append(R / S)
                        
                        if rs_values:
                            ranges.append(np.mean(rs_values))
                            scales.append(window)
            
            if len(ranges) >= 2:
                # Линейная регрессия log(R/S) vs log(scale)
                log_scales = np.log(scales)
                log_ranges = np.log(ranges)
                
                # Простая линейная регрессия
                n = len(log_scales)
                if n > 1:
                    slope = (n * np.sum(log_scales * log_ranges) - np.sum(log_scales) * np.sum(log_ranges)) / \
                           (n * np.sum(log_scales**2) - np.sum(log_scales)**2)
                    return slope
                else:
                    return 0.5
            else:
                return 0.5
                
        except Exception:
            return 0.5  # По умолчанию случайное блуждание
    
    def plot_timeframe_comparison(self, results: Dict):
        """Визуализация сравнения таймфреймов"""
        timeframes = list(results.keys())
        
        # График количества состояний
        fig1 = go.Figure()
        
        states_count = [results[tf]['unique_states'] for tf in timeframes]
        data_points = [results[tf]['data_points'] for tf in timeframes]
        
        fig1.add_trace(go.Bar(
            x=[self.timeframes.get(tf, tf) for tf in timeframes],
            y=states_count,
            name='Уникальные состояния',
            marker_color='blue'
        ))
        
        fig1.update_layout(
            title="Количество состояний по таймфреймам",
            xaxis_title="Таймфрейм",
            yaxis_title="Количество состояний",
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # График энтропии
        fig2 = go.Figure()
        
        entropies = [results[tf]['stationary_analysis']['entropy'] for tf in timeframes]
        
        fig2.add_trace(go.Scatter(
            x=[self.timeframes.get(tf, tf) for tf in timeframes],
            y=entropies,
            mode='lines+markers',
            name='Энтропия',
            line=dict(color='red', width=3),
            marker=dict(size=8)
        ))
        
        fig2.update_layout(
            title="Энтропия по таймфреймам",
            xaxis_title="Таймфрейм",
            yaxis_title="Энтропия",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # График фрактальности
        fig3 = go.Figure()
        
        hurst_exponents = [results[tf]['fractal_analysis']['hurst_exponent'] for tf in timeframes]
        
        fig3.add_trace(go.Scatter(
            x=[self.timeframes.get(tf, tf) for tf in timeframes],
            y=hurst_exponents,
            mode='lines+markers',
            name='Экспонента Херста',
            line=dict(color='green', width=3),
            marker=dict(size=8)
        ))
        
        # Добавляем горизонтальные линии для интерпретации
        fig3.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                      annotation_text="Случайное блуждание (0.5)")
        fig3.add_hline(y=0.7, line_dash="dash", line_color="orange", 
                      annotation_text="Тренд (0.7)")
        fig3.add_hline(y=0.3, line_dash="dash", line_color="purple", 
                      annotation_text="Среднее возвращение (0.3)")
        
        fig3.update_layout(
            title="Фрактальность по таймфреймам (Экспонента Херста)",
            xaxis_title="Таймфрейм",
            yaxis_title="Экспонента Херста",
            height=400
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    def generate_trading_insights(self, results: Dict) -> Dict:
        """Генерация торговых инсайтов на основе анализа таймфреймов"""
        insights = {
            'best_timeframes': [],
            'fractal_insights': [],
            'volatility_insights': [],
            'recommendations': []
        }
        
        # Анализируем лучшие таймфреймы
        for tf, result in results.items():
            entropy = result['stationary_analysis']['entropy']
            hurst = result['fractal_analysis']['hurst_exponent']
            states_count = result['unique_states']
            
            # Критерии для "хорошего" таймфрейма
            score = 0
            if entropy > 2.0:  # Высокая энтропия = много информации
                score += 1
            if 0.4 < hurst < 0.6:  # Близко к случайному блужданию = предсказуемо
                score += 1
            if states_count > 10:  # Достаточно состояний для анализа
                score += 1
            
            if score >= 2:
                insights['best_timeframes'].append({
                    'timeframe': tf,
                    'score': score,
                    'entropy': entropy,
                    'hurst': hurst
                })
        
        # Сортируем по score
        insights['best_timeframes'].sort(key=lambda x: x['score'], reverse=True)
        
        # Анализируем фрактальность
        fractal_tfs = [tf for tf, result in results.items() 
                      if result['fractal_analysis']['is_fractal']]
        
        if fractal_tfs:
            insights['fractal_insights'].append(
                f"Фрактальные паттерны обнаружены на таймфреймах: {', '.join(fractal_tfs)}"
            )
            insights['recommendations'].append(
                "Используйте фрактальный анализ для прогнозирования на разных масштабах"
            )
        
        # Анализируем волатильность
        volatility_analysis = {}
        for tf, result in results.items():
            vol_scales = result['fractal_analysis']['volatility_scales']
            if vol_scales:
                avg_vol = np.mean(list(vol_scales.values()))
                volatility_analysis[tf] = avg_vol
        
        if volatility_analysis:
            most_volatile = max(volatility_analysis, key=volatility_analysis.get)
            least_volatile = min(volatility_analysis, key=volatility_analysis.get)
            
            insights['volatility_insights'].extend([
                f"Самый волатильный таймфрейм: {most_volatile}",
                f"Самый стабильный таймфрейм: {least_volatile}"
            ])
        
        return insights
