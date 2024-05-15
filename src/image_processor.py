import asyncio
import os
import uuid
import aiohttp
import boto3
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
from PIL import Image

# Initialize the Rekognition client with credentials from config
rekognition_client = boto3.client(
    'rekognition',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


async def download_image_async(file_path, save_path, token):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(save_path, 'wb') as file:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                print(f"Image downloaded and saved to {save_path}")
                return True
            else:
                print(f"Failed to download image: HTTP {resp.status}")
                return False


async def handle_image(update, context):
    photo = update.message.photo[-1]
    chat_id = update.effective_chat.id
    try:
        unique_file_name = f"{uuid.uuid4()}.jpg"
        save_path = f"./data/images/{unique_file_name}"

        print(f"Attempting to fetch file path for photo ID {photo.file_id}")
        file_path = await get_file_path_async(photo.file_id, context.bot.token)

        if file_path and await download_image_async(file_path, save_path, context.bot.token):
            print("Image downloaded successfully, analyzing...")
            summary = await analyze_image_async(save_path)
            await context.bot.send_message(chat_id, summary)
        else:
            await context.bot.send_message(chat_id, "Failed to download or find the image.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        await context.bot.send_message(chat_id, "An error occurred while processing your image.")


async def analyze_image_async(path):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, analyze_image, path)


def analyze_image(path):
    with open(path, 'rb') as image_file:
        content = image_file.read()

    # Detect text in the image
    response = rekognition_client.detect_text(
        Image={'Bytes': content}
    )

    text_detections = response['TextDetections']
    extracted_texts = [text['DetectedText'] for text in text_detections if text['Type'] == 'LINE']

    # Remove duplicates while preserving order
    seen = set()
    unique_texts = [x for x in extracted_texts if not (x in seen or seen.add(x))]

    # Format the output in a readable way
    if unique_texts:
        summary = "This image contains the following text elements:\n\n"
        for text in unique_texts:
            summary += f"-> {text}\n"
    else:
        summary = "No significant text elements were detected in the image."

    return summary


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
