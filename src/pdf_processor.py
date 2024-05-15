import os
import uuid
import aiohttp
import asyncio
import fitz  # PyMuPDF for PDF operations

async def download_file_async(file_path, save_path, token):
    """Asynchronously download a file from Telegram's servers."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await resp.content.read(1024)  # 1KB per chunk
                        if not chunk:
                            break
                        file.write(chunk)
                print(f"File downloaded and saved to {save_path}")
                return True
            else:
                print(f"Failed to download file: HTTP {resp.status}")
                return False

async def handle_document(update, context):
    document = update.message.document
    chat_id = update.effective_chat.id
    try:
        unique_file_name = f"{uuid.uuid4()}.pdf"
        save_path = f"./data/pdfs/{unique_file_name}"

        print(f"Attempting to fetch file path for document ID {document.file_id}")
        file_path = await get_file_path_async(document.file_id, context.bot.token)

        if file_path and await download_file_async(file_path, save_path, context.bot.token):
            print("File downloaded successfully, extracting text...")
            # You can still extract text and save it for future use without sending it
            text = await extract_text_from_pdf_async(save_path)
            # Store the extracted text in the user_data dictionary for later use
            context.user_data['document_text'] = text
            # Notify the user that the PDF is ready for questions
            await context.bot.send_message(chat_id, "PDF processed. You can now ask questions about it!")
        else:
            await context.bot.send_message(chat_id, "Failed to download or find the PDF.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Print the error to the console
        await context.bot.send_message(chat_id, "An error occurred while processing your document.")

async def extract_text_from_pdf_async(path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, extract_text_from_pdf, path)

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

async def get_file_path_async(file_id, token):
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
        async with session.get(url) as resp:
            data = await resp.json()
            if data['ok']:
                print(f"File path fetched: {data['result']['file_path']}")
                return data['result']['file_path']
            else:
                print("Failed to fetch file path from Telegram.")
                return None
