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

async def extract_keywords_cv(cleaned_data: str):
    result = {}
    
    keywords_part = cleaned_data.split("Keywords:")[1].split("OtherInforCV Content:")[0].strip()
    # Split the data by lines and loop through them
    for line in keywords_part.strip().splitlines():
        # Split each line by ":" to separate the key and value
        key, value = line.split(":")
        # Strip any excess whitespace and add to the dictionary
        result[key.strip()] = int(value.strip())
    return result


async def extract_other_infor(cleaned_data: str):
    start_index = cleaned_data.find("OtherInforCV Content:")

    # Extract everything from that point onward
    other_info_content = cleaned_data[start_index:].strip()

    return other_info_content