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

def login_check_user(username: str, password: str):
    print("username:", username)
    # Get all collections
    collections = firestore_db.collections()
    check_exist = 0
    
    for collection in collections:
        collection_name = collection.id        
        # Check if the collection name matches the username
        if collection_name == username:
            print(f"The '{username}' account exists.")
            check_exist += 1
            docs = firestore_db.collection(username).document('account_data')
            doc = docs.get().to_dict()
            check_password = doc.get('password')
            if check_password == password:
                check_exist += 2
            break
        
    return check_exist

def register_check_user(username: str):
    # Get all collections
    collections = firestore_db.collections()
    check_exist = 0
    
    for collection in collections:
        collection_name = collection.id        
        # Check if the collection name matches the username
        if collection_name == username:
            print(f"The '{username}' account exists.")
            check_exist += 1
            break
        
    return check_exist


def create_user_data(username: str, password: str):
    try:
        # Reference to the collection and document named after the username
        user_collection = firestore_db.collection(username)
        user_doc = user_collection.document('account_data')

        # Set data with username and password fields
        user_doc.set({
            'username': username,
            'password': password
        })
        
        print(f"Collection '{username}' and document 'account_data' created with username and password fields.")
        return True
    except Exception as e:
        print("An error occurred while creating the user:", e)
        return False
    

async def upload_user_data(username: str, password: str):
    user_data = {
        'usename': username,
        'password': password
    }
    firestore_db.collection(username).document("").set(user_data)


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



def upload_result_to_firebase(project_name: str, cv_id: int, jd_id: int, score: float,matching_keyword_dict:dict, total_keyword:str):

    project_id = str(uuid.uuid4())
    # Save metadata to Firestore
    project_data = {
        'file_name': project_name,
        'project_id': project_id,
        'cv_id': cv_id,
        'jd_id': jd_id,
        'matching_keyword_dict': matching_keyword_dict,
        'score': score,
        'total_keyword': total_keyword
    }
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

#####################################################################################################    
    
    
    
    
    
def get_user_cv_details(username: str):
    try:
        # Access the 'CV_ids' document in the collection named after the username
        cv_ids_doc_ref = firestore_db.collection(username).document('CV_ids')
        cv_ids_doc = cv_ids_doc_ref.get()

        # Check if the document exists
        if cv_ids_doc.exists:
            # Get the 'ids' field and split it into individual IDs
            ids_str = cv_ids_doc.get('ids')
            if ids_str:
                cv_ids = ids_str.split(', ')
                
                # Loop through each ID to retrieve CV details from 'CV_database'
                for cv_id in cv_ids:
                    cv_doc_ref = firestore_db.collection('CV_database').document(cv_id)
                    cv_doc = cv_doc_ref.get()

                    # Check if the document exists and print details
                    if cv_doc.exists:
                        print(f"Details for CV ID {cv_id}:")
                        print(cv_doc.to_dict())
                    else:
                        print(f"No document found for CV ID {cv_id}")
            else:
                print("No IDs found in the 'ids' field.")
        else:
            print(f"Document 'CV_ids' does not exist in '{username}' collection.")

    except Exception as e:
        print("An error occurred:", e)
        
        
def get_user_jd_details(username: str):
    try:
        # Access the 'CV_ids' document in the collection named after the username
        jd_ids_doc_ref = firestore_db.collection(username).document('JD_ids')
        jd_ids_doc = jd_ids_doc_ref.get()

        # Check if the document exists
        if jd_ids_doc.exists:
            # Get the 'ids' field and split it into individual IDs
            ids_str = jd_ids_doc.get('ids')
            if ids_str:
                jd_ids = ids_str.split(', ')
                
                # Loop through each ID to retrieve jd details from 'jd_database'
                for jd_id in jd_ids:
                    jd_doc_ref = firestore_db.collection('JD_database').document(jd_id)
                    jd_doc = jd_doc_ref.get()

                    # Check if the document exists and print details
                    if jd_doc.exists:
                        print(f"Details for JD ID {jd_id}:")
                        print(jd_doc.to_dict())
                    else:
                        print(f"No document found for JD ID {jd_id}")
            else:
                print("No IDs found in the 'ids' field.")
        else:
            print(f"Document 'jd_ids' does not exist in '{username}' collection.")

    except Exception as e:
        print("An error occurred:", e)
        
        
        
def get_user_project_details(username: str):
    try:
        # Access the 'CV_ids' document in the collection named after the username
        project_ids_doc_ref = firestore_db.collection(username).document('Project_ids')
        project_ids_doc = project_ids_doc_ref.get()

        # Check if the document exists
        if project_ids_doc.exists:
            # Get the 'ids' field and split it into individual IDs
            ids_str = project_ids_doc.get('ids')
            if ids_str:
                project_ids = ids_str.split(', ')
                
                # Loop through each ID to retrieve project details from 'project_database'
                for project_id in project_ids:
                    project_doc_ref = firestore_db.collection('Project_database').document(project_id)
                    project_doc = project_doc_ref.get()

                    # Check if the document exists and print details
                    if project_doc.exists:
                        print(f"Details for project ID {project_id}:")
                        print(project_doc.to_dict())
                    else:
                        print(f"No document found for project ID {project_id}")
            else:
                print("No IDs found in the 'ids' field.")
        else:
            print(f"Document 'project_ids' does not exist in '{username}' collection.")

    except Exception as e:
        print("An error occurred:", e)