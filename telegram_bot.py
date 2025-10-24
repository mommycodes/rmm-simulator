import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("🧮 Калькуляторы", web_app=WebAppInfo(url=f"{WEB_APP_URL}/calculators"))],
        [InlineKeyboardButton("📊 Технический анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/ta"))],
        [InlineKeyboardButton("🌊 Волновой анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/waves"))],
        [InlineKeyboardButton("🎲 Симулятор", web_app=WebAppInfo(url=f"{WEB_APP_URL}/simulator"))],
        [InlineKeyboardButton("🧠 Цепи Маркова", web_app=WebAppInfo(url=f"{WEB_APP_URL}/markov"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🚀 **Добро пожаловать в RMM Trading Tools!**

Выберите нужный инструмент:

🧮 **Калькуляторы** - расчет рисков и объемов
📊 **Технический анализ** - материалы по ТА
🌊 **Волновой анализ** - теория волн Эллиота
🎲 **Симулятор** - тестирование стратегий
🧠 **Цепи Маркова** - анализ паттернов

Нажмите на кнопку ниже, чтобы открыть нужный инструмент!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = """
📚 **Доступные команды:**

/start - Главное меню
/help - Эта справка
/calculators - Открыть калькуляторы
/analysis - Открыть анализ

🔧 **Инструменты:**
• Калькулятор рисков
• Калькулятор объемов по SL
• Симулятор стратегий
• Анализ паттернов
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def calculators(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Прямой доступ к калькуляторам"""
    keyboard = [
        [InlineKeyboardButton("🧮 Открыть калькуляторы", web_app=WebAppInfo(url=f"{WEB_APP_URL}/calculators"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧮 **Калькуляторы RMM**\n\nНажмите кнопку ниже для открытия калькуляторов:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Доступ к аналитическим инструментам"""
    keyboard = [
        [InlineKeyboardButton("📊 Технический анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/ta"))],
        [InlineKeyboardButton("🌊 Волновой анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/waves"))],
        [InlineKeyboardButton("🧠 Цепи Маркова", web_app=WebAppInfo(url=f"{WEB_APP_URL}/markov"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 **Аналитические инструменты**\n\nВыберите тип анализа:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

def main() -> None:
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("calculators", calculators))
    application.add_handler(CommandHandler("analysis", analysis))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    logger.info("Запуск Telegram бота...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
