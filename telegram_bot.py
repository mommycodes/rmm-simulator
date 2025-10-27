import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🧮 Калькуляторы", web_app=WebAppInfo(url=f"{WEB_APP_URL}/calculators"))],
        [InlineKeyboardButton("📊 Технический анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/ta"))],
        [InlineKeyboardButton("🌊 Волновой анализ", web_app=WebAppInfo(url=f"{WEB_APP_URL}/waves"))],
        [InlineKeyboardButton("🎲 Симулятор", web_app=WebAppInfo(url=f"{WEB_APP_URL}/simulator"))],
        [InlineKeyboardButton("🧠 Цепи Маркова", web_app=WebAppInfo(url=f"{WEB_APP_URL}/markov"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🎯 **Добро пожаловать в RMM Trading Tools!**

Ваш персональный трейдинг-ассистент с полным набором инструментов для анализа и расчета рисков.

**Доступные инструменты:**
• 🧮 Калькуляторы входа и объема
• 📊 Технический анализ
• 🌊 Волновой анализ
• 🎲 Симулятор стратегий
• 🧠 Цепи Маркова

Выберите нужный инструмент из меню ниже ⬇️
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def calculators(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🧮 Калькулятор входа", web_app=WebAppInfo(url=f"{WEB_APP_URL}/calculators"))],
        [InlineKeyboardButton("📐 Калькулятор объема", web_app=WebAppInfo(url=f"{WEB_APP_URL}/calculators"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧮 **Калькуляторы**\n\nВыберите нужный калькулятор:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def simulator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🎲 Симулятор Монте-Карло", web_app=WebAppInfo(url=f"{WEB_APP_URL}/simulator"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎲 **Симулятор стратегий**\n\nПротестируйте свою стратегию с помощью симулятора Монте-Карло:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def markov(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🧠 Цепи Маркова", web_app=WebAppInfo(url=f"{WEB_APP_URL}/markov"))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🧠 **Цепи Маркова**\n\nАнализ рыночных паттернов с помощью цепей Маркова:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
🤖 **RMM Trading Tools - Справка**

**Доступные команды:**
• `/start` - Главное меню
• `/calculators` - Калькуляторы
• `/simulator` - Симулятор стратегий
• `/markov` - Цепи Маркова
• `/help` - Эта справка

**Инструменты:**
• 🧮 Калькуляторы входа и объема
• 📊 Технический анализ
• 🌊 Волновой анализ
• 🎲 Симулятор Монте-Карло
• 🧠 Анализ цепей Маркова

**Поддержка:** @mommycodes
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "calculators":
        await calculators(update, context)
    elif query.data == "simulator":
        await simulator(update, context)
    elif query.data == "markov":
        await markov(update, context)

def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        return
    
    if not WEB_APP_URL:
        print("❌ WEB_APP_URL не найден в .env файле!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calculators", calculators))
    application.add_handler(CommandHandler("simulator", simulator))
    application.add_handler(CommandHandler("markov", markov))
    application.add_handler(CommandHandler("help", help_command))
    
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Telegram бот запущен!")
    print("Для остановки нажмите Ctrl+C")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()