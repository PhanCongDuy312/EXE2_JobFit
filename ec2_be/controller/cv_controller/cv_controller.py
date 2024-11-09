from controller.db_controller.db_controller import *
from pdf2docx import Converter


def extract_keywords_cv(cleaned_data: str):
    result = {}
    
    keywords_part = cleaned_data.split("Keywords:")[1].split("OtherInforCV Content:")[0].strip()
    # Split the data by lines and loop through them
    for line in keywords_part.strip().splitlines():
        # Split each line by ":" to separate the key and value
        key, value = line.split(":")
        # Strip any excess whitespace and add to the dictionary
        result[key.strip()] = int(value.strip())
    return result


def extract_other_infor(cleaned_data: str):
    start_index = cleaned_data.find("OtherInforCV Content:")

    # Extract everything from that point onward
    other_info_content = cleaned_data[start_index:].strip()

    return other_info_content


def convert_pdf_to_docx(pdf_file, docx_file):
    cv = Converter(pdf_file)
    cv.convert(docx_file, start=0, end=None)
    cv.close()


async def convert_pdf_to_docx(pdf_file, docx_file):
    cv = Converter(pdf_file)
    cv.convert(docx_file, start=0, end=None)
    cv.close()