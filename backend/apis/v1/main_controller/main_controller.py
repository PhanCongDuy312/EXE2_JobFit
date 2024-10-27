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
from controller.llm_controller.llm_controller import *
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

# Function to upload file to Firebase Storage and return its public URL
async def upload_file_to_firebase(file: UploadFile):
    bucket = storage.bucket()
    
    # Create a unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file.filename}"  # Use unique ID to avoid naming conflicts

    # Upload the file to Firebase Storage
    blob = bucket.blob(filename)
    blob.upload_from_file(file.file)
    
    # Make the file publicly accessible and get the URL
    blob.make_public()
    download_url = blob.public_url

    return filename, file_id, download_url


async def download_pdf(url: str) -> None:
    """Download the PDF from the given URL."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to download PDF")
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)


async def load_pdf(url: str):
    """Load the PDF and return its content as documents."""
    download_pdf(url)
    loader = PyPDFLoader("temp.pdf")
    documents = loader.load()
    return documents


async def clean_ans(summary: str):
    cleaned_data = summary.replace('*', '')
    cleaned_data = cleaned_data.replace('**', '')
    cleaned_data = cleaned_data.replace('-', '')
    return cleaned_data


async def extract_matching_keywords(matching_result: str):
    keyword = matching_result.split("1. Keywords from JD in CV:")[1].split("Count the similarity keyword of JD that exist in CV:")[0].strip()

    filtered_lines = "\n".join([line for line in keyword.splitlines() if "Not found" not in line])

    # Convert the lines into a dictionary
    result = {line.split(' - ')[0].strip('- ').strip(): line.split(' - ')[1].strip() for line in filtered_lines.splitlines()}

    last_line = matching_result.splitlines()[-1]  # Get the last line
    final_point = last_line.split('=')[-1].strip()  # Split by '=' and strip whitespace

    return result, final_point



async  def algorithm_matching(cv_summary: str, cv_keyword_dict: dict, jd_keyword_dict: dict):
    match_percentage = 0

    # Build the prompt for Google Generative AI
    prompt = (
        "I need to calculate the matching percentage between a CV and a Job Description (JD). "
        "The CV contains the following keywords:\n"
    )

    # Add CV keywords to the prompt
    for keyword in cv_keyword_dict.keys():
        prompt += f"- {keyword}\n"

    prompt += (
        "\nThe Job Description has the following keywords:\n"
    )
    
    # Add JD keywords to the prompt
    for keyword in jd_keyword_dict.keys():
        prompt += f"- {keyword}\n"

    prompt += (
        "\nThe CV also contains other information that might relate to the JD. "
        "Please evaluate if the information in the CV is directly related to the JD based on the following:\n"
        f"{cv_summary}\n"
        "\nCalculate the matching percentage as follows:\n"
        "Rules:\n"
        "0: The Cv_keyword dont need to be the exactly the same with the JD_keyword, use your knowledge to matching the keyword it can be little bit different like css and css3 can be match together, but if its too different so don't count it\n"
        "1. Just take the keywords in JD and compare to the CV, dont create new keyword. If all keywords from the JD are found in the CV, the point should be 90 points.\n"
        "2. If fewer keywords are found, decrease the percentage accordingly.\n"
        "3. The remaining 10 points of the score should be based on how well the additional information in the CV relates to the JD, base on your knowledge.\n"
        "4. Please provide a score between 0 and 100 points based on these criteria."
        'In the return give me this follow this structure\n '
        '1. Keywords from JD in CV: \n'
        'List similarity keyword, JD_keyword - Cv_keyword\n'
        'Count the similarity keyword of JD that exist in CV: 10/18 = 55,56% (for example total JD has 19 keywords, and 10 of that exist in CV)'
        '2. Matching percentage based on keywords: 55,56% * 90 points = 75points\n'
        '3. Additional information in CV related to JD: ( In this part read the cv to find some additional information and list them like below )\n'
        'List additional information'
        'Total Matching Percentage: 75 points + 10 points ( This point based on how well the additional information in the CV relates to the JD ) = 85 points\n'
        'Follow the rule dont do anything new\n'
    )
    
    # Call the Google Generative AI with the prompt
    matching_result = query_google_generative_ai(prompt)
    print("################# matching #################")
    print(matching_result)
    keyword_dict, point = extract_matching_keywords(matching_result)

    return keyword_dict, point
