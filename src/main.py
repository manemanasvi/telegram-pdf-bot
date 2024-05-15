# src/main.py
from telegram.ext import Application
from handlers import setup_handlers
from config import TELEGRAM_TOKEN

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    setup_handlers(app)
    app.run_polling()

if __name__ == "__main__":
    main()
