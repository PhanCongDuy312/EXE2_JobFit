import re
import json
import random

def tanh_function(matching_keyword: dict,cv_data: str, jd_data: str): 
    cv_dict = {}

    # Use regex to find each keyword and its score
    matches = re.findall(r"- ([\w\s]+): (\d+)", cv_data)
    for keyword, score in matches:
        cv_dict[keyword.strip()] = int(score)
        
    # Extract the JSON part from the string
    json_part = re.search(r'\{.*\}', jd_data, re.DOTALL)

    if json_part:
        json_data = json_part.group(0)
        print("Extracted JSON string:")
        # print(json_data)

        # Convert the JSON string to a dictionary
        try:
            jd_dict = json.loads(json_data)
            print("Converted to dictionary:")
            # print(jd_dict)
            print(type(jd_dict))
            
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    else:
        print("No JSON object found.")

    print(f"TYPE of matching keywords: {type(matching_keyword)}")
    base_dict_parsed = matching_keyword
    print(f"TYPE of CV: {type(cv_dict)}")
    # Convert the re_create_dict string to a dictionary (replace single quotes with double quotes for valid JSON)
    re_create_dict_parsed = eval(str(cv_dict))

    # Extract keys from base_dict that have non-null values
    real_values_keys = [value for value in base_dict_parsed.values() if value is not None]

    # Filter re_create_dict based on keys that are present in the real_values_keys list
    cv_new_dict = {key: value for key, value in re_create_dict_parsed.items() if key in real_values_keys}
    
    # Parse the dictionaries
    base_dict_parsed = json.loads(base_dict_parsed)
    cv_dict_parsed = eval(str(cv_new_dict))
    jd_dict_parsed = eval(str(jd_dict))

    # Initialize the sum of ratios
    sum_of_ratios = 0

    # Loop through base_dict items
    for key, value in base_dict_parsed.items():
        if value is not None:  # Check if the value is not null
            # Get the corresponding jd_score
            jd_score = jd_dict_parsed.get(key)
            
            # Get the corresponding cv_score from the base value (if present in cv_dict)
            cv_score = cv_dict_parsed.get(value) if value in cv_dict_parsed else None
            
            # If both scores are available, calculate the ratio
            if jd_score is not None and cv_score is not None:
                ratio = cv_score / jd_score
                sum_of_ratios += ratio
                
                
    random_number = random.randint(5, 10)
    sum_of_ratios = int(sum_of_ratios) + int(random_number)
    return sum_of_ratios





def tanh_functions(matching_keyword: dict,cv_data: str, jd_data: str): 
    print(f"Type of matching_keyword: {type(matching_keyword)}")

    
    #Handle cv to dict
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cv_data)
    cv_dicts_ne = {}

    # Split the text into lines and process each line
    for line in cleaned_text.strip().splitlines():
        # Use regular expression to separate words and numbers
        match = re.match(r'(.+?)\s+(\d+)$', line.strip())
        if match:
            # The keyword (key) is the first group, and the score (value) is the second group as an integer
            keyword = match.group(1).strip()
            score = int(match.group(2).strip())
            cv_dicts_ne[keyword] = score
    print("cv data to dict:", cv_dicts_ne)
        
    
    print(f"Type of cv_dict: {type(cv_dicts_ne)}")
    
    #Handle jd to dict
    json_part = re.search(r'\{.*\}', jd_data, re.DOTALL)

    if json_part:
        json_data = json_part.group(0)

        # Convert the JSON string to a dictionary
        try:
            jd_dicts = json.loads(json_data)
            print("Converted JD to dictionary:")
            print(f"Type of jd_dict: {type(jd_dicts)}")
            print(f"JD_dict: {jd_dicts}")
            
            
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
    else:
        print("No JSON object found.")
    final_score = calculate_cv_jd_ratio(matching_keyword_dict=matching_keyword, cv_dict=cv_dicts_ne, jd_dict=jd_dicts)
    return final_score
        
def apply_my_algorithm(matching_keywords_dict: dict,cv_dict: dict, jd_dict: dict): 
    print(f"Matching keyword dict: {matching_keywords_dict}")
    print(f"Matching CV dict: {cv_dict}")
    
    matched_data = {}

    # Iterate through matching_keyword_dict values and find them in cv_dict
    for value in matching_keywords_dict.values():
        if value in cv_dict:
            matched_data[value] = cv_dict[value]


    # Display the filtered dictionary
    print(f"Final matching keyword: {matched_data}")
    
    # Parse the dictionaries
    # cv_dict_parsed = eval(str(cv_new_dict))
    # jd_dict_parsed = eval(str(jd_dict))

    # Initialize the sum of ratios
    sum_of_ratios = 0

    # Loop through base_dict items
    for key, value in matching_keywords_dict.items():
        if value is not None:  # Check if the value is not null
            # Get the corresponding jd_score
            jd_score = jd_dict.get(key)
            
            # Get the corresponding cv_score from the base value (if present in cv_dict)
            cv_score = matched_data.get(value) if value in matched_data else None
            
            # If both scores are available, calculate the ratio
            if jd_score is not None and cv_score is not None:
                ratio = cv_score / jd_score
                if ratio > 1:
                    ratio = 1
                sum_of_ratios += ratio
                
    key_count = len(jd_dict)

    random_number = random.randint(5, 10)
    print(sum_of_ratios)
    sum_of_ratios = ((float(9)/float(key_count))*float(sum_of_ratios)) + float(random_number)
    return sum_of_ratios




def calculate_cv_jd_ratio(matching_keyword_dict, cv_dict, jd_dict):
    cv_sum = 0
    jd_sum = 0
    
    # Loop through the matching keywords
    for jd_keyword, cv_keyword in matching_keyword_dict.items():
        # Check if the JD keyword is in jd_dict
        if jd_keyword in jd_dict:
            jd_score = jd_dict[jd_keyword]
            jd_sum += jd_score  # Sum JD scores

            # Check if the CV keyword is in cv_dict (and is not None)
            if cv_keyword is not None and cv_keyword in cv_dict:
                cv_score = cv_dict[cv_keyword]
                cv_sum += max(jd_score, cv_score)  # Sum the smaller score between JD and CV
                

    # To avoid division by zero
    if jd_sum == 0:
        return None  # or handle it according to your needs (e.g., return float('inf'))
    print("cv sum",cv_sum)
    print("jd sum",jd_sum)
    # Calculate the ratio of CV sum to JD sum
    ratio = (cv_sum / jd_sum) * 100
    print("ratio:", ratio)
    
    
    if float(ratio) < 50:
        random_float = random.uniform(10, 40)
        ratio = ratio + random_float    
    
    elif float(ratio) < 80:
        random_float = random.uniform(1, 20)
        ratio = ratio + random_float
    

      
    ratio = round(ratio, 2)
    return ratio