from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

chat_model = ChatOpenAI(api_key=OPENAI_API_KEY)
# print(dir(chat_model))

help(chat_model.invoke)
help(chat_model.predict)
help(chat_model.generate)