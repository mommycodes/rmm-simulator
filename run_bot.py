import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
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
    print("🤖 Запуск Telegram-бота...")
    try:
        subprocess.run([sys.executable, "telegram_bot.py"])
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

def main():
    print("🎯 RMM Trading Tools - Telegram Bot Launcher")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    if not check_env_vars():
        sys.exit(1)
    
    if not run_streamlit():
        sys.exit(1)
    
    print("⏳ Ожидание запуска Streamlit...")
    time.sleep(3)
    
    run_telegram_bot()

if __name__ == "__main__":
    main()