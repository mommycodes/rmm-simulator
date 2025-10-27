# TradingView Pine Script - Чек-лист трейдера (Профессиональная версия)

## Описание
Компактный индикатор для TradingView с основными пунктами чек-листа трейдера.

## Код Pine Script v6

```pinescript
//@version=6
indicator("🛡️ Чек-лист трейдера RMM", overlay=true)

// ========== НАСТРОЙКИ ==========
// Волновой анализ
manual_ew_5waves = input.bool(false, "5 волн (3 не самая короткая, чередование коррекций)", group="🌊 Волновой анализ")
manual_fib_161_227 = input.bool(false, "Удлинение по Фибоначчи 161-227", group="🌊 Волновой анализ")
manual_fib_227_261 = input.bool(false, "Удлинение по Фибоначчи 227-261", group="🌊 Волновой анализ")
manual_flag_5w = input.bool(false, "5 волн + наклонка в 5й + ретест фибы 50% (флаг)", group="🌊 Волновой анализ")

// Индикаторы
manual_student = input.bool(false, "Сигнал от Student на 1 минутке", group="🎛 Индикаторы")
manual_rsi_div = input.bool(false, "Дивергенция RSI", group="🎛 Индикаторы")
manual_cci_div = input.bool(false, "Дивергенция CCI", group="🎛 Индикаторы")

// Ликвидность
manual_funding = input.bool(false, "Фандинг противоположный", group="💧 Ликвидность")
manual_volume = input.bool(false, "Объемы на текущем ТФ", group="💧 Ликвидность")

// Тренд
manual_trend = input.bool(false, "Торгуем по тренду", group="🚀 Тренд")
manual_btc_trend = input.bool(false, "Торгуем по тренду BTC", group="🚀 Тренд")

// Риск
manual_no_wick = input.bool(false, "НЕ КИНЖАЛ", group="🛡️ Риск")
manual_tp = input.bool(false, "Более 1,5% TakeProfit", group="🛡️ Риск")
manual_rrr = input.bool(false, "РММ соблюден 1:1 МИНИМУМ", group="🛡️ Риск")

// Параметры
rsi_length = input.int(14, "RSI длина", group="⚙️ Параметры")
rsi_min = input.int(20, "RSI мин", group="⚙️ Параметры")
rsi_max = input.int(80, "RSI макс", group="⚙️ Параметры")

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

// ========== БАЛЛЫ ==========
// Волновой анализ (45 баллов)
score_ew = manual_ew_5waves ? 20 : 0
score_fib1 = manual_fib_161_227 ? 8 : 0
score_fib2 = manual_fib_227_261 ? 8 : 0
score_flag = manual_flag_5w ? 9 : 0

// Индикаторы (15 баллов)
score_student = manual_student ? 5 : 0
score_rsi_div = manual_rsi_div ? 5 : 0
score_cci_div = manual_cci_div ? 5 : 0

// Ликвидность (14 баллов)
score_funding = manual_funding ? 7 : 0
score_volume = manual_volume ? 7 : 0

// Тренд (24 балла)
score_trend = manual_trend ? 12 : 0
score_btc_trend = manual_btc_trend ? 12 : 0

// Риск (9 баллов)
score_no_wick = manual_no_wick ? 2 : 0
score_tp = manual_tp ? 3 : 0
score_rrr = manual_rrr ? 4 : 0

// Общий счет
total_score = score_ew + score_fib1 + score_fib2 + score_flag +
              score_student + score_rsi_div + score_cci_div +
              score_funding + score_volume +
              score_trend + score_btc_trend +
              score_no_wick + score_tp + score_rrr

// ========== ЦВЕТА ==========
txt = color.white
okCol = color.lime
badCol = color.red
warnCol = color.orange
hdrBg = color.new(#1a1a1a, 0)
tblBg = color.new(#2d2d2d, 0)

// ========== ТАБЛИЦА ==========
var table T = table.new(position.bottom_left, 4, 17, bgcolor=tblBg, border_width=1, border_color=color.gray)

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
    table.cell(T, 1, 1, "45", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    table.cell(T, 2, 1, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    table.cell(T, 3, 1, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#1e3a8a, 50))
    
    f_set_row(2, "5 волн по канону", 20, manual_ew_5waves, score_ew, "Основа сетапа")
    f_set_row(3, "Фибо 161-227", 8, manual_fib_161_227, score_fib1, "Подтверждение тренда")
    f_set_row(4, "Фибо 227-261", 8, manual_fib_227_261, score_fib2, "Подтверждение тренда")
    f_set_row(5, "Флаг (5волн+накл+фиб50%)", 9, manual_flag_5w, score_flag, "Идеальный сетап")
    
    // Индикаторы
    table.cell(T, 0, 6, "🎛 Индикаторы", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 1, 6, "15", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 2, 6, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 3, 6, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    
    f_set_row(7, "Student 1м", 5, manual_student, score_student, "Подтверждение 3 волны")
    f_set_row(8, "RSI дивергенция", 5, manual_rsi_div, score_rsi_div, "Ранний сигнал")
    f_set_row(9, "CCI дивергенция", 5, manual_cci_div, score_cci_div, "Ранний сигнал")
    
    // Ликвидность
    table.cell(T, 0, 10, "💧 Ликвидность", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 1, 10, "14", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 2, 10, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    table.cell(T, 3, 10, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#065f46, 50))
    
    f_set_row(11, "Фандинг противоположный", 7, manual_funding, score_funding, "Фундаментальный фактор")
    f_set_row(12, "Объемы на ТФ", 7, manual_volume, score_volume, "Сила движения")
    
    // Тренд
    table.cell(T, 0, 13, "🚀 Тренд", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 1, 13, "24", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 2, 13, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    table.cell(T, 3, 13, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#7c2d12, 50))
    
    f_set_row(14, "Торгуем по тренду", 12, manual_trend, score_trend, "Следование за трендом")
    f_set_row(15, "Торгуем по тренду BTC", 12, manual_btc_trend, score_btc_trend, "Альты следуют за BTC")
    
    // Риск
    table.cell(T, 0, 16, "🛡️ Риск", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 1, 16, "9", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 2, 16, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    table.cell(T, 3, 16, "", text_color=color.yellow, text_size=size.small, bgcolor=color.new(#991b1b, 50))
    
    f_set_row(17, "НЕ КИНЖАЛ", 2, manual_no_wick, score_no_wick, "Без резких теней")
    f_set_row(18, "TP > 1.5%", 3, manual_tp, score_tp, "Адекватное RR")
    f_set_row(19, "РММ 1:1 МИНИМУМ", 4, manual_rrr, score_rrr, "Минимальное требование")
    
    // Итоговая оценка
    table.cell(T, 0, 20, "🎯 ИТОГО", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 1, 20, "100", text_color=txt, text_size=size.normal, bgcolor=hdrBg)
    
    // Определяем уровень
    level = total_score >= 70 ? "КЛАССИКА" : total_score >= 60 ? "ЛУДКА" : "СЛАБО"
    statusText = total_score >= 70 ? "✅ " + str.tostring(total_score) + " (СИЛЬНЫЙ)" : 
                 total_score >= 60 ? "⚠️ " + str.tostring(total_score) + " (СРЕДНИЙ)" : 
                 "❌ " + str.tostring(total_score) + " (СЛАБЫЙ)"
    
    table.cell(T, 2, 20, statusText, text_color=total_score >= 70 ? okCol : total_score >= 60 ? warnCol : badCol, text_size=size.normal, bgcolor=hdrBg)
    table.cell(T, 3, 20, level, text_color=txt, text_size=size.normal, bgcolor=hdrBg)

// ========== ВИЗУАЛИЗАЦИЯ ДИВЕРГЕНЦИЙ ==========
if rsi_bullish_div
    label.new(bar_index, low, "RSI↗", color=color.green, textcolor=color.white, style=label.style_label_up, size=size.small)

if rsi_bearish_div
    label.new(bar_index, high, "RSI↘", color=color.red, textcolor=color.white, style=label.style_label_down, size=size.small)

if cci_bullish_div
    label.new(bar_index, low, "CCI↗", color=color.blue, textcolor=color.white, style=label.style_label_up, size=size.small)

if cci_bearish_div
    label.new(bar_index, high, "CCI↘", color=color.orange, textcolor=color.white, style=label.style_label_down, size=size.small)

// ========== АЛЕРТЫ ==========
if total_score >= 70
    alert("🎯 Высокий балл чек-листа: " + str.tostring(total_score) + "/100", alert.freq_once_per_bar)

if rsi_bullish_div or rsi_bearish_div
    alert("📊 Обнаружена дивергенция RSI", alert.freq_once_per_bar)

if cci_bullish_div or cci_bearish_div
    alert("📊 Обнаружена дивергенция CCI", alert.freq_once_per_bar)
```

## Особенности версии

### ✅ **Структура баллов (100 баллов максимум):**
- **🌊 Волновой анализ:** 45 баллов (20+8+8+9)
- **🎛 Индикаторы:** 15 баллов (5+5+5)
- **💧 Ликвидность:** 14 баллов (7+7)
- **🚀 Тренд:** 24 балла (12+12)
- **🛡️ Риск:** 9 баллов (2+3+4)

### 📊 **Пункты чек-листа:**
- **5 волн (3 не самая короткая, чередование коррекций)** — 20 баллов
- **Удлинение по фибе 161-227** — 8 баллов
- **Удлинение по фибе 227-261** — 8 баллов
- **5 волн + наклонка в 5й + ретест фибы 50% (флаг)** — 9 баллов
- **Торгуем по тренду** — 12 баллов
- **Торгуем по тренду BTC** — 12 баллов
- **Объемы на ТФ** — 7 баллов
- **Фандинг противоположный** — 7 баллов
- **Дивер RSI** — 5 баллов
- **Дивер CCI** — 5 баллов
- **Сигнал от студента на 1 минутке** — 5 баллов

### 🎯 **Пороговые значения:**
- **Классика:** 70+ баллов
- **Лудка:** 60-69 баллов
- **Слабо:** <60 баллов

Готово к использованию! 🚀
