import streamlit as st
import time
from datetime import datetime, timedelta

# === Конфигурация чек-листа с эмодзи и баллами ===
CHECKLIST_ITEMS = {
    "🌊 5 волн по канону": (16, "Полный цикл Эллиотта — основа сценария"),
    "📏 Равенство глубины коррекции": (8, "Коррекции должны быть сопоставимы по глубине"),
    "📐 Удлинение по Фибоначчи 227-261": (10, "Расширение волны подтверждает силу тренда"),
    "📉 Пробитие наклонки": (8, "Выход из локальной формации подтверждает смену фазы"),
    "🎓 Индикатор Student - подтверждение 3 волны": (7, "Доп. индикатор усиливает сигнал"),
    "⚡ Дивергенция на 1ч ТФ": (5, "Локальное расхождение, ранний сигнал"),
    "⚡ Дивергенция на 4ч ТФ": (6, "Среднесрочное расхождение, усиливает вход"),
    "⚡ Дивергенция на 1д ТФ": (8, "Крупный сигнал, высокий вес"),
    "📊 Объемы выше среднего": (8, "Подтверждает силу движения"),
    "📈 CCI в зоне ~200 или -200": (4, "Индикатор перекупленности/перепроданности"),
    "📈 RSI в зоне ~20 или ~80": (6, "Подтверждает экстремальное состояние рынка"),
    "📉 Пробитие линии тренда": (8, "Ключевой сигнал смены направления"),
    "🔁 Шаблон похожего паттерна": (5, "История повторяется — полезно, но не всегда"),
    "🚀 Движение по тренду": (7, "Следование за глобальным трендом снижает риск"),
    "₿ Анализ BTC и BTC.D для альты": (5, "Зависимость альткоинов от биткоина"),
    "🛡️ НЕ КИНЖАЛ": (6, "Цена не должна двигаться резкими тенями без структуры"),
    "🧭 Соответствие старшему ТФ": (8, "Сигнал на младшем ТФ должен подтверждаться старшим"),
    "🎯 Более 1,5% TakeProfit": (10, "Цель сделки должна быть больше мелких колебаний — адекватное RR"),
}

MAX_SCORE = sum(weight for weight, _ in CHECKLIST_ITEMS.values())


def render_checklist_entry():
    st.markdown("<h2 style='text-align:center;'>🛡️ Чек-лист трейдера</h2>", unsafe_allow_html=True)
    st.caption("⚡ Заполни чек-лист, подожди 10 минут и только потом входи в сделку — не спеши, ликвидация всегда приходит незаметно")

    # --- Инициализация состояния ---
    if "checklist" not in st.session_state:
        st.session_state.checklist = {key: False for key in CHECKLIST_ITEMS.keys()}
    if "evaluated" not in st.session_state:
        st.session_state.evaluated = False
    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_started" not in st.session_state:
        st.session_state.timer_started = False

    # --- Чеклист ---
    st.markdown("### 📋 Отметь условия входа")
    total_score = 0
    for key, (weight, hint) in CHECKLIST_ITEMS.items():
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
        if percent < 50:
            st.markdown(
                "<div style='background-color:#ffcccc; padding:20px; border-radius:15px; text-align:center; font-size:1.3rem; font-weight:bold; color:#b30000;'>"
                "❌ Сделка сомнительная — лучше пропустить"
                "</div>",
                unsafe_allow_html=True
            )
        elif 50 <= percent < 80:
            st.markdown(
                "<div style='background-color:#fff3cd; padding:20px; border-radius:15px; text-align:center; font-size:1.3rem; font-weight:bold; color:#856404;'>"
                "⚖️ Сделка средняя — подумай ещё раз"
                "</div>",
                unsafe_allow_html=True
            )
        elif 80 <= percent < 95:
            st.markdown(
                "<div style='background-color:#d4edda; padding:20px; border-radius:15px; text-align:center; font-size:1.3rem; font-weight:bold; color:#155724;'>"
                "✅ Сделка хорошая — можно рассматривать"
                "</div>",
                unsafe_allow_html=True
            )
        else:
            st.balloons()
            st.markdown(
                "<div style='background-color:#cce5ff; padding:20px; border-radius:15px; text-align:center; font-size:1.3rem; font-weight:bold; color:#004085;'>"
                "🚀 Сделка шикарная! Минимальные риски"
                "</div>",
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
                    f"""
                    <div style='text-align:center; font-size:1.8rem; color:#2e7d32; font-weight:bold; margin-top:0.5em;'>
                        ⏳ Ждём <b>{mins:02d}:{secs:02d}</b> минут
                    </div>
                    """,
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
