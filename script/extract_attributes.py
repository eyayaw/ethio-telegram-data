import json
import os
import logging
import subprocess
import time
from tqdm import tqdm
import google.generativeai as genai  # pip install google-generativeai

logging.basicConfig(level=logging.INFO, filename="./logs/gemini.log")
api_key = os.environ["GOOGLE_GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Set up the model
generation_config = {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

prompt = """
Extract structured information from job postings in English or other languages. Prioritize accuracy and consistency in managing partial information and ambiguities. Utilize automated language translation for non-English languages. Structure the output as a JSON object according to the provided schema, marking 'NA' for missing or inapplicable information.

**Schema for JSON Object:**

-  "job_title": Title of the job (e.g., Software Engineer, Data Scientist)
-  "job_type": Type of job (full-time, part-time, contract)
-  "salary": Salary range in numeric values
-  "salary_unit": Frequency of the salary (hourly, weekly, monthly, annually)
-  "job_location": Location of the job
-  "experience_required": Years of experience required
-  "education_required": Education level required (e.g., Bachelor's, Master's, PhD)
-  "skills_required": Array of required skills (e.g., Python, SQL)
-  "responsibilities": Array of job responsibilities
-  "benefits": Array of job benefits (e.g., health insurance, retirement plan)
-  "company_name": Name of the hiring company
-  "company_type": Type of company (e.g., startup, corporation)
-  "company_size": Size of the company (number of employees)
-  "company_industry": Industry of the company (e.g., tech, healthcare)
-  "application_deadline": Deadline for application
-  "application_link": Link to apply for the job
-  "job_description": Full job description
-  "date_created": Date the job posting was created
-  "date_updated": Date the job posting was last updated
-  "remarks": Additional relevant information or comments

**Key Considerations:**

-  Prioritize accuracy and consistency in managing partial information and ambiguities.
-  Utilize automated language translation for non-English languages.
-  Infer attributes based on context when not explicitly mentioned.
-  Mark inapplicable attributes as 'NA'.
-  Use arrays for multiple values.
- Return a valid json, make sure nested quotes are escaped.


**Example**:
**input**: "የሽያጭ ባለሙያ
#nishan_business_plc
#business
#Addis_Ababa
10+1 ከዚያ በላይ በማርኬቲንግ ማኔጅመንት ወይም በሴልስ ማንሺፕ የተማረና በቤት ሽያጭ ላይ ልምድ ያለው
የስራ ቦታ፡ አራት ኪሎ
Quanitity Required: 1
Minimum Years Of Experience: #0_years
Maximum Years Of Experience: #1_years
Salary: 5000.00
Deadline: December 13, 2023
How To Apply: አመልካቾች  የትምህርትና የስራ ልምድ ማስረጃዎቻችሁንና የማይመለስ ኮፒ በማያያዝ በአካል ድርጅቱ በሚገኝበት አራት ኪሎ አራዳ ክ/ከተማ ፊት ሇፊት ዴንቨር ህንጻ 2ኛ ፎቅ በመቅረብ ወይም በድርጅቱ ኢ-ሜይል አድራሻ nishanbusinesses@gmail.com በመላክ መመዝገብ ትችላላቹ

T.me/sera7"

**Output**:
```json
{
    "job_title": "የሽያጭ ባለሙያ",
    "job_type": "NA",
    "salary": 5000.00,
    "salary_unit": "NA",
    "job_location": "infront of 4kilo arada subcity Denver building 2nd floor, Addis Ababa",
    "experience_required": "experience in house sales",
    "education_required": "10+1 or higher in marketing management or salesmanship",
    "company_name": "nishan_business_plc",
    "company_type": "business",
    "company_size": "NA",
    "application_deadline": "December 13, 2023",
    "job_description": "NA",
    "date_created": "NA",
    "date_updated": "NA",
    "remarks": "አመልካቾች  የትምህርትና የስራ ልምድ ማስረጃዎቻችሁንና የማይመለስ ኮፒ በማያያዝ በአካል ድርጅቱ በሚገኝበት አራት ኪሎ አራዳ ክ/ከተማ ፊት ሇፊት ዴንቨር ህንጻ 2ኛ ፎቅ በመቅረብ ወይም በድርጅቱ ኢ-ሜይል አድራሻ nishanbusinesses@gmail.com በመላክ መመዝገብ ትችላላቹ"
}

```
"""


def extract_attributes(text):
    try:
        prompt_parts = [
            prompt,
            f'"input:" "{text}"',
            "output: ",
        ]
        response = model.generate_content(prompt_parts)
        if response.parts:
            output = response.text
        else:
            output = '```json\n{"error": "No content in response."}\n```'
        output = output.removeprefix("```json\n").removesuffix("```")
        output = json.loads(output)
        return {"input": text, "output": output}
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return {"input": text, "output": output}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"input": text, "output": "Unexpected error occurred."}


def extract_attributes_with_retry(text, max_retries=5):
    retry_delay = 1  # Start with 1 second
    for attempt in range(max_retries):
        try:
            return extract_attributes(text)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "504" in error_str:
                logging.warning(f"Error {e}. Retrying in {retry_delay} seconds.")
                reconnect_vpn()
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise e
    raise Exception("Max retries reached")


def reconnect_vpn():
    command = "hotspotshield connect us"
    subprocess.run(command, shell=True)


def remove_surrogates(obj):
    """
    Recursively remove surrogate characters from strings in the given object.
    Works with dictionaries, lists, and strings.
    """
    if isinstance(obj, dict):
        return {key: remove_surrogates(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [remove_surrogates(element) for element in obj]
    elif isinstance(obj, str):
        # Encode to UTF-8 ignoring errors, then decode back to a string
        return obj.encode("utf-8", "ignore").decode("utf-8")
    else:
        return obj


def main():
    # Load the data
    filename = "./data/hahujobs_2023-12-19.json"
    with open(filename) as f:
        texts = json.load(f)

    texts = {
        str(message["id"]): message["message"]
        for message in texts
        if "message" in message and message["message"]
    }
    results = {}
    for i, key in enumerate(tqdm(texts), 1):
        results[key] = extract_attributes_with_retry(texts[key])
        if i % 500 == 0 or i == len(texts):
            new_filename = f"./data/structured/{os.path.splitext(os.path.basename(filename))[0]}_temp_structured_gemini-pro_{i+1}.json"
            os.makedirs(os.path.dirname(new_filename), exist_ok=True)
            with open(new_filename, "w") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {new_filename}")

    new_filename = f"./data/structured/{os.path.splitext(os.path.basename(filename))[0]}_structured_gemini-pro.json"
    with open(new_filename, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Final results saved to {new_filename}")


if __name__ == "__main__":
    main()
