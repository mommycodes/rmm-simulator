"""
Модуль для получения данных о криптовалютах
Поддерживает различные источники данных
"""
import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

class CryptoDataFetcher:
    """Класс для получения данных о криптовалютах"""
    
    def __init__(self):
        self.available_symbols = {
            # Топовые
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD',
            'SOL': 'SOL-USD',
            'BNB': 'BNB-USD',
            'ADA': 'ADA-USD',
            'XRP': 'XRP-USD',
            'DOGE': 'DOGE-USD',
            'DOT': 'DOT-USD',
            'LTC': 'LTC-USD',
            'BCH': 'BCH-USD',
            'LINK': 'LINK-USD',
            'TRX': 'TRX-USD',

            'GRASS': 'GRASS-USD',
            'MNT': 'MNT-USD',
            'APT': 'APT-USD',
            'AVAX': 'AVAX-USD',
            'AAVE': 'AAVE-USD',
            '1INCH': '1INCH-USD',
            'OS': 'OS-USD',
            'OP': 'OP-USD',
            'INJ': 'INJ-USD',
            'SUI': 'SUI-USD',
            'SEI': 'SEI-USD',
            'ARB': 'ARB-USD',
            'ATOM': 'ATOM-USD',
            'FTM': 'FTM-USD',
            'NEAR': 'NEAR-USD',
            'PEPE': 'PEPE-USD',

            # Стейблкоины
            'USDT': 'USDT-USD',
            'USDC': 'USDC-USD',
            'DAI': 'DAI-USD',
            'TUSD': 'TUSD-USD',
        }
    
    def fetch_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Получение исторических данных криптовалюты
        
        Args:
            symbol: Символ криптовалюты
            period: Период данных
        
        Returns:
            DataFrame с историческими данными или None при ошибке
        """
        if not YFINANCE_AVAILABLE:
            st.error("""
            ❌ Модуль yfinance не установлен!
            
            Для работы с реальными данными установите:
            ```
            pip install yfinance
            ```
            
            Или используйте демо-данные для тестирования.
            """)
            return self._generate_demo_data(symbol, period)
        
        try:
            ticker = yf.Ticker(symbol)
            # Интервалы: 1h, 4h, 1d — передаем как есть (yfinance поддерживает эти значения)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                st.warning(f"Не удалось получить данные для {symbol}. Используем демо-данные.")
                return self._generate_demo_data(symbol, period)
            
            # Добавляем технические индикаторы
            data = self._add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            st.warning(f"Ошибка при получении данных: {str(e)}. Используем демо-данные.")
            return self._generate_demo_data(symbol, period)
    
    def _generate_demo_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Генерация демонстрационных данных для тестирования"""
        st.info("🎭 Используем демонстрационные данные для тестирования")
        
        # Определяем количество дней
        period_days = {
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730
        }.get(period, 365)
        
        # Генерируем даты
        dates = pd.date_range(start='2023-01-01', periods=period_days, freq='D')
        
        # Генерируем цены с трендом и волатильностью
        np.random.seed(42)  # Для воспроизводимости
        
        # Базовые параметры для разных криптовалют
        base_prices = {
            'BTC-USD': 30000,
            'ETH-USD': 2000,
            'SOL-USD': 100,
            'BNB-USD': 300,
            'ADA-USD': 0.5,
            'XRP-USD': 0.6,
            'DOGE-USD': 0.1,
            'DOT-USD': 7,
            'LTC-USD': 100,
            'BCH-USD': 200,
            'LINK-USD': 15,
            'TRX-USD': 0.12,
            'GRASS-USD': 1.0,
            'MNT-USD': 1.0,
            'APT-USD': 8.0,
            'AVAX-USD': 30.0,
            'AAVE-USD': 100.0,
            '1INCH-USD': 0.5,
            'OS-USD': 1.0,
            'OP-USD': 2.5,
            'INJ-USD': 25.0,
            'SUI-USD': 1.5,
            'SEI-USD': 0.5,
            'ARB-USD': 1.2,
            'ATOM-USD': 9.0,
            'FTM-USD': 0.6,
            'NEAR-USD': 4.0,
            'PEPE-USD': 0.00001,
            'USDT-USD': 1.0,
            'USDC-USD': 1.0,
            'DAI-USD': 1.0,
            'TUSD-USD': 1.0,
            'XLM-USD': 0.1,
        }
        
        base_price = base_prices.get(symbol, 1000)
        
        # Генерируем случайное блуждание с трендом
        returns = np.random.normal(0.001, 0.03, period_days)  # 0.1% средний дневной рост, 3% волатильность
        
        # Добавляем тренд
        trend = np.linspace(0, 0.2, period_days)  # 20% рост за период
        returns += trend / period_days
        
        # Генерируем цены
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Создаем OHLCV данные
        data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
            'Close': prices,
            'Volume': np.random.lognormal(15, 1, period_days)  # Логнормальное распределение для объема
        }, index=dates)
        
        # Убеждаемся, что High >= max(Open, Close) и Low <= min(Open, Close)
        data['High'] = np.maximum(data['High'], np.maximum(data['Open'], data['Close']))
        data['Low'] = np.minimum(data['Low'], np.minimum(data['Open'], data['Close']))
        
        # Добавляем технические индикаторы
        data = self._add_technical_indicators(data)
        
        return data
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Добавление технических индикаторов к данным"""
        df = data.copy()
        
        # RSI (Relative Strength Index)
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
        
        # Stochastic Oscillator
        stoch_data = self._calculate_stochastic(df['High'], df['Low'], df['Close'], 14, 3)
        df['Stoch_K'] = stoch_data['K']
        df['Stoch_D'] = stoch_data['D']
        
        # Williams %R
        df['Williams_R'] = self._calculate_williams_r(df['High'], df['Low'], df['Close'], 14)
        
        # CCI (Commodity Channel Index)
        df['CCI'] = self._calculate_cci(df['High'], df['Low'], df['Close'], 20)
        
        # ADX (Average Directional Index)
        adx_data = self._calculate_adx(df['High'], df['Low'], df['Close'], 14)
        df['ADX'] = adx_data['ADX']
        df['DI_Plus'] = adx_data['DI_Plus']
        df['DI_Minus'] = adx_data['DI_Minus']
        
        # Волатильность (стандартное отклонение за 20 дней)
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Объем (нормализованный)
        df['Volume_Norm'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # ATR (Average True Range)
        df['ATR'] = self._calculate_atr(df['High'], df['Low'], df['Close'], 14)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """RSI по Вильдеру (RMA-сглаживание)."""
        delta = prices.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        roll_up = gain.ewm(alpha=1 / window, adjust=False).mean()
        roll_down = loss.ewm(alpha=1 / window, adjust=False).mean()

        rs = roll_up / roll_down
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
    
    def get_available_symbols(self) -> Dict[str, str]:
        """Получение списка доступных символов"""
        return self.available_symbols.copy()
    
    def validate_symbol(self, symbol: str) -> bool:
        """Проверка валидности символа"""
        return symbol in self.available_symbols.values()
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3):
        """Расчет стохастического осциллятора"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'K': k_percent,
            'D': d_percent
        }
    
    def _calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
        """Расчет Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r
    
    def _calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20):
        """Расчет Commodity Channel Index"""
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        cci = (typical_price - sma_tp) / (0.015 * mad)
        return cci
    
    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
        """Расчет Average Directional Index"""
        # True Range
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Directional Movement
        dm_plus = high.diff()
        dm_minus = -low.diff()
        
        dm_plus = np.where((dm_plus > dm_minus) & (dm_plus > 0), dm_plus, 0)
        dm_minus = np.where((dm_minus > dm_plus) & (dm_minus > 0), dm_minus, 0)
        
        # Smoothed values
        atr = tr.rolling(window=period).mean()
        di_plus = 100 * (pd.Series(dm_plus).rolling(window=period).mean() / atr)
        di_minus = 100 * (pd.Series(dm_minus).rolling(window=period).mean() / atr)
        
        # ADX
        dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus)
        adx = dx.rolling(window=period).mean()
        
        return {
            'ADX': adx,
            'DI_Plus': di_plus,
            'DI_Minus': di_minus
        }
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
        """Расчет Average True Range"""
        tr1 = high - low
        tr2 = np.abs(high - close.shift(1))
        tr3 = np.abs(low - close.shift(1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        atr = tr.rolling(window=period).mean()
        return atr
