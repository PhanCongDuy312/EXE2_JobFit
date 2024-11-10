import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from firebase_admin import credentials, storage, db, firestore
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import requests
import textwrap
import re
from controller.llm_controller.llm_controller import *
from controller.db_controller.db_controller import *




def download_pdf(url: str) -> None:
    """Download the PDF from the given URL."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download PDF")
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)


def load_pdf(url: str):
    """Load the PDF and return its content as documents."""
    download_pdf(url)
    loader = PyPDFLoader("temp.pdf")
    documents = loader.load_and_split()
    content = ""
    for _data in documents:
        _content = [line.strip()
                    for line in _data.page_content.splitlines() if line.strip() != ""]
        content += "\n".join(_content) + "\n"
        
    return content


def clean_ans(summary: str):
    cleaned_data = summary.replace('*', '')
    cleaned_data = cleaned_data.replace('**', '')
    cleaned_data = cleaned_data.replace('-', '')
    return cleaned_data


def extract_matching_keywords(matching_result: str):
    keyword = matching_result.split("1. Keywords from JD in CV:")[1].split("Count the similarity keyword of JD that exist in CV:")[0].strip()

    filtered_lines = "\n".join([line for line in keyword.splitlines() if "Not found" not in line])

    # Convert the lines into a dictionary
    result = {line.split(' - ')[0].strip('- ').strip(): line.split(' - ')[1].strip() for line in filtered_lines.splitlines()}
    print("Result datatype: ",type(result))
    last_line = matching_result.splitlines()[-1]  # Get the last line
    final_point = last_line.split('=')[-1].strip()  # Split by '=' and strip whitespace

    return result, final_point

# def check_account_exist(user_name: str, password: str):
#     check_account_existance = check_user(username=user_name, password=password)
        
#     return check_account_existance