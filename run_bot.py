#!/usr/bin/env python3
"""
Скрипт для запуска Telegram-бота в фоновом режиме
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Проверяем наличие необходимых зависимостей"""
    try:
        import telegram
        import streamlit
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False

def check_env_vars():
    """Проверяем наличие переменных окружения"""
    required_vars = ['TELEGRAM_BOT_TOKEN', 'WEB_APP_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("Создайте файл .env с необходимыми переменными")
        return False
    
    print("✅ Переменные окружения настроены")
    return True

def run_streamlit():
    """Запускаем Streamlit приложение"""
    print("🚀 Запуск Streamlit приложения...")
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "telegram_app.py", 
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
        print("✅ Streamlit запущен на порту 8501")
        return True
    except Exception as e:
        print(f"❌ Ошибка запуска Streamlit: {e}")
        return False

def run_telegram_bot():
    """Запускаем Telegram-бота"""
    print("🤖 Запуск Telegram-бота...")
    try:
        subprocess.run([sys.executable, "telegram_bot.py"])
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

def main():
    """Главная функция"""
    print("🎯 RMM Trading Tools - Telegram Bot Launcher")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_requirements():
        sys.exit(1)
    
    # Проверяем переменные окружения
    if not check_env_vars():
        sys.exit(1)
    
    # Запускаем Streamlit в фоне
    if not run_streamlit():
        sys.exit(1)
    
    # Ждем немного, чтобы Streamlit запустился
    print("⏳ Ожидание запуска Streamlit...")
    time.sleep(3)
    
    # Запускаем бота
    run_telegram_bot()

if __name__ == "__main__":
    main()
