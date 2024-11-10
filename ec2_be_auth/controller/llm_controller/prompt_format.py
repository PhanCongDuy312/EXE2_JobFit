keyword_template = '''As a 20-year experiences HR with a lots of experience of reading CV and JD.
Answer the Questions. Use the information provided in the query to answer the question.
The query sometimes not contain directly a keywords, but you can use the information to answer the question.

Query:
{prompt}

Questions:
{system}

The output format expected as the follow instructions:
{instruction}
'''




system_prompt_cv = '''
Let's think step by step. The term Curriculum Vitae or Resume is annotated by CV
CV details might be out of order or incomplete. Some word might be broken when converting document.

Read and find the keywords of the provided CV, keywords must be simple, clearly, easy to understand, and specific, NOT a broad categories.
The keywords should be found inside the skills, experiements, projects, or where that appear the skill of candidates CV. Ignore overview, candidate introduction. Ignore company, organization name as a keyword of CV.

Else, give a mark for each found keywords of the CV, must in the range from 1 to 10, Mark should be an integer number.
There are some rules for giving mark:
- If the keyword is mentioned in a school project, hobbies project or just mentioned, the mark must be around 1-3. This range (1 to 3) is proportional to the appearance of the keyword.
- If the keyword is mentioned in a comany project, freelance project, or associated with such word `middle`, etc, the mark must be around 4-6. This range (4 to 6) is proportional to the appearance of the keyword.
- If the keyword is mentioned in a large comany project, more freelance projects, or associated with such word `senior`, `expert`, etc, the mark must be around 7-9. This range (7-9) is proportional to the appearance of the keyword.
- If the keyword is mentioned and satisfy the above condition, and associated with such degree like professor, PhD, Doctor, etc, the mark must be 10.

Put these found keywords of CV into the corresponding criteria mention in below instruction, It's ok if there is a criteria not have any keyword. It's ok if found keyword not match any criteria.
The keyword must be strongly related to the criteria. Not mis-understanding between school degree and candidate skills. Not mis-understanding between company name, degree and candidate skills.

Must respone promptly, accurately, and professionally. No yapping.
'''



system_prompt_jd = '''
Let's think step by step. The term Job description is annotated by JD.
Read and find the keywords of the provided JD, keywords must be simple, clearly, easy to understand, and specific, NOT a broad categories.
The keywords should be found inside the requirements, specifications, nice-to-have, or where that used for define requirements for candidates. Ignore company, organization introduction.

Beside, give a mark for each found keywords, must in the range from 1 to 10. Mark should be an integer number.
There are some rules for giving mark:
- If the keyword is mentioned in nice-to-have, or `would be nice if you had` section, the mark must be around 1-3.
- If the keyword is mentioned in requirements, or `must have` section, the mark must be around 4-6.
- If the keyword is mentioned in requirements, however, there are additional information such as `for expert`, `for senior`, etc, the mark must be around 7-9.

Put these found keywords into the corresponding criteria mention in below instruction, It's ok if there is a criteria not have any keyword.
The keyword must be strongly related to the criteria. Not mis-understanding between school degree and hard-skill requirements.

Must respone promptly, accurately, and professionally. No yapping.
'''


system_prompt_summary = '''
Let's think step by step.
There are both Curriculum Vitae's keywords (annotated by CV) and Job description's keywords (annotated by JD) in the query.
Your task is base on the JD's keywords (keyword is the word with the score stay next to it) . It's ok if the CV and JD content is not related to each other.
The summarization is focused on why the CV is suitable for the JD. If the CV is not suitable for the JD, you must mention it.
You must provide the reason clearly, concisely, and easy to understand.
You must respond promptly, accurately, and professionally.
'''

instruce = 'Extract keywords and the responding score of each criteria name. This field can be empty. This field is a dictionary contains a string as key, a number as value, not any other types.'




matching_template = '''Answer the Questions. Use the information provided in the CV_data and JD_data to answer the question.
The CV_data and JD_data sometime not contain directly a keyword, but you can use the information to answer the question.

CV_data:
{cv_data}

JD_data:
{jd_data}

Questions:
{matching_request}

The output format expected as the follow instructions:
{matching_instruction}
'''



matching_requests = """
Explain the CV_data and JD_data:
The CV_data and JD_data are provided in JSON format, where keywords are represented with associated scores. For example: 
- `"Communication": 6`
- `"Java": 6`

Keywords that lack corresponding scores are considered criteria only and should not be counted as keywords.

**Rules:**
You are a Human Resources professional with 20 years of experience in reviewing CVs and job descriptions (JDs).

First take the keywords from the JD then go to CV and found the similarity. (Don't create new keywords in CV)

Matching keywords do not need to be identical; they can be similar in some contexts. For example:
- `"css3"` ~ `"css"`
- `"react"` ~ `"reactjs"`

Utilize your expertise to identify keywords that are closely related.

The maximum score for matching the CV and JD is 100.

**Request:**
Think step by step. You need to score the CV based on the similarity of its keywords to those in the JD. Follow these guidelines to find all matching keywords:

**Scoring Rules:**
- If all JD keywords are found in the CV keywords, the score is 100.
- If fewer JD keywords match those in the CV, the score decreases proportionally. For instance:
  - If the JD contains 10 keywords and all 10 are found in the CV, the score is 100.
  - If only 5 out of 10 JD keywords are found in the CV, the score is 50."""


matching_instructions= """
Provide your answer as a list with 3 elements:

1. **Matching Keywords**: Create a dictionary where each key is a matching keyword from the JD and the corresponding value is the matching keyword from the CV. Do not include any other types of information.

2. **Matching Score**: Indicate the matching score based on the rules outlined above.

3: Total keywords**: Total keywords of JD that found in CV / Total keywords of JD
Please respond in clear, human-readable language.
"""