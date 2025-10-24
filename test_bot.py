#!/usr/bin/env python3
"""
Простой скрипт для тестирования Telegram-бота
"""
import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButton, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# URL вашего сайта
WEB_APP_URL = os.getenv('WEB_APP_URL')

# Админ (только вы)
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_USER_ID = None  # Будет установлен автоматически

# Файл для хранения авторизованных пользователей
USERS_FILE = 'authorized_users.json'

# Загружаем список авторизованных пользователей
def load_authorized_users():
    """Загружает список авторизованных пользователей"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей: {e}")
        return []

def save_authorized_users(users):
    """Сохраняет список авторизованных пользователей"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователей: {e}")
        return False

def is_user_authorized(user_id, username):
    """Проверяет, авторизован ли пользователь"""
    # Админ всегда авторизован
    if username == ADMIN_USERNAME:
        return True
    
    # Загружаем список пользователей
    users = load_authorized_users()
    
    # Проверяем по ID и username
    for user in users:
        if user.get('id') == user_id or user.get('username') == username:
            return True
    
    return False

def is_admin(user_id, username):
    """Проверяет, является ли пользователь админом"""
    return username == ADMIN_USERNAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Проверяем доступ
    if not is_user_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\n"
            "Обратитесь к администратору для получения доступа к боту.\n"
            "📬 Контакт: @mommycodes",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🧮 Калькуляторы", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=calculators"))],
        [InlineKeyboardButton("📊 Технический анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=ta"))],
        [InlineKeyboardButton("🌊 Волновой анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=waves"))],
        [InlineKeyboardButton("🎲 Симулятор", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=simulator"))],
        [InlineKeyboardButton("🧠 Цепи Маркова", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=markov"))],
        [InlineKeyboardButton("🧭 Сводка по монете", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=coin_summary"))],
        [InlineKeyboardButton("📋 Чек-лист", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=checklist"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🚀 **Добро пожаловать в RMM Trading Tools!**

**Доступные инструменты:**

🧮 **Калькуляторы** - расчет рисков и объемов позиций
📊 **Технический анализ** - материалы по техническому анализу
🌊 **Волновой анализ** - теория волн Эллиота и практика
🎲 **Симулятор** - тестирование торговых стратегий
🧠 **Цепи Маркова** - анализ паттернов и прогнозирование
🧭 **Сводка по монете** - быстрый анализ торгового инструмента
📋 **Чек-лист** - подготовка к сделке

**🌐 Полный сайт:** https://mommycodes.streamlit.app

Нажмите на кнопку ниже, чтобы открыть нужный инструмент!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def calculators(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Прямой доступ к калькуляторам"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Проверяем доступ
    if not is_user_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\n"
            "Обратитесь к администратору для получения доступа к боту.\n"
            "📬 Контакт: @mommycodes",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🧮 Открыть калькуляторы", web_app=WebAppInfo(url=f"{WEB_APP_URL}?page=calculators"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧮 **Калькуляторы RMM**\n\nНажмите кнопку ниже для открытия калькуляторов:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# АДМИНСКИЕ КОМАНДЫ
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Справка по админским командам"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    help_text = """
🔧 **Админские команды:**

`/add_user @username` - добавить пользователя
`/remove_user @username` - удалить пользователя  
`/list_users` - список всех пользователей
`/admin_help` - эта справка

**Примеры:**
`/add_user @john_doe`
`/remove_user @jane_smith`
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавить пользователя"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/add_user @john_doe`")
        return
    
    target_username = context.args[0].replace('@', '')
    
    # Загружаем текущий список
    users = load_authorized_users()
    
    # Проверяем, не добавлен ли уже
    for user in users:
        if user.get('username') == target_username:
            await update.message.reply_text(f"✅ Пользователь @{target_username} уже в списке!")
            return
    
    # Добавляем пользователя
    new_user = {
        'username': target_username,
        'added_by': username,
        'added_date': str(update.message.date)
    }
    users.append(new_user)
    
    if save_authorized_users(users):
        await update.message.reply_text(f"✅ Пользователь @{target_username} добавлен в список!")
    else:
        await update.message.reply_text("❌ Ошибка при сохранении пользователя!")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удалить пользователя"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/remove_user @john_doe`")
        return
    
    target_username = context.args[0].replace('@', '')
    
    # Загружаем текущий список
    users = load_authorized_users()
    
    # Удаляем пользователя
    original_count = len(users)
    users = [user for user in users if user.get('username') != target_username]
    
    if len(users) < original_count:
        if save_authorized_users(users):
            await update.message.reply_text(f"✅ Пользователь @{target_username} удален из списка!")
        else:
            await update.message.reply_text("❌ Ошибка при сохранении изменений!")
    else:
        await update.message.reply_text(f"❌ Пользователь @{target_username} не найден в списке!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Список всех пользователей"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    users = load_authorized_users()
    
    if not users:
        await update.message.reply_text("📝 Список пользователей пуст.")
        return
    
    text = "📝 **Список авторизованных пользователей:**\n\n"
    for i, user in enumerate(users, 1):
        text += f"{i}. @{user.get('username', 'N/A')}\n"
        text += f"   Добавлен: {user.get('added_by', 'N/A')}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def setup_menu_button(application):
    """Настройка кнопки меню для авторизованных пользователей"""
    try:
        # Создаем кнопку меню с Web App
        menu_button = MenuButtonWebApp(
            text="🚀 RMM Tools",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
        
        # Устанавливаем кнопку меню
        await application.bot.set_chat_menu_button(menu_button=menu_button)
        logger.info("Кнопка меню настроена успешно")
    except Exception as e:
        logger.error(f"Ошибка настройки кнопки меню: {e}")

def main():
    """Запуск бота"""
    # Получаем токен из переменных окружения
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        print("Добавьте в .env файл: TELEGRAM_BOT_TOKEN=ваш_токен")
        return
    
    # Создаем приложение
    application = Application.builder().token(bot_token).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calculators", calculators))
    
    # Админские команды
    application.add_handler(CommandHandler("admin_help", admin_help))
    application.add_handler(CommandHandler("add_user", add_user))
    application.add_handler(CommandHandler("remove_user", remove_user))
    application.add_handler(CommandHandler("list_users", list_users))
    
    # Настраиваем кнопку меню при запуске
    application.post_init = setup_menu_button
    
    # Запускаем бота
    logger.info("Запуск Telegram бота...")
    print("Бот запущен!")
    print("Админские команды:")
    print("   /admin_help - справка по админским командам")
    print("   /add_user @username - добавить пользователя")
    print("   /remove_user @username - удалить пользователя")
    print("   /list_users - список пользователей")
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\nОстановка бота...")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()
