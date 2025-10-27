import streamlit as st
import time
from datetime import datetime, timedelta

# === Конфигурация чек-листа с разделами и баллами ===
# Система уровней: Классика (70+), Продвинутый (70+), Лудка (60+)
CHECKLIST_SECTIONS = {
    "🌊 Волновой анализ": {
        "5 волн по канону (3 не самая короткая, чередование коррекций)": (18, "Основа сетапа - ПРИОРИТЕТ", "⚠️ Кроме 5 волн в коррекциях меньшего ТФ"),
        "Удлинение по Фибоначчи 161-227": (9, "Подтверждение окончания тренда", "⚠️ Сильные выбросы цены могут исказить проекцию"),
        "Удлинение по Фибоначчи 227-261": (9, "Подтверждение окончания тренда", "⚠️ Сильные выбросы цены могут исказить проекцию"),
        "5 волн + наклонка в 5й + ретест фибы 50% (флаг)": (10, "Идеальный сетап", "⚠️ Ложные пробои при низкой ликвидности"),
    },
    "📊 Технический анализ": {
        "Пробитие линии тренда": (7, "Ключевой сигнал смены направления", "⚠️ Ложные пробои при боковике"),
        "Движение по тренду": (7, "Следование за глобальным трендом", "⚠️ Тренд не подтвержден старшими ТФ"),
        "Движение по тренду с BTC": (4, "Альты следуют за BTC", "⚠️ Не входить если BTC движется аномально"),
        "Движение в зоны ликвидности (50x / 100x)": (2, "Цена стремится к стопам и ликвидациям", "⚠️ Не входить если объемы и ликвидность слишком аномальные"),
    },
    "💡 Smart Money": {
        "Сигнал от Student на 1 минутке": (4, "Подтверждение 3 волны", "⚠️ Слабый тренд — сигнал может быть ложным"),
        "SMT-дивергенция": (4, "Ранний сигнал разворота", "⚠️ ПРИ СИЛЬНОМ ИМПУЛЬСЕ/ПРОЛИВЕ ДИВЕР НЕ РАБОТАЕТ"),
        "Дивергенция RSI": (2, "Ранний сигнал", "⚠️ ПРИ СИЛЬНОМ ИМПУЛЬСЕ/ПРОЛИВЕ ДИВЕР НЕ РАБОТАЕТ"),
        "Дивергенция CCI": (2, "Ранний сигнал", "⚠️ ПРИ СИЛЬНОМ ИМПУЛЬСЕ/ПРОЛИВЕ ДИВЕР НЕ РАБОТАЕТ"),
        "Действие ПРОТИВ толпы": (6, "Ожидания толпы - действуем наоборот", "⚠️ Если страх высок - покупаем, если жадность высока - продаем"),
    },
    "💧 Ликвидность и объёмы": {
        "Фандинг противоположный": (5, "Фундаментальный фактор", "⚠️ Учитывать направление фандинга"),
        "Объемы на текущем ТФ": (4, "Подтверждает силу движения", "⚠️ Объем может быть ложным при новостных выбросах"),
    },
    "🛡️ Риск и фильтры": {
        "НЕ КИНЖАЛ": (2, "Цена НЕ должна двигаться резкими тенями без структуры", "⚠️ Ложные сигналы при всплесках ликвидности"),
        "Более 1,5% TakeProfit": (3, "Цель сделки — адекватное RR", "⚠️ Не входить если RR слишком мал или слишком большой"),
        "РММ соблюден 1:1 МИНИМУМ": (4, "Соотношение риск/прибыль не менее 1:1", "⚠️ Минимальное требование для безопасной торговли"),
    }
}

# Пороги для разных уровней торговли
TRADING_LEVELS = {
    "Классика": 70,
    "Продвинутый": 70, 
    "Лудка": 60
}

MAX_SCORE = sum(weight for section in CHECKLIST_SECTIONS.values() for weight, _, _ in section.values())

def render_checklist_entry():
    st.markdown("<h2 style='text-align:center;'>🛡️ Чек-лист трейдера</h2>", unsafe_allow_html=True)
    st.caption("⚡ Заполни чек-лист, подожди 10 минут и только потом входи в сделку — не спеши, ликвидация всегда приходит незаметно")

    # --- Инициализация состояния ---
    if "checklist" not in st.session_state:
        st.session_state.checklist = {key: False for section in CHECKLIST_SECTIONS.values() for key in section.keys()}
    if "evaluated" not in st.session_state:
        st.session_state.evaluated = False
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_started" not in st.session_state:
        st.session_state.timer_started = False

    # --- Чеклист ---
    st.markdown("### 📋 Отметь условия входа")
    total_score = 0
    for section_name, items in CHECKLIST_SECTIONS.items():
        st.markdown(f"<hr style='border:1px solid #ddd; margin:10px 0'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-weight:bold; color:#2e7d32; margin-bottom:5px;'>{section_name}</h4>", unsafe_allow_html=True)
        for key, (weight, hint, warning) in items.items():
            tooltip = f"{hint}\n{warning}" if warning else hint
            
            checked = st.checkbox(
                f"{key}", 
                value=st.session_state.checklist[key], 
                help=tooltip,
                key=key
            )
            st.session_state.checklist[key] = checked
            if checked:
                total_score += weight


    # --- Кнопка оценки сделки ---
    if st.button("📊 Оценить сделку"):
        st.session_state.evaluated = True
        percent = int((total_score / MAX_SCORE) * 100)

        st.markdown("### 📈 Итоговая оценка сделки")
        progress_bar = st.progress(0)
        status = st.empty()

        for i in range(percent + 1):
            progress_bar.progress(i)
            status.text(f"Заполняем чек-лист: {i}%")
            time.sleep(0.02)

        st.markdown(f"<h3 style='text-align:center;'>🎯 Баллы: <b>{total_score}/{MAX_SCORE}</b> ({percent}%)</h3>", unsafe_allow_html=True)

        # --- Анализ по уровням торговли ---
        st.markdown("### 🎚️ Анализ по уровням торговли")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            classic_threshold = TRADING_LEVELS["Классика"]
            classic_passed = total_score >= classic_threshold
            classic_color = "rgba(16,185,129,0.15)" if classic_passed else "rgba(239,68,68,0.15)"
            classic_text = "✅ ПРОЙДЕН" if classic_passed else "❌ НЕ ПРОЙДЕН"
            st.markdown(f"""
            <div style='background-color:{classic_color}; padding:10px; border-radius:8px; text-align:center; margin:5px; color:#FFFFFF;'>
                <h4>📚 Классика</h4>
                <p><b>{total_score}/{classic_threshold}</b></p>
                <p>{classic_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            advanced_threshold = TRADING_LEVELS["Продвинутый"]
            advanced_passed = total_score >= advanced_threshold
            advanced_color = "rgba(16,185,129,0.15)" if advanced_passed else "rgba(239,68,68,0.15)"
            advanced_text = "✅ ПРОЙДЕН" if advanced_passed else "❌ НЕ ПРОЙДЕН"
            st.markdown(f"""
            <div style='background-color:{advanced_color}; padding:10px; border-radius:8px; text-align:center; margin:5px; color:#FFFFFF;'>
                <h4>🚀 Продвинутый</h4>
                <p><b>{total_score}/{advanced_threshold}</b></p>
                <p>{advanced_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            ludka_threshold = TRADING_LEVELS["Лудка"]
            ludka_passed = total_score >= ludka_threshold
            ludka_color = "rgba(16,185,129,0.15)" if ludka_passed else "rgba(239,68,68,0.15)"
            ludka_text = "✅ ПРОЙДЕН" if ludka_passed else "❌ НЕ ПРОЙДЕН"
            st.markdown(f"""
            <div style='background-color:{ludka_color}; padding:10px; border-radius:8px; text-align:center; margin:5px; color:#FFFFFF;'>
                <h4>🎲 Лудка</h4>
                <p><b>{total_score}/{ludka_threshold}</b></p>
                <p>{ludka_text}</p>
            </div>
            """, unsafe_allow_html=True)

        # --- Общая рекомендация ---
        st.markdown("### 💡 Рекомендация")
        
        if total_score >= TRADING_LEVELS["Классика"]:
            color, msg = ("rgba(59,130,246,0.15)", "🚀 Сделка шикарная! Минимальные риски")
            text_color = "#FFFFFF"
            st.balloons()
        elif total_score >= TRADING_LEVELS["Лудка"]:
            color, msg = ("rgba(16,185,129,0.15)", "✅ Сделка хорошая — можно рассматривать")
            text_color = "#FFFFFF"
        elif total_score >= 50:
            color, msg = ("rgba(245,158,11,0.15)", "⚖️ Сделка средняя — подумай ещё раз")
            text_color = "#FFFFFF"
        else:
            color, msg = ("rgba(239,68,68,0.15)", "❌ Сделка сомнительная — лучше пропустить")
            text_color = "#FFFFFF"

        st.markdown(
            f"<div style='background-color:{color}; padding:15px; border-radius:12px; text-align:center; font-size:1.2rem; font-weight:bold; color:{text_color};'>{msg}</div>",
            unsafe_allow_html=True
        )
        
        # --- Дополнительная информация ---
        st.markdown("---")
        st.markdown("### 📋 Дополнительная информация")
        
        if total_score < TRADING_LEVELS["Лудка"]:
            missing_points = TRADING_LEVELS["Лудка"] - total_score
            st.warning(f"⚠️ До минимального порога не хватает {missing_points} баллов")
            st.info("💡 Рекомендуется дождаться лучшего сетапа или пересмотреть критерии входа")
        elif total_score >= TRADING_LEVELS["Классика"]:
            st.success("🎉 Отличный сетап! Все основные критерии выполнены")
        else:
            st.info("👍 Хороший сетап, но можно улучшить")

    # --- Таймер ---
    if all(st.session_state.checklist.values()):
        if not st.session_state.timer_started:
            if st.button("🚀 Запустить таймер ⏳"):
                st.session_state.timer_end = datetime.now() + timedelta(minutes=10)
                st.session_state.timer_started = True

    if st.session_state.timer_started and st.session_state.timer_end:
        st.markdown("### ⏳ Таймер")
        timer_container = st.empty()
        progress_container = st.empty()

        remaining = st.session_state.timer_end - datetime.now()
        if remaining.total_seconds() > 0:
            for seconds_left in range(int(remaining.total_seconds()), -1, -1):
                mins, secs = divmod(seconds_left, 60)
                progress = 1 - seconds_left / (10 * 60)
                progress_container.progress(progress)
                timer_container.markdown(
                    f"<div style='text-align:center; font-size:1.8rem; color:#2e7d32; font-weight:bold; margin-top:0.5em;'>⏳ Ждём <b>{mins:02d}:{secs:02d}</b> минут</div>",
                    unsafe_allow_html=True
                )
                time.sleep(1)

        timer_container.empty()
        progress_container.empty()
        st.success("🚀 Все условия выполнены! Можно входить в сделку.")

    # --- Примеры сделок ---
    st.markdown("### 📊 Примеры сделок")
    st.image("https://i.postimg.cc/rsPGT5JB/2025-08-09-113211.png", use_container_width=True)
    st.image("https://i.postimg.cc/C5zGr99C/APTUSDT-P-2025-09-09-20-18-27-b4ea3.png", use_container_width=True)
    st.image("https://i.postimg.cc/s2KWVs3j/APTUSDT-P-2025-08-27-11-29-26-04e6f.png", use_container_width=True)
    st.image("https://i.postimg.cc/kXwWrhF8/image.png", use_container_width=True)
    st.image("https://i.postimg.cc/2y13NSGP/APTUSDT-P-2025-08-29-19-31-48-04275.png", use_container_width=True)
