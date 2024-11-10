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


# Get values from environment variables
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
# google_api_key = os.getenv('GOOGLE_API_KEY')


# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_database_url,  # Realtime Database URL
    'storageBucket': firebase_storage_bucket  # Storage Bucket
})

# Get references for Firestore and Realtime Database
firestore_db = firestore.client()
realtime_db_ref = db.reference()

async def extract_keywords_jd(cleaned_data: str):
    cleaned_data = cleaned_data.replace('-', '')
    keywords_part = cleaned_data.split("Keywords:")[1].split("Criteria:")[0].strip()
    
    keyword_dict = {}

    # Split the data into lines and process each line
    for line in keywords_part.strip().split('\n'):
        # Remove any leading/trailing whitespace and extract the keyword and value
        keyword, value = line.rsplit(' (', 1)
        value = int(value[:-1])  # Convert the value to an integer
        keyword_dict[keyword.strip()] = value  # Add to dictionary


    return keyword_dict