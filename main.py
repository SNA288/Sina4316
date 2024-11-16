# Main.py v1.0.81

import os
# import logging ( temporary commented )
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from commands import buttons
from IMBbPlus import inline_query

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
OMDB_API_KEY = ('OMDB_API_KEY')

# # Configure logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Hey there! 👋\n"
        "I'm here to help you find any movie or tv-show you’re looking for.\n\n"
        "Just type *@SichanakBot* followed by the movie name, like this:\n"
        "`@SichanakBot batman`\n\n"
        "Let’s find your next watch! 🍿"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown"
    )



def main():
    # Create the Application instance
    # logger.info("Initializing bot with token")
    
    application = Application.builder().token(TOKEN).build()

    # Add Commands, InlineQuery ,Buttons handlers
    # logger.info("Setting up command and button handlers")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(InlineQueryHandler(inline_query))

    # Start polling the bot for updates
    # try:
        # logger.info("Starting the bot with polling")
        application.run_polling()
    # except Exception as e:
        # logger.error(f"Error starting bot with polling: {e}")

if __name__ == '__main__':
    main()
