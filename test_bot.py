import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButton, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

WEB_APP_URL = os.getenv('WEB_APP_URL')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_USER_ID = None
USERS_FILE = 'authorized_users.json'

def load_authorized_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей: {e}")
        return []

def save_authorized_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Ошибка сохранения пользователей: {e}")
        return False

def is_user_authorized(user_id, username):
    if username == ADMIN_USERNAME:
        return True
    
    users = load_authorized_users()
    
    for user in users:
        if user.get('id') == user_id or user.get('username') == username:
            return True
    
    return False

def is_admin(user_id, username):
    return username == ADMIN_USERNAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_user_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\n"
            "Обратитесь к администратору для получения доступа к боту.\n"
            "📬 Контакт: @mommycodes",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🌐 Открыть сайт", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎯 **Ваш персональный трейдинг-ассистент**

Здесь собраны все инструменты, которые помогут вам принимать обдуманные торговые решения.

От расчета рисков до анализа паттернов — все в одном месте, доступно в любое время.

✨ **Готовы начать?**
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def calculators(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_user_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\n"
            "Обратитесь к администратору для получения доступа к боту.\n"
            "📬 Контакт: @mommycodes",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🌐 Открыть сайт", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **Ваш персональный трейдинг-ассистент**\n\n✨ Готовы начать?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    logger.info(f"Команда add_user от пользователя {username} (ID: {user_id})")
    logger.info(f"ADMIN_USERNAME: {ADMIN_USERNAME}")
    logger.info(f"is_admin результат: {is_admin(user_id, username)}")
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/add_user @john_doe`")
        return
    
    target_username = context.args[0].replace('@', '')
    
    users = load_authorized_users()
    
    for user in users:
        if user.get('username') == target_username:
            await update.message.reply_text(f"✅ Пользователь @{target_username} уже в списке!")
            return
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Укажите username пользователя!\nПример: `/remove_user @john_doe`")
        return
    
    target_username = context.args[0].replace('@', '')
    
    users = load_authorized_users()
    
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
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_admin(user_id, username):
        await update.message.reply_text("🚫 У вас нет прав администратора!")
        return
    
    users = load_authorized_users()
    
    if not users:
        await update.message.reply_text("📝 Список пользователей пуст.")
        return
    
    text = "📝 Список авторизованных пользователей:\n\n"
    for i, user in enumerate(users, 1):
        username = user.get('username', 'N/A')
        added_by = user.get('added_by', 'N/A')
        text += f"{i}. @{username}\n"
        text += f"   Добавлен: {added_by}\n\n"
    
    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not is_user_authorized(user_id, username):
        await update.message.reply_text(
            "🚫 **Доступ закрыт**\n\n"
            "Обратитесь к администратору для получения доступа к боту.\n"
            "📬 Контакт: @mommycodes",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🌐 Открыть сайт", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 **Ваш персональный трейдинг-ассистент**\n\n✨ Готовы начать?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def setup_menu_button(application):
    try:
        await application.bot.set_chat_menu_button(menu_button=None)
        logger.info("Кнопка меню отключена - доступ только через команды")
    except Exception as e:
        logger.error(f"Ошибка настройки кнопки меню: {e}")

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        print("Добавьте в .env файл: TELEGRAM_BOT_TOKEN=ваш_токен")
        return
    
    application = Application.builder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calculators", calculators))
    
    application.add_handler(CommandHandler("admin_help", admin_help))
    application.add_handler(CommandHandler("add_user", add_user))
    application.add_handler(CommandHandler("remove_user", remove_user))
    application.add_handler(CommandHandler("list_users", list_users))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Ошибка при обработке обновления: {context.error}")
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    application.add_error_handler(error_handler)
    
    application.post_init = setup_menu_button
    
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