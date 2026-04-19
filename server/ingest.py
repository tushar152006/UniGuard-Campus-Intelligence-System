import os
import json
import pathlib
import sys
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

def process_raw_report(text_content):
    print(">> Initializing Neural Ingestion Pipeline...")
    
    # We ask Gemini to extract TWO versions: One for standard students (abstract) and one for Admins (detailed).
    prompt = f"""
    You are an AI document processor for a university operations dashboard.
    Read the following RAW TEXT REPORT and extract the information into TWO structured JSON objects.

    RAW TEXT:
    {text_content}

    TASK:
    Output pure JSON matching exactly this schema, with no markdown code blocks starting with ```json:
    {{
      "public": {{
        "date": "YYYY-MM-DD",
        "block": "Block name/number",
        "indicator": "Health Alert or Mess Quality or Water",
        "summary": "Brief, abstract summary (no names, no IDs).",
        "is_crisis": false,
        "official_verdict": "Clear message debunking rumors or preventing panic"
      }},
      "private": {{
        "date": "YYYY-MM-DD",
        "block": "Block name/number",
        "floor": "",
        "room": "",
        "student_id": "",
        "student_name": "",
        "condition": "",
        "temperature": "",
        "action": "",
        "contact": ""
      }}
    }}
    
    If data is missing for a field, put "N/A". Ensure valid JSON structure.
    """

    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    
    try:
        # Clean the text if the model returned markdown blocks
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_text)
        return parsed_data
    except Exception as e:
        print(f"Error parsing Gemini output: {e}")
        print("Raw response:", response.text)
        sys.exit(1)

def append_to_logs(parsed_data):
    # 1. Update Public Knowledge Base
    public_file = DATA_DIR / "public_status.json"
    if public_file.exists():
        with open(public_file, "r") as f:
            public_logs = json.load(f)
    else:
        public_logs = []
    
    public_logs.insert(0, parsed_data["public"]) # Add to top
    with open(public_file, "w") as f:
        json.dump(public_logs, f, indent=2)
    print("✅ Public Knowledge Graph updated (Anonymized data).")

    # 2. Update Private Admin Database
    private_file = DATA_DIR / "health" / "private_admin.json"
    if private_file.exists():
        with open(private_file, "r") as f:
            private_logs = json.load(f)
    else:
        private_logs = []
        
    private_logs.insert(0, parsed_data["private"]) # Add to top
    with open(private_file, "w") as f:
        json.dump(private_logs, f, indent=2)
    print("✅ Secure Admin Database updated (Includes Student ID).")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest raw text reports into the UniGuard JSON Database")
    parser.add_argument("file", help="Path to raw text or log file")
    
    args = parser.parse_args()
    file_path = pathlib.Path(args.file)
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    with open(file_path, "r") as f:
        content = f.read()
        
    print(f"--- Processing {file_path.name} ---")
    extracted = process_raw_report(content)
    append_to_logs(extracted)
    print(">> Pipeline Complete. UniGuard Chatbot is now aware of new data.")
