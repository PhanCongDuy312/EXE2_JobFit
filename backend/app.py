import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
import firebase_admin
from firebase_admin import credentials, storage, db, firestore
from langchain_community.document_loaders import PyPDFLoader
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI
# import requests
# import textwrap
# import re
from dotenv import load_dotenv

from controller.main_controller.main_controller import *
from controller.llm_controller.llm_controller import *
from controller.llm_controller.prompt import *
from controller.jd_controller.jd_controller import *
from controller.cv_controller.cv_controller import *
from controller.db_controller.db_controller import *

from tempfile import NamedTemporaryFile
from pdf2docx import Converter
from io import BytesIO
import shutil

load_dotenv()

app = FastAPI()

# # Get values from environment variables
# firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
# firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
# firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
# # google_api_key = os.getenv('GOOGLE_API_KEY')


# # Initialize Firebase Admin SDK with service account credentials
# cred = credentials.Certificate(firebase_credentials_path)
# firebase_admin.initialize_app(cred, {
#     'databaseURL': firebase_database_url,  # Realtime Database URL
#     'storageBucket': firebase_storage_bucket  # Storage Bucket
# })

# # Get references for Firestore and Realtime Database
# firestore_db = firestore.client()
# realtime_db_ref = db.reference()

# Set Google API Key and create ChatGoogleGenerativeAI instance
# chat_model = ChatGoogleGenerativeAI(google_api_key=google_api_key, temperature=0, model="gemini-pro", request_timeout=120)


# Route to upload CV
@app.post("/upload/cv/")
async def upload_cv(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOC files are allowed.")

    if file.content_type in ["application/pdf"]:
        pdf_format = await check_cv_types(file)
        # Upload file to Firebase and get the details
    filename, cv_id, public_url_path = await upload_file_to_firebase(file)

    # Save metadata to Firestore
    cv_data = {
        'file_name': filename,
        'id': cv_id,
        'public_url_path': public_url_path,
    }
    firestore_db.collection('CV_database').document(cv_id).set(cv_data)

    # Save metadata to Realtime Database
    realtime_db_ref.child(f'CV_db_url/{cv_id}').set(cv_data)

    return {"cv_id": cv_id, "public_url": public_url_path}



# Route to upload JD
@app.post("/upload/jd/")
async def upload_jd(file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOC files are allowed.")

    # Upload file to Firebase and get the details
    filename, jd_id, public_url_path = await upload_file_to_firebase(file)

    # Save metadata to Firestore
    jd_data = {
        'file_name': filename,
        'id': jd_id,
        'public_url_path': public_url_path,
    }
    firestore_db.collection('JD_database').document(jd_id).set(jd_data)

    # Save metadata to Realtime Database
    realtime_db_ref.child(f'JD_db_url/{jd_id}').set(jd_data)

    return {"jd_id": jd_id, "public_url": public_url_path}



@app.post("/process_cv")
async def process_cv(cv_id: str = Body(...)):
    """Process the CV by its ID and extract keywords."""
    # Get the public URL from Firestore
    cv_ref = firestore_db.collection("CV_database").document(cv_id)
    cv_doc = cv_ref.get()

    if not cv_doc.exists:
        raise HTTPException(status_code=404, detail="CV not found")

    public_url_path = cv_doc.to_dict().get('public_url_path')
    
    if not public_url_path:
        raise HTTPException(status_code=404, detail="Public URL path not found")

    # Load and process the PDF
    try:
        documents = load_pdf(public_url_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PDF: {str(e)}")

    # Create a prompt for Google Generative AI using the specified text


    try:
        cv_result = await query_google_generative_ai(documents, True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying AI: {str(e)}")

    # Return the CV result
    return cv_result

@app.post("/process_jd")
async def process_jd(jd_id: str = Body(...)):
    """Process the JD by its ID and extract keywords."""
    # Get the public URL from Firestore
    jd_ref = firestore_db.collection("JD_database").document(jd_id)
    jd_doc = jd_ref.get()

    if not jd_doc.exists:
        raise HTTPException(status_code=404, detail="JD not found")

    public_url_path = jd_doc.to_dict().get('public_url_path')
    
    if not public_url_path:
        raise HTTPException(status_code=404, detail="Public URL path not found")

    # Load and process the PDF
    try:
        documents = load_pdf(public_url_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PDF: {str(e)}")

    try:
        jd_result = await query_google_generative_ai(documents, False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying AI: {str(e)}")

    # Return the JD result
    return jd_result

# @app.post("/compare_cv_jd")
# async def compare_cv_jd(project_name: str = Body(...), cv_id: str = Body(...), jd_id: str = Body(...)):
#     """Compare CV and JD and count the number of similarity keywords between them."""
    
    
#     # Process the CV
#     cv_response = await process_cv(cv_id)
#     cv_summary = cv_response["summary"]

#     # Process the JD
#     jd_response = await process_jd(jd_id)
#     jd_summary = jd_response["summary"]


#     print("################# CV ################# ")
#     cv_summary = clean_ans(cv_summary)
#     print(cv_summary)
#     cv_keyword_dict = extract_keywords_cv(cv_summary)
#     cv_other_infor = extract_other_infor(cv_summary)
#     print(cv_keyword_dict)
#     print("################# JD ################# ")
#     jd_summary = clean_ans(jd_summary)
#     print(jd_summary)
#     jd_keyword_dict = extract_keywords_jd(jd_summary)
#     print(jd_keyword_dict)
#     keyword_dict, point = algorithm_matching(cv_other_infor, cv_keyword_dict, jd_keyword_dict)
    
#     # project_id = str(uuid.uuid4())
    
#     # project_data = {
#     #     'file_name': project_name,
#     #     'project_id': project_id,
#     #     'cv_id': cv_id,
#     #     'jd_id': jd_id,
#     #     'matching_score': point
#     # }
#     # firestore_db.collection('Result_database').document(project_id).set(project_data)
#     print(f'Keyword_dict type: {type(keyword_dict)}')
    # project_data = upload_result_to_firebase(project_name=project_name, cv_id=cv_id, jd_id=jd_id, score=point, matching_keyword_dict=keyword_dict)
    
#     # return {
#     #     "cv_keywords": cv_keyword_dict,
#     #     "jd_keywords": jd_keyword_dict,
#     #     # "similarity_count": similarity_count,
#     #     "similarity_keywords": keyword_dict,
#     #     "final_result": point
#     # }
#     return project_data


@app.post("/compare_cv_jd")
async def compare_cv_jd(project_name: str = Body(...), cv_id: str = Body(...), jd_id: str = Body(...)):
    """Compare CV and JD and count the number of similarity keywords between them."""
    
    
    # Process the CV
    cv_response = await process_cv(cv_id)

    # Process the JD
    jd_response = await process_jd(jd_id)

    algorithm_result = summary_algorithm(cv_response, jd_response)
    matching_keywords, matching_score, total_keywords = clean_algorithm_result(algorithm_result)
    project_data = upload_result_to_firebase(project_name=project_name, cv_id=cv_id, jd_id=jd_id, score=int(matching_score), matching_keyword_dict=matching_keywords, total_keyword=total_keywords)
    
    return project_data

@app.get("/get/project")
async def get_project():
    all_project_files = get_all_project_files()
    return all_project_files

@app.get("/get/cv")
async def get_cv():
    all_project_files = get_all_cv_files()
    return all_project_files

@app.get("/get/jd")
async def get_jd():
    all_project_files = get_all_jd_files()
    return all_project_files

@app.get("/get/delete_project")
async def delete_project(project_id: str):
    delete_project_with_id(project_id)
    return {"message": "Project deleted successfully"}

@app.get("/get/delete_cv")
async def delete_cv(cv_id: str):
    delete_cv_with_id(cv_id)
    return {"message": "CV deleted successfully"}

@app.get("/get/delete_jd")
async def delete_jd(jd_id: str):
    delete_jd_with_id(jd_id)
    return {"message": "JD deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

