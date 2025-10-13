"""
Модуль для ручного ввода данных о криптовалютах
Поддерживает загрузку CSV, Excel, ручной ввод и анализ изображений графиков
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import base64
from PIL import Image
import requests

# Попытка импорта cv2 (опционально)
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class ManualDataInput:
    """Класс для ручного ввода и загрузки данных о криптовалютах"""
    
    def __init__(self):
        self.data = None
        self.symbol = ""
        self.timeframe = "1d"
        
    def render_data_input_interface(self):
        """Главный интерфейс для ввода данных"""
        
        st.markdown("## 📊 Ввод данных о криптовалютах")
        st.info("""
        **Выберите способ ввода данных:**
        - 📁 **Загрузка файла** (CSV, Excel)
        - ✏️ **Ручной ввод** данных
        - 🖼️ **Анализ изображения** графика
        - 📋 **Шаблон** для заполнения
        """)
        
        # Выбор способа ввода
        input_method = st.radio(
            "🔧 Способ ввода данных:",
            ["📁 Загрузка файла", "✏️ Ручной ввод", "🖼️ Анализ изображения", "📋 Скачать шаблон"],
            horizontal=True
        )
        
        if input_method == "📁 Загрузка файла":
            self._render_file_upload()
        elif input_method == "✏️ Ручной ввод":
            self._render_manual_input()
        elif input_method == "🖼️ Анализ изображения":
            self._render_image_analysis()
        elif input_method == "📋 Скачать шаблон":
            self._render_template_download()
        
        return self.data
    
    def _render_file_upload(self):
        """Интерфейс загрузки файла"""
        st.markdown("### 📁 Загрузка файла")
        
        uploaded_file = st.file_uploader(
            "Выберите файл с данными",
            type=['csv', 'xlsx', 'xls'],
            help="Файл должен содержать колонки: Date, Open, High, Low, Close, Volume"
        )
        
        if uploaded_file is not None:
            try:
                # Определяем тип файла
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                # Проверяем наличие необходимых колонок
                required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                missing_columns = [col for col in required_columns if col not in data.columns]
                
                if missing_columns:
                    st.error(f"❌ Отсутствуют колонки: {', '.join(missing_columns)}")
                    st.info("📋 Скачайте шаблон для правильного формата")
                else:
                    # Обрабатываем данные
                    data = self._process_uploaded_data(data)
                    self.data = data
                    
                    st.success("✅ Данные успешно загружены!")
                    self._display_data_preview(data)
                    
            except Exception as e:
                st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
    
    def _render_manual_input(self):
        """Интерфейс ручного ввода"""
        st.markdown("### ✏️ Ручной ввод данных")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self.symbol = st.text_input("🪙 Символ криптовалюты", value="BTC-USD", help="Например: BTC-USD, ETH-USD")
            self.timeframe = st.selectbox("⏰ Таймфрейм", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"], index=5)
            
            num_points = st.number_input("📊 Количество точек", min_value=10, max_value=1000, value=100)
            
            if st.button("🎲 Сгенерировать случайные данные"):
                self.data = self._generate_random_data(num_points)
                st.success("✅ Сгенерированы случайные данные!")
        
        with col2:
            if st.button("📝 Ввести данные вручную"):
                self._render_data_entry_form()
    
    def _render_data_entry_form(self):
        """Форма для ввода данных по точкам"""
        st.markdown("#### 📝 Ввод данных по точкам")
        
        # Создаем форму для ввода
        with st.form("data_entry_form"):
            st.markdown("**Введите данные (минимум 10 точек):**")
            
            # Создаем колонки для ввода
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown("**Дата**")
            with col2:
                st.markdown("**Open**")
            with col3:
                st.markdown("**High**")
            with col4:
                st.markdown("**Low**")
            with col5:
                st.markdown("**Close**")
            with col6:
                st.markdown("**Volume**")
            
            # Создаем поля для ввода (примерно 20 строк)
            data_rows = []
            for i in range(20):
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                with col1:
                    date = st.date_input(f"Дата {i+1}", key=f"date_{i}", label_visibility="collapsed")
                with col2:
                    open_price = st.number_input(f"Open {i+1}", key=f"open_{i}", label_visibility="collapsed", format="%.2f")
                with col3:
                    high = st.number_input(f"High {i+1}", key=f"high_{i}", label_visibility="collapsed", format="%.2f")
                with col4:
                    low = st.number_input(f"Low {i+1}", key=f"low_{i}", label_visibility="collapsed", format="%.2f")
                with col5:
                    close = st.number_input(f"Close {i+1}", key=f"close_{i}", label_visibility="collapsed", format="%.2f")
                with col6:
                    volume = st.number_input(f"Volume {i+1}", key=f"volume_{i}", label_visibility="collapsed", format="%.0f")
                
                if open_price > 0:  # Если есть данные
                    data_rows.append({
                        'Date': date,
                        'Open': open_price,
                        'High': high,
                        'Low': low,
                        'Close': close,
                        'Volume': volume
                    })
            
            submitted = st.form_submit_button("💾 Сохранить данные")
            
            if submitted and len(data_rows) >= 10:
                # Создаем DataFrame
                data = pd.DataFrame(data_rows)
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
                data = data.sort_index()
                
                self.data = data
                st.success(f"✅ Сохранено {len(data_rows)} точек данных!")
                self._display_data_preview(data)
            elif submitted and len(data_rows) < 10:
                st.error("❌ Необходимо минимум 10 точек данных")
    
    def _render_image_analysis(self):
        """Интерфейс анализа изображения графика"""
        st.markdown("### 🖼️ Анализ изображения графика")
        st.info("""
        **Загрузите изображение графика для анализа:**
        - 📈 Скриншот с TradingView, Binance, Coinbase
        - 🖼️ Любое изображение с ценовым графиком
        - 📊 Система попытается извлечь данные о ценах
        """)
        
        uploaded_image = st.file_uploader(
            "Выберите изображение графика",
            type=['png', 'jpg', 'jpeg'],
            help="Загрузите скриншот ценового графика"
        )
        
        if uploaded_image is not None:
            try:
                # Показываем изображение
                image = Image.open(uploaded_image)
                st.image(image, caption="Загруженное изображение", use_column_width=True)
                
                # Анализируем изображение
                if st.button("🔍 Анализировать график"):
                    with st.spinner("Анализируем изображение..."):
                        extracted_data = self._analyze_chart_image(image)
                        
                        if extracted_data is not None:
                            self.data = extracted_data
                            st.success("✅ Данные успешно извлечены из изображения!")
                            self._display_data_preview(extracted_data)
                        else:
                            st.error("❌ Не удалось извлечь данные из изображения")
                            st.info("💡 Попробуйте загрузить более четкое изображение графика")
                            
            except Exception as e:
                st.error(f"❌ Ошибка при обработке изображения: {str(e)}")
    
    def _render_template_download(self):
        """Интерфейс скачивания шаблона"""
        st.markdown("### 📋 Шаблон для заполнения")
        
        # Создаем шаблон
        template_data = {
            'Date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
            'Open': np.random.uniform(40000, 50000, 30),
            'High': np.random.uniform(45000, 55000, 30),
            'Low': np.random.uniform(35000, 45000, 30),
            'Close': np.random.uniform(40000, 50000, 30),
            'Volume': np.random.uniform(1000000, 5000000, 30)
        }
        
        template_df = pd.DataFrame(template_data)
        
        st.markdown("**Пример данных (замените на свои):**")
        st.dataframe(template_df.head(10))
        
        # Создаем CSV для скачивания
        csv = template_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Скачать шаблон CSV",
            data=csv,
            file_name="crypto_data_template.csv",
            mime="text/csv"
        )
        
        st.info("""
        **Инструкция по заполнению:**
        1. 📥 Скачайте шаблон
        2. ✏️ Замените данные на реальные
        3. 💾 Сохраните файл
        4. 📁 Загрузите обратно в систему
        """)
    
    def _process_uploaded_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Обработка загруженных данных"""
        # Конвертируем дату
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.set_index('Date')
        
        # Сортируем по дате
        data = data.sort_index()
        
        # Добавляем технические индикаторы
        data = self._add_technical_indicators(data)
        
        return data
    
    def _generate_random_data(self, num_points: int) -> pd.DataFrame:
        """Генерация случайных данных для тестирования"""
        # Базовые параметры
        base_price = 50000
        volatility = 0.02
        
        # Генерируем даты
        dates = pd.date_range(start='2024-01-01', periods=num_points, freq='D')
        
        # Генерируем цены
        returns = np.random.normal(0, volatility, num_points)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Создаем OHLCV данные
        data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.lognormal(15, 1, num_points)
        }, index=dates)
        
        # Убеждаемся, что High >= max(Open, Close) и Low <= min(Open, Close)
        data['High'] = np.maximum(data['High'], np.maximum(data['Open'], data['Close']))
        data['Low'] = np.minimum(data['Low'], np.minimum(data['Open'], data['Close']))
        
        # Добавляем технические индикаторы
        data = self._add_technical_indicators(data)
        
        return data
    
    def _analyze_chart_image(self, image: Image.Image) -> Optional[pd.DataFrame]:
        """Анализ изображения графика (упрощенная версия)"""
        if not CV2_AVAILABLE:
            st.warning("⚠️ Модуль cv2 не установлен. Анализ изображений недоступен.")
            st.info("💡 Для анализа изображений установите: pip install opencv-python")
            st.info("💡 Или используйте ручной ввод или загрузку файлов")
            return None
        
        # Это упрощенная версия - в реальности нужен более сложный анализ
        st.warning("⚠️ Анализ изображений находится в разработке")
        st.info("💡 Пока используйте ручной ввод или загрузку файлов")
        
        # Возвращаем None, так как анализ изображений сложен
        return None
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Добавление технических индикаторов"""
        df = data.copy()
        
        # RSI
        df['RSI'] = self._calculate_rsi(df['Close'], 14)
        
        # MACD
        macd_data = self._calculate_macd(df['Close'])
        df['MACD'] = macd_data['MACD']
        df['MACD_Signal'] = macd_data['Signal']
        df['MACD_Histogram'] = macd_data['Histogram']
        
        # Bollinger Bands
        bb_data = self._calculate_bollinger_bands(df['Close'], 20, 2)
        df['BB_Upper'] = bb_data['Upper']
        df['BB_Lower'] = bb_data['Lower']
        df['BB_Middle'] = bb_data['Middle']
        
        # Волатильность
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Объем (нормализованный)
        df['Volume_Norm'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Расчет RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Расчет MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: float = 2):
        """Расчет полос Боллинджера"""
        middle = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'Upper': upper,
            'Lower': lower,
            'Middle': middle
        }
    
    def _display_data_preview(self, data: pd.DataFrame):
        """Отображение превью данных"""
        st.markdown("#### 📊 Превью данных")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📈 Записей", len(data))
        with col2:
            st.metric("📅 Период", f"{(data.index[-1] - data.index[0]).days} дней")
        with col3:
            st.metric("💰 Цена", f"${data['Close'].iloc[-1]:.2f}")
        with col4:
            price_change = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
            st.metric("📊 Изменение", f"{price_change:+.2f}%")
        
        # Показываем первые и последние записи
        st.markdown("**Первые 5 записей:**")
        st.dataframe(data.head())
        
        st.markdown("**Последние 5 записей:**")
        st.dataframe(data.tail())
        
        # Простой график
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Цена закрытия',
            line=dict(color='blue')
        ))
        
        fig.update_layout(
            title="График цены",
            xaxis_title="Дата",
            yaxis_title="Цена",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
