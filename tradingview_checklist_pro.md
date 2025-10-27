# TradingView Pine Script - Чек-лист трейдера (Профессиональная версия)

## Описание
Компактный индикатор для TradingView с основными пунктами чек-листа трейдера (100 баллов максимум).

## Код Pine Script v6

```pinescript
//@version=6
indicator("🛡️ Чек-лист трейдера RMM", overlay=true)

// ========== НАСТРОЙКИ ==========
// Волновой анализ (46 баллов)
manual_ew_5waves = input.bool(false, "5 волн по канону (3 не самая короткая, чередование коррекций)", group="🌊 Волновой анализ")
manual_fib_161_227 = input.bool(false, "Удлинение по Фибоначчи 161-227", group="🌊 Волновой анализ")
manual_fib_227_261 = input.bool(false, "Удлинение по Фибоначчи 227-261", group="🌊 Волновой анализ")
manual_flag_5w = input.bool(false, "5 волн + наклонка в 5й + ретест фибы 50% (флаг)", group="🌊 Волновой анализ")

// Технический анализ (20 баллов)
manual_trend_break = input.bool(false, "Пробитие линии тренда", group="📊 Технический анализ")
manual_trend = input.bool(false, "Движение по тренду", group="📊 Технический анализ")
manual_btc_trend = input.bool(false, "Движение по тренду с BTC", group="📊 Технический анализ")
manual_liquidity = input.bool(false, "Движение в зоны ликвидности (50x / 100x)", group="📊 Технический анализ")

// Smart Money (18 баллов)
manual_student = input.bool(false, "Сигнал от Student на 1 минутке", group="💡 Smart Money")
manual_smt_div = input.bool(false, "SMT-дивергенция", group="💡 Smart Money")
manual_rsi_div = input.bool(false, "Дивергенция RSI", group="💡 Smart Money")
manual_cci_div = input.bool(false, "Дивергенция CCI", group="💡 Smart Money")
manual_against_crowd = input.bool(false, "Действие ПРОТИВ толпы", group="💡 Smart Money")

// Ликвидность (9 баллов)
manual_funding = input.bool(false, "Фандинг противоположный", group="💧 Ликвидность")
manual_volume = input.bool(false, "Объемы на текущем ТФ", group="💧 Ликвидность")

// Риск (9 баллов)
manual_no_wick = input.bool(false, "НЕ КИНЖАЛ", group="🛡️ Риск")
manual_tp = input.bool(false, "Более 1,5% TakeProfit", group="🛡️ Риск")
manual_rrr = input.bool(false, "РММ соблюден 1:1 МИНИМУМ", group="🛡️ Риск")

// Параметры
rsi_length = input.int(14, "RSI длина", group="⚙️ Параметры")

// ========== РАСЧЕТЫ ==========
rsi = ta.rsi(close, rsi_length)
cci = ta.cci(close, 14)

// Дивергенция RSI
rsi_high = ta.highest(rsi, 5)
rsi_low = ta.lowest(rsi, 5)
price_high = ta.highest(high, 5)
price_low = ta.lowest(low, 5)

rsi_bullish_div = rsi[1] > rsi[2] and rsi[1] < rsi[0] and price_high[1] < price_high[2]
rsi_bearish_div = rsi[1] < rsi[2] and rsi[1] > rsi[0] and price_low[1] > price_low[2]

// Дивергенция CCI
cci_high = ta.highest(cci, 5)
cci_low = ta.lowest(cci, 5)

cci_bullish_div = cci[1] > cci[2] and cci[1] < cci[0] and price_high[1] < price_high[2]
cci_bearish_div = cci[1] < cci[2] and cci[1] > cci[0] and price_low[1] > price_low[2]

// SMT-дивергенция (упрощенная)
smt_bullish = high[1] > high[2] and rsi[1] < rsi[2] and rsi[1] < rsi[0]
smt_bearish = low[1] < low[2] and rsi[1] > rsi[2] and rsi[1] > rsi[0]

// ========== БАЛЛЫ ==========
// Волновой анализ (46 баллов)
score_ew = manual_ew_5waves ? 18 : 0
score_fib1 = manual_fib_161_227 ? 9 : 0
score_fib2 = manual_fib_227_261 ? 9 : 0
score_flag = manual_flag_5w ? 10 : 0

// Технический анализ (20 баллов)
score_trend_break = manual_trend_break ? 7 : 0
score_trend = manual_trend ? 7 : 0
score_btc_trend = manual_btc_trend ? 4 : 0
score_liquidity = manual_liquidity ? 2 : 0

// Smart Money (18 баллов)
score_student = manual_student ? 4 : 0
score_smt = manual_smt_div ? 4 : 0
score_rsi = manual_rsi_div ? 2 : 0
score_cci = manual_cci_div ? 2 : 0
score_crowd = manual_against_crowd ? 6 : 0

// Ликвидность (9 баллов)
score_funding = manual_funding ? 5 : 0
score_volume = manual_volume ? 4 : 0

// Риск (9 баллов)
score_no_wick = manual_no_wick ? 2 : 0
score_tp = manual_tp ? 3 : 0
score_rrr = manual_rrr ? 4 : 0

// Общий счет
total_score = score_ew + score_fib1 + score_fib2 + score_flag +
              score_trend_break + score_trend + score_btc_trend + score_liquidity +
              score_student + score_smt + score_rsi + score_cci + score_crowd +
              score_funding + score_volume +
              score_no_wick + score_tp + score_rrr

// ========== ЦВЕТА ==========
txt = color.white
okCol = color.lime
badCol = color.red
warnCol = color.orange
hdrBg = color.new(#1a1a1a, 0)
tblBg = color.new(#2d2d2d, 0)

// ========== ТАБЛИЦА ==========
var table T = table.new(position.bottom_left, 4, 22, bgcolor=tblBg, border_width=1, border_color=color.gray)

// Функция для строки
f_set_row(row, title, maxPts, enabled, score, note) =>
    status = enabled ? "✅ " + str.tostring(score) : "❌ 0"
    statusColor = enabled ? okCol : badCol
    
    table.cell(T, 0, row, title, text_color=txt, text_size=size.small)
    table.cell(T, 1, row, str.tostring(maxPts), text_color=txt, text_size=size.small)
    table.cell(T, 2, row, status, text_color=statusColor, text_size=size.small)
    table.cell(T, 3, row, note, text_color=txt, text_size=size.small)

// Рисуем только на последнем баре
if barstate.islast
    // Заголовок
    table.cell(T, 0, 0, "🛡️ Чек-лист трейдера", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 1, 0, "Баллы", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 2, 0, "Статус", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 3, 0, "Примечание", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    
    // Волновой анализ
    table.cell(T, 0, 1, "🌊 Волновой анализ", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    table.cell(T, 1, 1, "46", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    table.cell(T, 2, 1, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    table.cell(T, 3, 1, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    
    f_set_row(2, "5 волн по канону", 18, manual_ew_5waves, score_ew, "Основа сетапа")
    f_set_row(3, "Фибо 161-227", 9, manual_fib_161_227, score_fib1, "Подтверждение тренда")
    f_set_row(4, "Фибо 227-261", 9, manual_fib_227_261, score_fib2, "Подтверждение тренда")
    f_set_row(5, "Флаг (5волн+накл+фиб50%)", 10, manual_flag_5w, score_flag, "Идеальный сетап")
    
    // Технический анализ
    table.cell(T, 0, 6, "📊 Технический анализ", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 1, 6, "20", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 2, 6, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 3, 6, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    
    f_set_row(7, "Пробитие линии тренда", 7, manual_trend_break, score_trend_break, "Смена направления")
    f_set_row(8, "Движение по тренду", 7, manual_trend, score_trend, "Следование за трендом")
    f_set_row(9, "Тренд с BTC", 4, manual_btc_trend, score_btc_trend, "Альты следуют за BTC")
    f_set_row(10, "Зоны ликвидности", 2, manual_liquidity, score_liquidity, "Стопы и ликвидации")
    
    // Smart Money
    table.cell(T, 0, 11, "💡 Smart Money", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 1, 11, "18", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 2, 11, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 3, 11, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    
    f_set_row(12, "Student 1м", 4, manual_student, score_student, "Подтверждение 3 волны")
    f_set_row(13, "SMT-дивергенция", 4, manual_smt_div, score_smt, "Ранний сигнал разворота")
    f_set_row(14, "RSI дивергенция", 2, manual_rsi_div, score_rsi, "Ранний сигнал")
    f_set_row(15, "CCI дивергенция", 2, manual_cci_div, score_cci, "Ранний сигнал")
    f_set_row(16, "Действие ПРОТИВ толпы", 6, manual_against_crowd, score_crowd, "Против ожиданий толпы")
    
    // Ликвидность
    table.cell(T, 0, 17, "💧 Ликвидность", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 1, 17, "9", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 2, 17, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 3, 17, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    
    f_set_row(18, "Фандинг противоположный", 5, manual_funding, score_funding, "Фундаментальный фактор")
    f_set_row(19, "Объемы на ТФ", 4, manual_volume, score_volume, "Сила движения")
    
    // Риск
    table.cell(T, 0, 20, "🛡️ Риск", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 1, 20, "9", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 2, 20, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 3, 20, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    
    f_set_row(21, "НЕ КИНЖАЛ", 2, manual_no_wick, score_no_wick, "Без резких теней")
    f_set_row(22, "TP > 1.5%", 3, manual_tp, score_tp, "Адекватное RR")
    f_set_row(23, "РММ 1:1 МИНИМУМ", 4, manual_rrr, score_rrr, "Минимальное требование")
    
    // Итоговая оценка
    table.cell(T, 0, 24, "🎯 ИТОГО", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 1, 24, "100", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    
    // Определяем уровень
    level = total_score >= 70 ? "КЛАССИКА" : total_score >= 60 ? "ЛУДКА" : "СЛАБО"
    statusText = total_score >= 70 ? "✅ " + str.tostring(total_score) + " (СИЛЬНЫЙ)" : 
                 total_score >= 60 ? "⚠️ " + str.tostring(total_score) + " (СРЕДНИЙ)" : 
                 "❌ " + str.tostring(total_score) + " (СЛАБЫЙ)"
    
    table.cell(T, 2, 24, statusText, text_color=total_score >= 70 ? okCol : total_score >= 60 ? warnCol : badCol, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 3, 24, level, text_color=txt, text_size=size.normal, bgcolor=hdrBg)

// ========== ВИЗУАЛИЗАЦИЯ ДИВЕРГЕНЦИЙ ==========
if rsi_bullish_div
    label.new(bar_index, low, "RSI↗", color=color.green, textcolor=color.white, style=label.style_label_up, size=size.small)

if rsi_bearish_div
    label.new(bar_index, high, "RSI↘", color=color.red, textcolor=color.white, style=label.style_label_down, size=size.small)

if cci_bullish_div
    label.new(bar_index, low, "CCI↗", color=color.blue, textcolor=color.white, style=label.style_label_up, size=size.small)

if cci_bearish_div
    label.new(bar_index, high, "CCI↘", color=color.orange, textcolor=color.white, style=label.style_label_down, size=size.small)

if smt_bullish
    label.new(bar_index, low, "SMT↗", color=color.purple, textcolor=color.white, style=label.style_label_up, size=size.small)

if smt_bearish
    label.new(bar_index, high, "SMT↘", color=color.fuchsia, textcolor=color.white, style=label.style_label_down, size=size.small)

// ========== АЛЕРТЫ ==========
if total_score >= 70
    alert("🎯 Высокий балл чек-листа: " + str.tostring(total_score) + "/100", alert.freq_once_per_bar)

if rsi_bullish_div or rsi_bearish_div
    alert("📊 Обнаружена дивергенция RSI", alert.freq_once_per_bar)

if cci_bullish_div or cci_bearish_div
    alert("📊 Обнаружена дивергенция CCI", alert.freq_once_per_bar)

if smt_bullish or smt_bearish
    alert("📊 Обнаружена SMT-дивергенция", alert.freq_once_per_bar)
```

## Особенности версии

### ✅ **Структура баллов (100 баллов максимум):**
- **🌊 Волновой анализ:** 46 баллов (18+9+9+10)
- **📊 Технический анализ:** 20 баллов (7+7+4+2)
- **💡 Smart Money:** 18 баллов (4+4+2+2+6)
- **💧 Ликвидность:** 9 баллов (5+4)
- **🛡️ Риск:** 9 баллов (2+3+4)

### 📊 **Пункты чек-листа:**
- **5 волн по канону** — 18 баллов (ПРИОРИТЕТ)
- **Удлинение по фибе 161-227** — 9 баллов
- **Удлинение по фибе 227-261** — 9 баллов
- **Флаг (5волн+накл+фиб50%)** — 10 баллов
- **Пробитие линии тренда** — 7 баллов
- **Движение по тренду** — 7 баллов
- **Тренд с BTC** — 4 балла
- **Сигнал от Student** — 4 балла
- **SMT-дивергенция** — 4 балла
- **Действие ПРОТИВ толпы** — 6 баллов
- **РММ 1:1 МИНИМУМ** — 4 балла

### 🎯 **Пороговые значения:**
- **Классика:** 70+ баллов (зеленый)
- **Лудка:** 60-69 баллов (оранжевый)
- **Слабо:** <60 баллов (красный)

Готово к использованию! 🚀