import asyncio
import openai
from config import OPENAI_API_KEY
import textwrap

class LangchainResult:
    def __init__(self):
        self.content = ""

class ChatOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key

    async def generate(self, input_data):
        # Call the OpenAI API and parse the response
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=input_data,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
            api_key=self.api_key,
        )

        # Create a LangchainResult object with the response text
        result = LangchainResult()
        result.content = response.choices[0].text

        return result

async def handle_message(update, context):
    query = update.message.text  # User's message as query
    document_text = context.user_data.get('document_text')  # Previously stored document text

    if document_text:
        # Prepare the input
        input_data = f"{document_text}\n\nQuestion: {query}\nAnswer:"

        # Invoke the model with the input
        try:
            response = await chat_model.generate(input_data)

            # Print the response to the console for debugging
            print(f"Response: {response.content}")

            # Extract the answer from the response object
            answer = response.content.strip()

            # Send the answer as a single text message
            await update.message.reply_text(answer, parse_mode='HTML')
        except Exception as e:
            print(f"Error: {str(e)}")
            await update.message.reply_text("Failed to process your question.")
    else:
        await update.message.reply_text("Please upload a PDF first.")
# Initialize the ChatOpenAI model
chat_model = ChatOpenAI(api_key=OPENAI_API_KEY)