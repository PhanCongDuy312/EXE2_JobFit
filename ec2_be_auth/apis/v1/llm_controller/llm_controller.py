import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
import firebase_admin
from firebase_admin import credentials, storage, db, firestore
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import requests
import textwrap
import re
from dotenv import load_dotenv

load_dotenv()


google_api_key = os.getenv('GOOGLE_API_KEY')
print(google_api_key)
chat_model = ChatGoogleGenerativeAI(google_api_key=google_api_key, temperature=0, model="gemini-pro", request_timeout=120)


def query_google_generative_ai(prompt: str) -> str:
    """Query Google Generative AI with the given prompt and return the response."""
    response = chat_model.invoke([{"role": "user", "content": prompt}])  # Use the invoke method
    return response.content  # Access the content directly from the response