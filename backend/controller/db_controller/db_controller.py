from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, storage, db, firestore
from fastapi import  UploadFile
import uuid
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from io import BytesIO
from fastapi import FastAPI, HTTPException

load_dotenv()


# Get values from environment variables
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
firebase_database_url = os.getenv('FIREBASE_DATABASE_URL')
firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')


# Initialize Firebase Admin SDK with service account credentials
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_database_url,  # Realtime Database URL
    'storageBucket': firebase_storage_bucket  # Storage Bucket
})


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

async def check_cv_types(file: UploadFile):
    pdf_bytes = await file.read()
    
    # Use BytesIO to create a file-like object
    pdf_file_like = BytesIO(pdf_bytes)
    loader = PyPDFLoader(pdf_file_like).load_and_split()
    content = ""
    for _data in loader:
        _content = [line.strip()
                    for line in _data.page_content.splitlines() if line.strip() != ""]
        content += "\n".join(_content) + "\n"
    newline_count = content.count("\n")
    pdf_format = True if newline_count < 20 else False
    return pdf_format



def upload_result_to_firebase(project_name: str, cv_id: int, jd_id: int, score: int,matching_keyword_dict:dict, total_keyword:str):

    project_id = str(uuid.uuid4())

    # Save metadata to Firestore
    project_data = {
        'file_name': project_name,
        'project_id': project_id,
        'cv_id': cv_id,
        'jd_id': jd_id,
        'matching_keyword_dict': str(matching_keyword_dict),
        'score': score,
        'total_keyword': total_keyword
    }
    print("Project data", project_data)
    firestore_db.collection('Project_database').document(project_id).set(project_data)

    # Save metadata to Realtime Database
    # realtime_db_ref.child(f'Project_db_url/{project_id}').set(project_data)

    return project_data



def get_all_project_files():
    project = firestore_db.collection('Project_database').stream()
    all_project_files = []
    for project_doc in project:
        project_data = project_doc.to_dict()  # Convert document to dictionary
        all_project_files.append(project_data)

    return all_project_files

def get_all_cv_files():
    project = firestore_db.collection('CV_database').stream()
    all_project_files = []
    for project_doc in project:
        project_data = project_doc.to_dict()  # Convert document to dictionary
        all_project_files.append(project_data)

    return all_project_files


def get_all_jd_files():
    project = firestore_db.collection('JD_database').stream()
    all_project_files = []
    for project_doc in project:
        project_data = project_doc.to_dict()  # Convert document to dictionary
        all_project_files.append(project_data)

    return all_project_files

def delete_project_with_id(project_id: str):
    try:
        # Reference the document based on the project_id
        doc_ref = firestore_db.collection('Project_database').document(project_id)
        
        # Check if the document exists
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Project not found")

        # Delete the document
        doc_ref.delete()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete project")
    
def delete_cv_with_id(cv_id: str):
    try:
        # Reference the document based on the cv_id
        doc_ref = firestore_db.collection('CV_database').document(cv_id)
        
        # Check if the document exists
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="cv not found")

        # Delete the document
        doc_ref.delete()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete cv")
    
    
def delete_jd_with_id(jd_id: str):
    try:
        # Reference the document based on the jd_id
        doc_ref = firestore_db.collection('JD_database').document(jd_id)
        
        # Check if the document exists
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="jd not found")

        # Delete the document
        doc_ref.delete()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete jd")

    
    
    
    