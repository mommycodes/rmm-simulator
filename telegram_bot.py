import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')

AUTHORIZED_USERS_FILE = 'authorized_users.json'

def load_authorized_users():
    try:
        with open(AUTHORIZED_USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "admin": ADMIN_USERNAME}

def save_authorized_users(users_data):
    with open(AUTHORIZED_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)

def is_authorized(user_id, username):
    users_data = load_authorized_users()
    return (str(user_id) in users_data["users"] or 
            username in users_data["users"] or 
            username == users_data["admin"])

def is_admin(username):
    users_data = load_authorized_users()
    return username == users_data["admin"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\nОбратитесь к администратору для получения доступа.\n\n**Администратор:** @mommycodes"
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🚀 START", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎯 **Trading Tools**

Ваш персональный трейдинг-ассистент с полным набором инструментов для анализа и расчета рисков.

**Доступные инструменты:**
• 🧮 Калькуляторы входа и объема
• 📊 Технический анализ и чек-лист
• 🌊 Волновой анализ
• 🎲 Симулятор стратегий
• 🧠 Цепи Маркова

Нажмите кнопку **🚀 START** для доступа к инструментам ⬇️
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/add_user @username`")
        return
    
    new_user = context.args[0].replace('@', '')
    users_data = load_authorized_users()
    
    if new_user in users_data["users"]:
        await update.message.reply_text(f"✅ Пользователь @{new_user} уже авторизован!")
        return
    
    users_data["users"].append(new_user)
    save_authorized_users(users_data)
    
    await update.message.reply_text(f"✅ Пользователь @{new_user} добавлен в список авторизованных!")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/remove_user @username`")
        return
    
    user_to_remove = context.args[0].replace('@', '')
    users_data = load_authorized_users()
    
    if user_to_remove not in users_data["users"]:
        await update.message.reply_text(f"❌ Пользователь @{user_to_remove} не найден в списке!")
        return
    
    users_data["users"].remove(user_to_remove)
    save_authorized_users(users_data)
    
    await update.message.reply_text(f"✅ Пользователь @{user_to_remove} удален из списка авторизованных!")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    
    if not is_admin(username):
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return
    
    users_data = load_authorized_users()
    users_list = "\n".join([f"• @{user}" for user in users_data["users"]])
    
    message = f"👥 **Авторизованные пользователи:**\n\n{users_list}\n\n**Администратор:** @{users_data['admin']}"
    
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    
    if is_admin(username):
        help_text = """
🤖 **RMM Trading Tools - Админ панель**

**Пользовательские команды:**
• `/start` - Главное меню
• `/help` - Эта справка

**Админ команды:**
• `/add_user @username` - Добавить пользователя
• `/remove_user @username` - Удалить пользователя
• `/list_users` - Список пользователей

**Поддержка:** @mommycodes
        """
    else:
        help_text = """
🤖 **RMM Trading Tools**

**Доступные команды:**
• `/start` - Главное меню
• `/help` - Эта справка

**Поддержка:** @mommycodes
        """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    
    if is_admin(username):
        help_text = """
🤖 **Trading Tools - Админ панель**

**Пользовательские команды:**
• `/start` - Главное меню
• `/help` - Эта справка

**Админ команды:**
• `/add_user @username` - Добавить пользователя
• `/remove_user @username` - Удалить пользователя
• `/list_users` - Список пользователей

**Поддержка:** @mommycodes
        """
    else:
        help_text = """
🤖 **Trading Tools**

**Доступные команды:**
• `/start` - Главное меню
• `/help` - Эта справка

**Поддержка:** @mommycodes
        """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        return
    
    if not WEB_APP_URL:
        print("❌ WEB_APP_URL не найден в .env файле!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_user", add_user))
    application.add_handler(CommandHandler("remove_user", remove_user))
    application.add_handler(CommandHandler("list_users", list_users))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    commands = [
        BotCommand("start", "🚀 Главное меню"),
        BotCommand("help", "❓ Справка")
    ]
    
    async def post_init(application):
        await application.bot.set_my_commands(commands)
    
    application.post_init = post_init
    
    print("🤖 Telegram бот с авторизацией запущен!")
    print("Для остановки нажмите Ctrl+C")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
