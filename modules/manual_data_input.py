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

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class ManualDataInput:
    
    def __init__(self):
        self.data = None
        self.symbol = ""
        self.timeframe = "1d"
        self.source = "manual"
        
    def render_interface(self):
        st.markdown("## 📊 Ручной ввод данных")
        
        input_method = st.radio(
            "Выберите способ ввода данных:",
            ["Ручной ввод", "Загрузка CSV", "Загрузка Excel", "Анализ изображения"],
            horizontal=True
        )
        
        if input_method == "Ручной ввод":
            self._render_manual_input()
        elif input_method == "Загрузка CSV":
            self._render_csv_upload()
        elif input_method == "Загрузка Excel":
            self._render_excel_upload()
        elif input_method == "Анализ изображения":
            self._render_image_analysis()
            
        if self.data is not None:
            self._render_data_preview()
            self._render_chart()
            
    def _render_manual_input(self):
        st.markdown("### ✏️ Ручной ввод данных")
        
        col1, col2 = st.columns(2)
        with col1:
            self.symbol = st.text_input("Символ", value="BTCUSDT", help="Например: BTCUSDT, ETHUSDT")
            self.timeframe = st.selectbox("Таймфрейм", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"])
            
        with col2:
            num_points = st.number_input("Количество точек", min_value=1, max_value=1000, value=50)
            
        st.markdown("#### Введите данные:")
        
        data_rows = []
        for i in range(num_points):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                timestamp = st.text_input(f"Время {i+1}", value=f"2024-01-{i+1:02d}", key=f"time_{i}")
            with col2:
                open_price = st.number_input(f"Open {i+1}", value=50000.0, key=f"open_{i}")
            with col3:
                high_price = st.number_input(f"High {i+1}", value=51000.0, key=f"high_{i}")
            with col4:
                low_price = st.number_input(f"Low {i+1}", value=49000.0, key=f"low_{i}")
            with col5:
                close_price = st.number_input(f"Close {i+1}", value=50500.0, key=f"close_{i}")
                
            data_rows.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price
            })
            
        if st.button("📊 Создать данные"):
            self.data = pd.DataFrame(data_rows)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            self.source = "manual"
            st.success("Данные созданы!")
            
    def _render_csv_upload(self):
        st.markdown("### 📁 Загрузка CSV")
        
        uploaded_file = st.file_uploader("Выберите CSV файл", type=['csv'])
        
        if uploaded_file is not None:
            try:
                self.data = pd.read_csv(uploaded_file)
                
                col1, col2 = st.columns(2)
                with col1:
                    self.symbol = st.text_input("Символ", value="BTCUSDT")
                with col2:
                    self.timeframe = st.selectbox("Таймфрейм", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"])
                
                self.source = "csv"
                st.success("CSV файл загружен!")
                
            except Exception as e:
                st.error(f"Ошибка при загрузке CSV: {e}")
                
    def _render_excel_upload(self):
        st.markdown("### 📊 Загрузка Excel")
        
        uploaded_file = st.file_uploader("Выберите Excel файл", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                self.data = pd.read_excel(uploaded_file)
                
                col1, col2 = st.columns(2)
                with col1:
                    self.symbol = st.text_input("Символ", value="BTCUSDT")
                with col2:
                    self.timeframe = st.selectbox("Таймфрейм", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"])
                
                self.source = "excel"
                st.success("Excel файл загружен!")
                
            except Exception as e:
                st.error(f"Ошибка при загрузке Excel: {e}")
                
    def _render_image_analysis(self):
        st.markdown("### 🖼️ Анализ изображения графика")
        
        if not CV2_AVAILABLE:
            st.warning("OpenCV не установлен. Установите: pip install opencv-python")
            return
            
        uploaded_image = st.file_uploader("Загрузите изображение графика", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Загруженное изображение", use_container_width=True)
            
            if st.button("🔍 Анализировать изображение"):
                with st.spinner("Анализируем изображение..."):
                    try:
                        self.data = self._analyze_chart_image(image)
                        self.source = "image"
                        st.success("Изображение проанализировано!")
                    except Exception as e:
                        st.error(f"Ошибка анализа: {e}")
                        
    def _analyze_chart_image(self, image: Image.Image) -> pd.DataFrame:
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        edges = cv2.Canny(gray, 50, 150)
        
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
        
        if lines is not None:
            data_points = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                price = (y1 + y2) / 2
                data_points.append({
                    'timestamp': f"2024-01-{len(data_points)+1:02d}",
                    'open': price,
                    'high': price * 1.01,
                    'low': price * 0.99,
                    'close': price
                })
                
            df = pd.DataFrame(data_points)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
            
    def _render_data_preview(self):
        st.markdown("### 📋 Предварительный просмотр данных")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Символ", self.symbol)
        with col2:
            st.metric("Таймфрейм", self.timeframe)
        with col3:
            st.metric("Количество точек", len(self.data))
            
        st.dataframe(self.data.head(10))
        
    def _render_chart(self):
        st.markdown("### 📈 График данных")
        
        fig = go.Figure(data=go.Candlestick(
            x=self.data['timestamp'],
            open=self.data['open'],
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close']
        ))
        
        fig.update_layout(
            title=f"{self.symbol} - {self.timeframe}",
            xaxis_title="Время",
            yaxis_title="Цена",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    def get_data(self) -> Optional[pd.DataFrame]:
        return self.data
        
    def get_symbol(self) -> str:
        return self.symbol
        
    def get_timeframe(self) -> str:
        return self.timeframe
        
    def get_source(self) -> str:
        return self.source