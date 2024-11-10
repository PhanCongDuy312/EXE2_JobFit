import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
import firebase_admin
from firebase_admin import credentials, storage, db, firestore
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from controller.db_controller.db_controller import *



def extract_keywords_jd(cleaned_data: str):
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