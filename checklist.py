import streamlit as st
import time
from datetime import datetime, timedelta

# === Конфигурация чек-листа с разделами и баллами (сумма = 100) ===
CHECKLIST_SECTIONS = {
    "🌊 Волновой анализ": {
        "5 волн по канону": (15, "Полный цикл Эллиотта — основа сценария"),
        "Равенство глубины коррекции": (6, "Коррекции должны быть сопоставимы по глубине"),
        "Удлинение по Фибоначчи 227-261": (8, "Расширение волны подтверждает силу тренда"),
        "Пробитие наклонки": (5, "Выход из локальной формации подтверждает смену фазы"),
    },
    "🎛 Индикаторы": {
        "Индикатор Student - подтверждение 3 волны": (6, "Доп. индикатор усиливает сигнал"),
        "Дивергенция на 1ч ТФ": (3, "Локальное расхождение, ранний сигнал"),
        "Дивергенция на 4ч ТФ": (4, "Среднесрочное расхождение, усиливает вход"),
        "Дивергенция на 1д ТФ": (5, "Крупный сигнал, высокий вес"),
        "CCI в зоне ~200 или -200": (2, "Индикатор перекупленности/перепроданности"),
        "RSI в зоне ~20 или ~80": (4, "Подтверждает экстремальное состояние рынка"),
    },
    "💧 Ликвидность и объёмы": {
        "Движение в зоны ликвидности (50x / 100x)": (6, "Цена стремится к кластерам стопов и ликвидаций — важный сигнал"),
        "Объемы выше среднего": (6, "Подтверждает силу движения"),
    },
    "🚀 Тренд и контекст": {
        "Пробитие линии тренда": (5, "Ключевой сигнал смены направления"),
        "Движение по тренду": (5, "Следование за глобальным трендом снижает риск"),
        "Соответствие старшему ТФ": (5, "Сигнал на младшем ТФ должен подтверждаться старшим"),
        "Анализ BTC и BTC.D для альты": (3, "Зависимость альткоинов от биткоина"),
        "Шаблон похожего паттерна": (3, "История повторяется — полезно, но не всегда"),
    },
    "🛡️ Риск и фильтры": {
        "НЕ КИНЖАЛ": (3, "Цена не должна двигаться резкими тенями без структуры"),
        "Более 1,5% TakeProfit": (6, "Цель сделки должна быть больше мелких колебаний — адекватное RR"),
    }
}

MAX_SCORE = sum(weight for section in CHECKLIST_SECTIONS.values() for weight, _ in section.values())

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
        # Визуальное отделение раздела
        st.markdown(f"<hr style='border:1px solid #ddd; margin:10px 0'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-weight:bold; color:#2e7d32; margin-bottom:5px;'>{section_name}</h4>", unsafe_allow_html=True)
        for key, (weight, hint) in items.items():
            checked = st.checkbox(
                f"{key} ({weight} баллов)", 
                value=st.session_state.checklist[key], 
                help=hint, 
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

        # --- Визуальная оценка ---
        color, msg = ("#ffcccc", "❌ Сделка сомнительная — лучше пропустить") if percent < 50 else \
                     ("#fff3cd", "⚖️ Сделка средняя — подумай ещё раз") if percent < 80 else \
                     ("#d4edda", "✅ Сделка хорошая — можно рассматривать") if percent < 95 else \
                     ("#cce5ff", "🚀 Сделка шикарная! Минимальные риски")
        text_color = "#b30000" if percent < 50 else "#856404" if percent < 80 else "#155724" if percent < 95 else "#004085"

        if percent >= 95:
            st.balloons()

        st.markdown(
            f"<div style='background-color:{color}; padding:15px; border-radius:12px; text-align:center; font-size:1.2rem; font-weight:bold; color:{text_color};'>{msg}</div>",
            unsafe_allow_html=True
        )

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
    st.image("https://i.postimg.cc/s2KWVs3j/APTUSDT-P-2025-08-27-11-29-26-04e6f.png", use_container_width=True)
    st.image("https://i.postimg.cc/kXwWrhF8/image.png", use_container_width=True)
