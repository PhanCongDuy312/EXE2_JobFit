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
from controller.llm_controller.prompt_format import *
from langchain import PromptTemplate
import json
load_dotenv()


google_api_key = os.getenv('GOOGLE_API_KEY')
print(google_api_key)
chat_model = ChatGoogleGenerativeAI(google_api_key=google_api_key, temperature=0, model="gemini-pro", request_timeout=120)


# def cv_query_google_generative_ai(prompt: str) -> str:
#     formated_prompt = format_cv_prompt(prompt)
#     response = chat_model.invoke([{"role": "user", "content": str(formated_prompt)}])  # Use the invoke method
#     return response.content  # Access the content directly from the response

# def jd_query_google_generative_ai(prompt: str) -> str:
#     formated_prompt = format_jd_prompt(prompt)
#     response = chat_model.invoke([{"role": "user", "content": str(formated_prompt)}])  # Use the invoke method
#     return response.content  # Access the content directly from the response

async def query_google_generative_ai(prompt: str, cv:bool) -> str:
    if cv == True:
        formated_prompt = await format_cv_prompt(prompt)
        response = chat_model.invoke([{"role": "user", "content": str(formated_prompt)}])  # Use the invoke method
        return response.content  # Access the content directly from the response

    formated_prompt = await format_jd_prompt(prompt)
    response = chat_model.invoke([{"role": "user", "content": str(formated_prompt)}])  # Use the invoke method
    return response.content  # Access the content directly from the response



async def format_jd_prompt(jd_data:str):
    prompt_template = PromptTemplate(
    input_variables=["prompt", 'system', 'instruction'],
    template=keyword_template
    )

    formated = prompt_template.format(
            prompt=jd_data,
            system=system_prompt_jd,
            instruction=instruce
        )
    return formated

async def format_cv_prompt(cv_data:str):
    prompt_template = PromptTemplate(
    input_variables=["prompt", 'system', 'instruction'],
    template=keyword_template
    )

    formated = prompt_template.format(
            prompt=cv_data,
            system=system_prompt_cv,
            instruction=instruce
        )
    return formated


def summary_algorithm(cv_data: str, jd_data: str):
    formated_prompt =  format_final_prompt(cv_data, jd_data)

    response = chat_model.invoke([{"role": "user", "content": str(formated_prompt)}])  # Use the invoke method

    

    return response.content  # Access the content directly from the response
    
def format_final_prompt(cv_datas: str, jd_datas:str):
    prompt_template = PromptTemplate(
    input_variables=["cv_data", 'jd_data', 'matching_request', 'matching_instruction'],
    template=matching_template
    )

    formated = prompt_template.format(
            cv_data=cv_datas,
            jd_data=jd_datas,
            matching_request=matching_requests,
            matching_instruction=matching_instructions
        )
    return formated

def clean_algorithm_result(data: str):
    data = str(data)
    print("DATA before clean: ",data)
    # cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', data)
    # print("DATA after clean: ",cleaned_text)
    
    matching_keywords_cleaned = {}  # Initialize the dictionary outside the try-except

    try:
        dict_match = re.search(r'```(.*?)```', data, re.DOTALL).group(1).strip()
        matching_keywords = json.loads(dict_match)
        matching_keywords_cleaned = {key: (value if value is not None else "None") for key, value in matching_keywords.items()}
    except:
        matching_keywords = {}
        for line in data.splitlines():
            if "- " in line:  # Look for lines with a match
                key_value = line.split("- ")[1].split(": ")
                keyword = key_value[0].strip()
                match = key_value[1].strip()
                matching_keywords_cleaned[keyword] = match

    
    # matching_keywords_cleaned = {"No matching keywords": "None"} if matching_keywords_cleaned is None else matching_keywords_cleaned
                
    # Extract the matching score
    matching_score = int(re.search(r"\*\*Matching Score\*\*: (\d+)", data).group(1))


            
    return matching_keywords_cleaned, matching_score


