import os
import uuid
import jwt  # JWT library for encoding/decoding tokens
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer

from pydantic import BaseModel
from dotenv import load_dotenv

from controller.main_controller.main_controller import *
from controller.llm_controller.llm_controller import *
from controller.jd_controller.jd_controller import *
from controller.cv_controller.cv_controller import *
from controller.db_controller.db_controller import *
from controller.matching_controller.matching_controller import *


from tempfile import NamedTemporaryFile
from pdf2docx import Converter
from io import BytesIO
import shutil
from pydantic import BaseModel

load_dotenv()

# FastAPI app initialization
app = FastAPI(
    title="Enhanced FastAPI JWT Authentication",
    description="An optimized FastAPI application with JWT-based authentication.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Middleware configuration
# origins = ["http://localhost", "http://localhost:5173"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# JWT configuration
JWT_SECRET = '123456'
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Helper functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate a JWT token."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=JWT_EXPIRATION_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    """Validate JWT token and return the username."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Models
class RegisterRequest(BaseModel):
    username: str
    password: str



# Authentication endpoints
@app.post("/login", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login with OAuth2PasswordRequestForm.
    Returns a JWT token upon successful authentication.
    """
    print("formdata",form_data.username)
    account_exist = login_check_user(str(form_data.username), str(form_data.password))
    
    if account_exist == 3:
        token = create_access_token(data={"sub": form_data.username})
        return {"access_token": token, "token_type": "bearer"}
    elif account_exist == 0:
        raise HTTPException(status_code=404, detail="User not found")
    elif account_exist == 1:
        raise HTTPException(status_code=403, detail="Incorrect password")
    raise HTTPException(status_code=500, detail="Authentication failed")


@app.post("/register", tags=["Authentication"])
async def register(request: RegisterRequest):
    """
    Register a new user.process_cv
    """
    if register_check_user(request.username) == 1:
        raise HTTPException(status_code=400, detail="User already exists")
    if create_user_data(request.username, request.password):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=500, detail="Registration failed")

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

# # Route to upload CV
# @app.post("/upload/cv/")
# async def upload_cv(file: UploadFile = File(...)):
#     if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
#         raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOC files are allowed.")

#     # if file.content_type in ["application/pdf"]:
#     #     pdf_format = await check_cv_types(file)
#         # Upload file to Firebase and get the details
#     filename, cv_id, public_url_path = await upload_file_to_firebase(file)

#     # Save metadata to Firestore
#     cv_data = {
#         'file_name': filename,
#         'id': cv_id,
#         'public_url_path': public_url_path,
#     }
#     firestore_db.collection('CV_database').document(cv_id).set(cv_data)

#     # Save metadata to Realtime Database
#     realtime_db_ref.child(f'CV_db_url/{cv_id}').set(cv_data)

#     return {"cv_id": cv_id, "public_url": public_url_path}
@app.post("/upload/cv/")

async def upload_cv(file: UploadFile = File(...), username: str = Depends(validate_token)):
    if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOC files are allowed.")

    # if file.content_type in ["application/pdf"]:
    #     pdf_format = await check_cv_types(file)
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



@app.post("/compare_cv_jd")
async def compare_cv_jd(project_name: str = Body(...), cv_id: str = Body(...), jd_id: str = Body(...)):
    """Compare CV and JD and count the number of similarity keywords between them."""
    
    
    # Process the CV
    cv_response = await process_cv(cv_id)

    # Process the JD
    jd_response = await process_jd(jd_id)

    print(f"CV response: {cv_response}")
    print(f"JD response: {jd_response}")

    algorithm_result = summary_algorithm(cv_response, jd_response)
    matching_keywords, matching_score = clean_algorithm_result(algorithm_result)
    print("matching_keywords", matching_keywords)
    
    total_elements = len(matching_keywords)

    # Count how many values are 'Not found'
    not_found_count = sum(1 for value in matching_keywords.values() if value == 'Not found')

    total_keywords = (f"{total_elements - not_found_count}/{total_elements}")    
    print("total keywords: ",total_keywords)
    best_score = tanh_functions(matching_keyword=matching_keywords, cv_data=cv_response, jd_data=jd_response)
    
    project_data = upload_result_to_firebase(project_name=project_name, cv_id=cv_id, jd_id=jd_id, score=float(best_score), matching_keyword_dict=matching_keywords, total_keyword=total_keywords)
    
    return project_data


@app.get("/get/cv")
async def get_cv(username: str = Depends(validate_token)):
    """Get CV details."""
    print(f"Authenticated user: {username}")  # Log authenticated user
    # Replace this with actual logic to fetch CVs for the user
    _ = get_user_cv_details(username)
    return {"message": f"Returning CVs for user {username}"}

@app.get("/get/jd")
async def get_cv(username: str = Depends(validate_token)):
    """Get CV details."""
    print(f"Authenticated user: {username}")  # Log authenticated user
    # Replace this with actual logic to fetch CVs for the user
    _ = get_user_jd_details(username)
    return {"message": f"Returning JDs for user {username}"}

@app.get("/get/project")
async def get_cv(username: str = Depends(validate_token)):
    """Get CV details."""
    print(f"Authenticated user: {username}")  # Log authenticated user
    # Replace this with actual logic to fetch CVs for the user
    _ = get_user_project_details(username)
    return {"message": f"Returning Projects for user {username}"}



# @app.get("/get/jd")
# async def get_jd():
#     all_project_files = get_all_jd_files()
#     return all_project_files

@app.delete("/get/delete_project")
async def delete_project(project_id: str):
    delete_project_with_id(project_id)
    return {"message": "Project deleted successfully"}

@app.delete("/get/delete_cv")
async def delete_cv(cv_id: str):
    delete_cv_with_id(cv_id)
    return {"message": "CV deleted successfully"}

@app.delete("/get/delete_jd")
async def delete_jd(jd_id: str):
    delete_jd_with_id(jd_id)
    return {"message": "JD deleted successfully"}

# if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

