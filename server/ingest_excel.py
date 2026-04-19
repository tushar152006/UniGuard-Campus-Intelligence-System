import os
import json
import pathlib
import sys
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR.parent / "data" / "logs"

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL: GEMINI_API_KEY missing from .env")
    sys.exit(1)

genai.configure(api_key=api_key)

def process_excel_report(csv_content):
    print(">> Initializing Neural Ingestion Pipeline for Excel Data...")
    
    prompt = f"""
    You are an AI document processor for a university operations dashboard.
    Read the following EXCEL SHEET DATA (in CSV format) and extract the information into a structured JSON array of objects.
    Each row in the dataset represents an individual case that should have its own public and private entries.

    DATA (CSV):
    {csv_content}

    TASK:
    Output pure JSON matching exactly this schema (an array of objects), with no markdown code blocks starting with ```json:
    [
      {{
        "public": {{
          "date": "YYYY-MM-DD",
          "block": "Block name/number",
          "indicator": "Health Alert or specific category like Fever/Food Poisoning",
          "summary": "Brief, abstract summary (no names, no IDs).",
          "is_crisis": false,
          "official_verdict": "Clear message preventing panic or giving advice, or N/A"
        }},
        "private": {{
          "date": "YYYY-MM-DD",
          "block": "Block name/number",
          "floor": "",
          "room": "Room number",
          "student_id": "Student ID",
          "student_name": "Name",
          "condition": "Symptoms and Notes",
          "temperature": "Extract from symptoms/notes if present, otherwise 'N/A'",
          "action": "Prescribed medicines & Action taken",
          "contact": "Mobile Number"
        }}
      }}
    ]
    
    If data is missing for a field, put "N/A". Ensure valid JSON structure, pure array output exactly matching the schema.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    try:
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_text)
        return parsed_data
    except Exception as e:
        print(f"Error parsing Gemini output: {e}")
        print("Raw response:", response.text)
        sys.exit(1)

def append_to_logs(parsed_data_array):
    if not isinstance(parsed_data_array, list):
        print("Error: Expected a list of parsed cases, got something else.")
        sys.exit(1)

    public_file = DATA_DIR / "public_status.json"
    private_file = DATA_DIR / "health" / "private_admin.json"
    
    # Update Public Knowledge Base
    if public_file.exists():
        with open(public_file, "r") as f:
            try:
                public_logs = json.load(f)
            except json.JSONDecodeError:
                public_logs = []
    else:
        public_logs = []
    
    # Update Private Admin Database
    if private_file.exists():
        with open(private_file, "r") as f:
            try:
                private_logs = json.load(f)
            except json.JSONDecodeError:
                private_logs = []
    else:
        private_logs = []
        
    for item in parsed_data_array:
        if "public" in item:
            public_logs.insert(0, item["public"])
        if "private" in item:
            private_logs.insert(0, item["private"])
            
    with open(public_file, "w") as f:
        json.dump(public_logs, f, indent=2)
    print("✅ Public Knowledge Graph updated (Anonymized data).")

    with open(private_file, "w") as f:
        json.dump(private_logs, f, indent=2)
    print("✅ Secure Admin Database updated (Includes PII).")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest regular tabular reports (Excel) into the UniGuard JSON Database")
    parser.add_argument("file", help="Path to Excel (.xlsx) file")
    
    args = parser.parse_args()
    file_path = pathlib.Path(args.file)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    print(f"--- Processing {file_path.name} ---")
    
    try:
        df = pd.read_excel(file_path)
        csv_content = df.to_csv(index=False)
    except Exception as e:
        print(f"Failed to read Excel file: {e}")
        sys.exit(1)
        
    extracted_array = process_excel_report(csv_content)
    append_to_logs(extracted_array)
    print(">> Excel Pipeline Complete. UniGuard Chatbot is now aware of new data from Doctor's Sheet.")
