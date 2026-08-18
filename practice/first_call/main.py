from dotenv import load_dotenv
import os
from google import generativeai

load_dotenv(override=True)
api_key=os.getenv('GEMINI_API_KEY')

print(api_key[:5])

client= generativeai.