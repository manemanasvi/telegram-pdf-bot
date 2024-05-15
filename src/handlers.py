# src/handlers.py
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters
from pdf_processor import handle_document
from qna_session import handle_message
from image_processor import handle_image

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome to DocuBot! 📄🤖\n"
        "Upload a PDF file and then ask questions about its content. You can also upload an image for a summary."
    )
