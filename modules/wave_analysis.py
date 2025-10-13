"""
Детальный модуль волнового анализа для криптовалют
Анализирует волны Эллиотта, определяет импульсы и коррекции
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from .data_fetcher import CryptoDataFetcher

class WaveAnalysis:
    """Класс для детального волнового анализа"""
    
    def __init__(self):
        self.data_fetcher = CryptoDataFetcher()
        self.timeframes = {
            '1m': '1 минута',
            '5m': '5 минут', 
            '15m': '15 минут',
            '1h': '1 час',
            '4h': '4 часа',
            '1d': '1 день',
            '1w': '1 неделя'
        }
        
    def render_wave_analysis_interface(self):
        """Главный интерфейс волнового анализа"""
        
        st.markdown("## 🌊 Детальный волновой анализ")
        
        # Объяснение волнового анализа
        st.info("""
        **🌊 Что такое волновой анализ?**
        
        Волновой анализ основан на теории Эллиотта - рынок движется волнами:
        - **📈 Импульс** - 5 волн в направлении тренда (1-2-3-4-5)
        - **📉 Коррекция** - 3 волны против тренда (A-B-C)
        - **🔄 Циклы** - импульсы и коррекции повторяются
        
        **🎯 Цель:** Определить текущую волну и предсказать следующее движение
        """)
        
        # Выбор параметров
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Выбор криптовалюты
            crypto_options = self.data_fetcher.get_available_symbols()
            selected_crypto = st.selectbox(
                "🪙 Криптовалюта:",
                list(crypto_options.keys()),
                index=0
            )
            symbol = crypto_options[selected_crypto]
        
        with col2:
            # Выбор таймфрейма
            selected_timeframe = st.selectbox(
                "⏰ Таймфрейм:",
                list(self.timeframes.keys()),
                index=5,  # По умолчанию 1 день
                format_func=lambda x: self.timeframes[x]
            )
        
        with col3:
            # Период анализа
            analysis_period = st.selectbox(
                "📅 Период анализа:",
                ["3mo", "6mo", "1y", "2y"],
                index=2,  # По умолчанию 1 год
                format_func=lambda x: {
                    "3mo": "3 месяца",
                    "6mo": "6 месяцев", 
                    "1y": "1 год",
                    "2y": "2 года"
                }[x]
            )
        
        # Кнопка анализа
        if st.button("🌊 Анализировать волны", use_container_width=True):
            with st.spinner("Анализируем волны..."):
                self._run_wave_analysis(symbol, selected_timeframe, analysis_period)
    
    def _run_wave_analysis(self, symbol: str, timeframe: str, period: str):
        """Запуск волнового анализа"""
        
        # Загружаем данные
        data = self.data_fetcher.fetch_data(symbol, period)
        
        if data is None or data.empty:
            st.error("❌ Не удалось загрузить данные")
            return
        
        # Сохраняем данные в session_state
        st.session_state.wave_data = data
        st.session_state.wave_symbol = symbol
        st.session_state.wave_timeframe = timeframe
        st.session_state.wave_period = period
        
        st.success(f"✅ Данные загружены! {len(data)} записей за {period}")
        
        # Анализируем волны
        wave_analysis = self._analyze_waves(data)
        
        # Показываем результаты
        self._display_wave_analysis(wave_analysis, data, symbol, timeframe)
    
    def _analyze_waves(self, data: pd.DataFrame) -> Dict:
        """Анализ волн на данных"""
        
        # Находим локальные экстремумы
        highs, lows = self._find_extremes(data)
        
        # Определяем волны
        waves = self._identify_waves(data, highs, lows)
        
        # Классифицируем волны
        wave_classification = self._classify_waves(waves, data)
        
        # Определяем текущую фазу
        current_phase = self._determine_current_phase(waves, data)
        
        # Анализируем паттерны
        patterns = self._analyze_patterns(waves, data)
        
        return {
            'extremes': {'highs': highs, 'lows': lows},
            'waves': waves,
            'classification': wave_classification,
            'current_phase': current_phase,
            'patterns': patterns,
            'data': data
        }
    
    def _find_extremes(self, data: pd.DataFrame, window: int = 5) -> Tuple[List, List]:
        """Находим локальные максимумы и минимумы"""
        
        # Локальные максимумы
        highs = data['High'].rolling(window=window, center=True).max() == data['High']
        high_points = data[highs].copy()
        high_points = high_points.reset_index()
        high_points['type'] = 'high'
        
        # Локальные минимумы
        lows = data['Low'].rolling(window=window, center=True).min() == data['Low']
        low_points = data[lows].copy()
        low_points = low_points.reset_index()
        low_points['type'] = 'low'
        
        return high_points, low_points
    
    def _identify_waves(self, data: pd.DataFrame, highs: pd.DataFrame, lows: pd.DataFrame) -> List[Dict]:
        """Идентификация волн"""
        
        # Объединяем все экстремумы
        all_extremes = []
        
        for _, row in highs.iterrows():
            all_extremes.append({
                'date': row['Date'],
                'price': row['High'],
                'type': 'high',
                'index': row.name
            })
        
        for _, row in lows.iterrows():
            all_extremes.append({
                'date': row['Date'],
                'price': row['Low'],
                'type': 'low',
                'index': row.name
            })
        
        # Сортируем по дате
        all_extremes.sort(key=lambda x: x['date'])
        
        # Определяем волны
        waves = []
        for i in range(len(all_extremes) - 1):
            current = all_extremes[i]
            next_point = all_extremes[i + 1]
            
            # Определяем направление волны
            if current['type'] == 'low' and next_point['type'] == 'high':
                direction = 'up'
            elif current['type'] == 'high' and next_point['type'] == 'low':
                direction = 'down'
            else:
                continue
            
            # Вычисляем параметры волны
            price_change = next_point['price'] - current['price']
            price_change_pct = (price_change / current['price']) * 100
            duration = (next_point['date'] - current['date']).days
            
            wave = {
                'start_date': current['date'],
                'end_date': next_point['date'],
                'start_price': current['price'],
                'end_price': next_point['price'],
                'direction': direction,
                'change': price_change,
                'change_pct': price_change_pct,
                'duration': duration,
                'start_index': current['index'],
                'end_index': next_point['index']
            }
            
            waves.append(wave)
        
        return waves
    
    def _classify_waves(self, waves: List[Dict], data: pd.DataFrame) -> Dict:
        """Классификация волн на импульсы и коррекции"""
        
        if len(waves) < 5:
            return {'type': 'insufficient_data', 'waves': waves}
        
        # Анализируем последние 5 волн для определения паттерна
        recent_waves = waves[-5:]
        
        # Определяем общий тренд
        total_change = sum(wave['change'] for wave in recent_waves)
        
        if total_change > 0:
            trend = 'bullish'
        else:
            trend = 'bearish'
        
        # Анализируем паттерн
        pattern = self._analyze_elliott_pattern(recent_waves, trend)
        
        return {
            'type': pattern['type'],
            'trend': trend,
            'confidence': pattern['confidence'],
            'waves': recent_waves,
            'description': pattern['description']
        }
    
    def _analyze_elliott_pattern(self, waves: List[Dict], trend: str) -> Dict:
        """Анализ паттерна Эллиотта"""
        
        if len(waves) < 5:
            return {
                'type': 'insufficient_data',
                'confidence': 0,
                'description': 'Недостаточно данных для анализа'
            }
        
        # Анализируем соотношения волн
        wave_changes = [abs(wave['change_pct']) for wave in waves]
        
        # Простая эвристика для определения импульса/коррекции
        if len(wave_changes) >= 5:
            # Проверяем на импульс (волна 3 самая сильная)
            if wave_changes[2] > wave_changes[0] and wave_changes[2] > wave_changes[4]:
                return {
                    'type': 'impulse',
                    'confidence': 0.7,
                    'description': 'Импульсная волна - волна 3 самая сильная'
                }
            # Проверяем на коррекцию (волны A и C примерно равны)
            elif abs(wave_changes[0] - wave_changes[2]) < 0.5:
                return {
                    'type': 'correction',
                    'confidence': 0.6,
                    'description': 'Коррекционная волна - волны A и C примерно равны'
                }
        
        return {
            'type': 'unclear',
            'confidence': 0.3,
            'description': 'Паттерн неясен - нужен дополнительный анализ'
        }
    
    def _determine_current_phase(self, waves: List[Dict], data: pd.DataFrame) -> Dict:
        """Определение текущей фазы волны"""
        
        if not waves:
            return {'phase': 'unknown', 'description': 'Нет данных о волнах'}
        
        # Берем последнюю волну
        last_wave = waves[-1]
        current_price = data['Close'].iloc[-1]
        
        # Определяем, где мы находимся относительно последней волны
        if last_wave['direction'] == 'up':
            if current_price > last_wave['end_price']:
                phase = 'continuation'
                description = 'Продолжение восходящей волны'
            elif current_price < last_wave['start_price']:
                phase = 'reversal'
                description = 'Разворот после восходящей волны'
            else:
                phase = 'retracement'
                description = 'Откат в восходящей волне'
        else:
            if current_price < last_wave['end_price']:
                phase = 'continuation'
                description = 'Продолжение нисходящей волны'
            elif current_price > last_wave['start_price']:
                phase = 'reversal'
                description = 'Разворот после нисходящей волны'
            else:
                phase = 'retracement'
                description = 'Откат в нисходящей волне'
        
        return {
            'phase': phase,
            'description': description,
            'last_wave': last_wave
        }
    
    def _analyze_patterns(self, waves: List[Dict], data: pd.DataFrame) -> Dict:
        """Анализ паттернов волн"""
        
        if len(waves) < 3:
            return {'patterns': [], 'summary': 'Недостаточно волн для анализа паттернов'}
        
        patterns = []
        
        # Анализируем последние 3 волны
        recent_waves = waves[-3:]
        
        # Проверяем на треугольник
        if self._is_triangle(recent_waves):
            patterns.append({
                'type': 'triangle',
                'description': 'Треугольная консолидация',
                'confidence': 0.7
            })
        
        # Проверяем на флаг
        if self._is_flag(recent_waves):
            patterns.append({
                'type': 'flag',
                'description': 'Флаг - продолжение тренда',
                'confidence': 0.6
            })
        
        # Проверяем на клин
        if self._is_wedge(recent_waves):
            patterns.append({
                'type': 'wedge',
                'description': 'Клин - возможный разворот',
                'confidence': 0.5
            })
        
        return {
            'patterns': patterns,
            'summary': f'Найдено {len(patterns)} паттернов'
        }
    
    def _is_triangle(self, waves: List[Dict]) -> bool:
        """Проверка на треугольник"""
        if len(waves) < 3:
            return False
        
        # Простая проверка - волны сжимаются
        changes = [abs(wave['change_pct']) for wave in waves]
        return changes[0] > changes[1] > changes[2]
    
    def _is_flag(self, waves: List[Dict]) -> bool:
        """Проверка на флаг"""
        if len(waves) < 3:
            return False
        
        # Флаг - сильная волна, затем слабые коррекции
        first_wave = abs(waves[0]['change_pct'])
        other_waves = [abs(wave['change_pct']) for wave in waves[1:]]
        
        return first_wave > max(other_waves) * 2
    
    def _is_wedge(self, waves: List[Dict]) -> bool:
        """Проверка на клин"""
        if len(waves) < 3:
            return False
        
        # Клин - волны сжимаются, но в одном направлении
        directions = [wave['direction'] for wave in waves]
        return len(set(directions)) == 1  # Все в одном направлении
    
    def _display_wave_analysis(self, analysis: Dict, data: pd.DataFrame, symbol: str, timeframe: str):
        """Отображение результатов волнового анализа"""
        
        st.markdown("---")
        
        # Красивый заголовок с градиентом
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        ">
            <h2 style="color: white; margin: 0; font-size: 28px;">
                📊 Результаты волнового анализа
            </h2>
            <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">
                Детальный анализ волн Эллиотта и торговые рекомендации
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Основная информация в красивых карточках
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <h4 style="margin: 0; font-size: 18px;">🪙 Криптовалюта</h4>
                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                    {symbol}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <h4 style="margin: 0; font-size: 18px;">⏰ Таймфрейм</h4>
                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                    {self.timeframes[timeframe]}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #fd7e14 0%, #e83e8c 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <h4 style="margin: 0; font-size: 18px;">🌊 Найдено волн</h4>
                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                    {len(analysis['waves'])}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            pattern_type = analysis['classification']['type'].upper() if analysis['classification']['type'] != 'insufficient_data' else "НЕДОСТАТОЧНО ДАННЫХ"
            pattern_color = "#28a745" if analysis['classification']['type'] != 'insufficient_data' else "#dc3545"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {pattern_color} 0%, #6c757d 100%);
                color: white;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 5px 0;
            ">
                <h4 style="margin: 0; font-size: 18px;">📈 Тип паттерна</h4>
                <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
                    {pattern_type}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Классификация волн
        self._display_wave_classification(analysis['classification'])
        
        # Текущая фаза
        self._display_current_phase(analysis['current_phase'])
        
        # Паттерны
        self._display_patterns(analysis['patterns'])
        
        # График волн
        self._plot_wave_chart(analysis, data, symbol)
        
        # Торговые рекомендации
        self._display_trading_recommendations(analysis, symbol)
    
    def _display_wave_classification(self, classification: Dict):
        """Отображение классификации волн"""
        
        # Красивый заголовок
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        ">
            <h3 style="margin: 0; color: #495057; font-size: 22px;">
                🎯 Классификация волн
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        if classification['type'] == 'insufficient_data':
            st.markdown("""
            <div style="
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 10px 0;
            ">
                <h4 style="margin: 0; color: #856404;">⚠️ Недостаточно данных для классификации волн</h4>
            </div>
            """, unsafe_allow_html=True)
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Определяем цвет в зависимости от типа
            if classification['type'] == 'impulse':
                card_color = "#d4edda"
                border_color = "#c3e6cb"
                text_color = "#155724"
            elif classification['type'] == 'correction':
                card_color = "#d1ecf1"
                border_color = "#bee5eb"
                text_color = "#0c5460"
            else:
                card_color = "#fff3cd"
                border_color = "#ffeaa7"
                text_color = "#856404"
            
            st.markdown(f"""
            <div style="
                background: {card_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
            ">
                <h4 style="margin: 0 0 15px 0; color: {text_color}; text-align: center;">
                    📊 Основные параметры
                </h4>
                <p style="margin: 8px 0; color: {text_color}; font-weight: bold;">
                    <span style="color: #495057;">Тип:</span> {classification['type'].upper()}
                </p>
                <p style="margin: 8px 0; color: {text_color}; font-weight: bold;">
                    <span style="color: #495057;">Тренд:</span> {classification['trend']}
                </p>
                <p style="margin: 8px 0; color: {text_color}; font-weight: bold;">
                    <span style="color: #495057;">Уверенность:</span> {classification['confidence']:.1%}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: #ffffff;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
            ">
                <h4 style="margin: 0 0 15px 0; color: #495057; text-align: center;">
                    📝 Описание
                </h4>
                <p style="margin: 8px 0; color: #495057; font-size: 16px;">
                    {classification['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Дополнительная информация в зависимости от типа
            if classification['type'] == 'impulse':
                st.markdown("""
                <div style="
                    background: #d4edda;
                    border: 2px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h5 style="margin: 0; color: #155724;">📈 Импульс</h5>
                    <p style="margin: 5px 0 0 0; color: #155724; font-weight: bold;">
                        Сильное движение в направлении тренда
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif classification['type'] == 'correction':
                st.markdown("""
                <div style="
                    background: #d1ecf1;
                    border: 2px solid #bee5eb;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h5 style="margin: 0; color: #0c5460;">📉 Коррекция</h5>
                    <p style="margin: 5px 0 0 0; color: #0c5460; font-weight: bold;">
                        Откат против основного тренда
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #fff3cd;
                    border: 2px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h5 style="margin: 0; color: #856404;">❓ Неясно</h5>
                    <p style="margin: 5px 0 0 0; color: #856404; font-weight: bold;">
                        Нужен дополнительный анализ
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def _display_current_phase(self, phase: Dict):
        """Отображение текущей фазы"""
        
        # Красивый заголовок
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        ">
            <h3 style="margin: 0; color: #495057; font-size: 22px;">
                🌊 Текущая фаза
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Определяем цвет в зависимости от фазы
            if phase['phase'] == 'continuation':
                card_color = "#d4edda"
                border_color = "#c3e6cb"
                text_color = "#155724"
            elif phase['phase'] == 'reversal':
                card_color = "#fff3cd"
                border_color = "#ffeaa7"
                text_color = "#856404"
            elif phase['phase'] == 'retracement':
                card_color = "#d1ecf1"
                border_color = "#bee5eb"
                text_color = "#0c5460"
            else:
                card_color = "#f8d7da"
                border_color = "#f5c6cb"
                text_color = "#721c24"
            
            st.markdown(f"""
            <div style="
                background: {card_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 20px;
                margin: 10px 0;
            ">
                <h4 style="margin: 0 0 15px 0; color: {text_color}; text-align: center;">
                    📊 Информация о фазе
                </h4>
                <p style="margin: 8px 0; color: {text_color}; font-weight: bold;">
                    <span style="color: #495057;">Фаза:</span> {phase['phase'].upper()}
                </p>
                <p style="margin: 8px 0; color: {text_color}; font-weight: bold;">
                    <span style="color: #495057;">Описание:</span> {phase['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Дополнительная информация в зависимости от фазы
            if phase['phase'] == 'continuation':
                st.markdown("""
                <div style="
                    background: #d4edda;
                    border: 2px solid #c3e6cb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #155724;">🟢 Продолжение</h4>
                    <p style="margin: 10px 0 0 0; color: #155724; font-weight: bold;">
                        Тренд сохраняется
                    </p>
                    <p style="margin: 5px 0 0 0; color: #155724; font-size: 14px;">
                        Рекомендуется следовать текущему направлению
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif phase['phase'] == 'reversal':
                st.markdown("""
                <div style="
                    background: #fff3cd;
                    border: 2px solid #ffeaa7;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #856404;">🟡 Разворот</h4>
                    <p style="margin: 10px 0 0 0; color: #856404; font-weight: bold;">
                        Возможна смена тренда
                    </p>
                    <p style="margin: 5px 0 0 0; color: #856404; font-size: 14px;">
                        Будьте осторожны с новыми позициями
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif phase['phase'] == 'retracement':
                st.markdown("""
                <div style="
                    background: #d1ecf1;
                    border: 2px solid #bee5eb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #0c5460;">🔵 Откат</h4>
                    <p style="margin: 10px 0 0 0; color: #0c5460; font-weight: bold;">
                        Временная коррекция
                    </p>
                    <p style="margin: 5px 0 0 0; color: #0c5460; font-size: 14px;">
                        Возможность войти по лучшей цене
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: #f8d7da;
                    border: 2px solid #f5c6cb;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 10px 0;
                    text-align: center;
                ">
                    <h4 style="margin: 0; color: #721c24;">❌ Неизвестно</h4>
                    <p style="margin: 10px 0 0 0; color: #721c24; font-weight: bold;">
                        Неопределенность
                    </p>
                    <p style="margin: 5px 0 0 0; color: #721c24; font-size: 14px;">
                        Рекомендуется дождаться четких сигналов
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def _display_patterns(self, patterns: Dict):
        """Отображение найденных паттернов"""
        
        st.markdown("#### 🔍 Найденные паттерны")
        
        if not patterns['patterns']:
            st.info("ℹ️ Специальные паттерны не обнаружены")
            return
        
        for pattern in patterns['patterns']:
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if pattern['type'] == 'triangle':
                        st.markdown("🔺 **Треугольник**")
                    elif pattern['type'] == 'flag':
                        st.markdown("🏁 **Флаг**")
                    elif pattern['type'] == 'wedge':
                        st.markdown("🔺 **Клин**")
                
                with col2:
                    st.markdown(f"**{pattern['description']}**")
                
                with col3:
                    st.markdown(f"Уверенность: {pattern['confidence']:.1%}")
    
    def _plot_wave_chart(self, analysis: Dict, data: pd.DataFrame, symbol: str):
        """Построение графика волн"""
        
        st.markdown("#### 📈 График волн")
        
        fig = go.Figure()
        
        # Цена
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Цена',
            line=dict(color='blue', width=2)
        ))
        
        # Волны
        waves = analysis['waves']
        for i, wave in enumerate(waves[-10:]):  # Показываем последние 10 волн
            color = 'green' if wave['direction'] == 'up' else 'red'
            
            fig.add_trace(go.Scatter(
                x=[wave['start_date'], wave['end_date']],
                y=[wave['start_price'], wave['end_price']],
                mode='lines+markers',
                name=f'Волна {i+1}',
                line=dict(color=color, width=3),
                marker=dict(size=8),
                showlegend=False
            ))
        
        # Локальные экстремумы
        highs = analysis['extremes']['highs']
        lows = analysis['extremes']['lows']
        
        if not highs.empty:
            fig.add_trace(go.Scatter(
                x=highs['Date'],
                y=highs['High'],
                mode='markers',
                name='Вершины',
                marker=dict(color='red', size=6, symbol='triangle-up'),
                showlegend=False
            ))
        
        if not lows.empty:
            fig.add_trace(go.Scatter(
                x=lows['Date'],
                y=lows['Low'],
                mode='markers',
                name='Основания',
                marker=dict(color='green', size=6, symbol='triangle-down'),
                showlegend=False
            ))
        
        fig.update_layout(
            title=f"Волновой анализ {symbol}",
            xaxis_title="Дата",
            yaxis_title="Цена",
            height=600,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_trading_recommendations(self, analysis: Dict, symbol: str):
        """Отображение торговых рекомендаций на основе волнового анализа"""
        
        # Красивый заголовок
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        ">
            <h2 style="color: white; margin: 0; font-size: 28px;">
                💰 Торговые рекомендации
            </h2>
            <p style="color: #f0f0f0; margin: 10px 0 0 0; font-size: 16px;">
                Детальные планы входа и выхода на основе волнового анализа
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        classification = analysis['classification']
        phase = analysis['current_phase']
        patterns = analysis['patterns']
        
        # Основные рекомендации в красивых карточках
        if classification['type'] == 'impulse':
            if phase['phase'] == 'continuation':
                st.markdown("""
                <div style="
                    background: #d4edda;
                    border: 3px solid #28a745;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #155724; font-size: 24px;">
                        🟢 ПОКУПКА
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #155724; font-size: 18px; font-weight: bold;">
                        Импульс продолжается
                    </p>
                </div>
                """, unsafe_allow_html=True)
                self._show_impulse_trading_plan(symbol, 'buy')
            elif phase['phase'] == 'retracement':
                st.markdown("""
                <div style="
                    background: #d1ecf1;
                    border: 3px solid #17a2b8;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #0c5460; font-size: 24px;">
                        🔵 ОЖИДАНИЕ
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #0c5460; font-size: 18px; font-weight: bold;">
                        Откат в импульсе, ждите входа
                    </p>
                </div>
                """, unsafe_allow_html=True)
                self._show_retracement_trading_plan(symbol)
            else:
                st.markdown("""
                <div style="
                    background: #fff3cd;
                    border: 3px solid #ffc107;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #856404; font-size: 24px;">
                        🟡 ОСТОРОЖНО
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #856404; font-size: 18px; font-weight: bold;">
                        Возможен разворот импульса
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        elif classification['type'] == 'correction':
            if phase['phase'] == 'continuation':
                st.markdown("""
                <div style="
                    background: #f8d7da;
                    border: 3px solid #dc3545;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #721c24; font-size: 24px;">
                        🔴 ПРОДАЖА
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #721c24; font-size: 18px; font-weight: bold;">
                        Коррекция продолжается
                    </p>
                </div>
                """, unsafe_allow_html=True)
                self._show_impulse_trading_plan(symbol, 'sell')
            elif phase['phase'] == 'reversal':
                st.markdown("""
                <div style="
                    background: #d4edda;
                    border: 3px solid #28a745;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #155724; font-size: 24px;">
                        🟢 ПОКУПКА
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #155724; font-size: 18px; font-weight: bold;">
                        Коррекция завершается
                    </p>
                </div>
                """, unsafe_allow_html=True)
                self._show_impulse_trading_plan(symbol, 'buy')
            else:
                st.markdown("""
                <div style="
                    background: #d1ecf1;
                    border: 3px solid #17a2b8;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: center;
                ">
                    <h3 style="margin: 0; color: #0c5460; font-size: 24px;">
                        🔵 ОЖИДАНИЕ
                    </h3>
                    <p style="margin: 10px 0 0 0; color: #0c5460; font-size: 18px; font-weight: bold;">
                        Коррекция в процессе
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div style="
                background: #e2e3e5;
                border: 3px solid #6c757d;
                border-radius: 10px;
                padding: 25px;
                margin: 20px 0;
                text-align: center;
            ">
                <h3 style="margin: 0; color: #495057; font-size: 24px;">
                    ⚪ НЕЙТРАЛЬНО
                </h3>
                <p style="margin: 10px 0 0 0; color: #495057; font-size: 18px; font-weight: bold;">
                    Паттерн неясен, ждите четких сигналов
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Рекомендации по паттернам в красивых карточках
        if patterns['patterns']:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            ">
                <h3 style="margin: 0 0 15px 0; color: #495057; text-align: center;">
                    🎯 Рекомендации по паттернам
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            for pattern in patterns['patterns']:
                if pattern['type'] == 'triangle':
                    st.markdown("""
                    <div style="
                        background: #fff3cd;
                        border: 2px solid #ffeaa7;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                    ">
                        <h5 style="margin: 0; color: #856404;">🔺 Треугольник</h5>
                        <p style="margin: 5px 0 0 0; color: #856404; font-weight: bold;">
                            Ждите пробоя для входа
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                elif pattern['type'] == 'flag':
                    st.markdown("""
                    <div style="
                        background: #d4edda;
                        border: 2px solid #c3e6cb;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                    ">
                        <h5 style="margin: 0; color: #155724;">🏁 Флаг</h5>
                        <p style="margin: 5px 0 0 0; color: #155724; font-weight: bold;">
                            Продолжение тренда, входите по направлению
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                elif pattern['type'] == 'wedge':
                    st.markdown("""
                    <div style="
                        background: #f8d7da;
                        border: 2px solid #f5c6cb;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                    ">
                        <h5 style="margin: 0; color: #721c24;">🔺 Клин</h5>
                        <p style="margin: 5px 0 0 0; color: #721c24; font-weight: bold;">
                            Возможен разворот, будьте осторожны
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _show_impulse_trading_plan(self, symbol: str, direction: str):
        """Показывает план торговли для импульса"""
        
        # Получаем текущую цену
        if 'wave_data' in st.session_state:
            current_price = st.session_state.wave_data['Close'].iloc[-1]
        else:
            current_price = 50000  # Fallback
        
        if direction == 'buy':
            st.markdown("""
            <div style="
                background: #d4edda;
                border: 2px solid #c3e6cb;
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
            ">
                <h4 style="margin: 0 0 15px 0; color: #155724; text-align: center;">
                    📈 План покупки
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <h5 style="margin: 0 0 10px 0; color: #495057;">💰 Уровни входа и выхода</h5>
                    <p style="margin: 5px 0; color: #28a745; font-weight: bold;">
                        🎯 Вход: ${current_price:,.2f}
                    </p>
                    <p style="margin: 5px 0; color: #dc3545; font-weight: bold;">
                        🛑 Стоп-лосс: ${current_price * 0.95:,.2f} (-5%)
                    </p>
                    <p style="margin: 5px 0; color: #17a2b8; font-weight: bold;">
                        🎯 Тейк-профит 1: ${current_price * 1.10:,.2f} (+10%)
                    </p>
                    <p style="margin: 5px 0; color: #17a2b8; font-weight: bold;">
                        🎯 Тейк-профит 2: ${current_price * 1.20:,.2f} (+20%)
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <h5 style="margin: 0 0 10px 0; color: #495057;">📊 Стратегия</h5>
                    <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                        💡 Логика: Импульс продолжается, входим по тренду
                    </p>
                    <p style="margin: 5px 0; color: #495057;">
                        📈 Риск/Прибыль: 1:2 (консервативно)
                    </p>
                    <p style="margin: 5px 0; color: #495057;">
                        ⏰ Временной горизонт: 1-3 дня
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: #f8d7da;
                border: 2px solid #f5c6cb;
                border-radius: 8px;
                padding: 20px;
                margin: 15px 0;
            ">
                <h4 style="margin: 0 0 15px 0; color: #721c24; text-align: center;">
                    📉 План продажи
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <h5 style="margin: 0 0 10px 0; color: #495057;">💰 Уровни входа и выхода</h5>
                    <p style="margin: 5px 0; color: #dc3545; font-weight: bold;">
                        🎯 Вход: ${current_price:,.2f}
                    </p>
                    <p style="margin: 5px 0; color: #28a745; font-weight: bold;">
                        🛑 Стоп-лосс: ${current_price * 1.05:,.2f} (+5%)
                    </p>
                    <p style="margin: 5px 0; color: #17a2b8; font-weight: bold;">
                        🎯 Тейк-профит 1: ${current_price * 0.90:,.2f} (-10%)
                    </p>
                    <p style="margin: 5px 0; color: #17a2b8; font-weight: bold;">
                        🎯 Тейк-профит 2: ${current_price * 0.80:,.2f} (-20%)
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <h5 style="margin: 0 0 10px 0; color: #495057;">📊 Стратегия</h5>
                    <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                        💡 Логика: Коррекция продолжается, входим против тренда
                    </p>
                    <p style="margin: 5px 0; color: #495057;">
                        📉 Риск/Прибыль: 1:2 (консервативно)
                    </p>
                    <p style="margin: 5px 0; color: #495057;">
                        ⏰ Временной горизонт: 1-3 дня
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    def _show_retracement_trading_plan(self, symbol: str):
        """Показывает план торговли для отката"""
        
        st.markdown("""
        <div style="
            background: #d1ecf1;
            border: 2px solid #bee5eb;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        ">
            <h4 style="margin: 0 0 15px 0; color: #0c5460; text-align: center;">
                🔵 План для отката
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            ">
                <h5 style="margin: 0 0 10px 0; color: #495057;">⏳ Стратегия ожидания</h5>
                <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                    🕐 Ждите завершения отката
                </p>
                <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                    📈 Входите на пробое предыдущего максимума
                </p>
                <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                    📊 Используйте уровни Фибоначчи (38.2%, 50%, 61.8%)
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            ">
                <h5 style="margin: 0 0 10px 0; color: #495057;">🛡️ Управление рисками</h5>
                <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                    🛑 Стоп-лосс за минимумом отката
                </p>
                <p style="margin: 5px 0; color: #495057; font-weight: bold;">
                    💡 Логика: Откат - это возможность войти по лучшей цене
                </p>
                <p style="margin: 5px 0; color: #495057;">
                    ⚡ Патience - ключ к успеху
                </p>
            </div>
            """, unsafe_allow_html=True)
