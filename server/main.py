import os
import json
import pathlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Pathing
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR.parent / "data" / "logs"

load_dotenv(BASE_DIR / ".env")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class ChatRequest(BaseModel):
    message: str
    role: str = "student" # Default role

class IngestRequest(BaseModel):
    text_content: str

def get_logs(role: str):
    """
    Robustly scans DATA_DIR/logs for JSON files.
    - Student: Returns 'public_status.json' and any file with 'public' in name.
    - Admin: Returns ALL logs including private health and lab data.
    """
    logs = []
    # Search all subdirectories in DATA_DIR
    for path in DATA_DIR.rglob("*.json"):
        # Privacy filter
        if role == "student":
            if "private" in path.name or "health" in str(path):
                continue
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    logs.extend(data)
                else:
                    logs.append(data)
        except Exception as e:
            print(f"Error reading log at {path}: {e}")
            
    return logs

@app.post("/chat")
async def chat(request: ChatRequest):
    if not api_key:
        return {"response": "Warning: Gemini API Key missing on server."}

    context_logs = get_logs(request.role)
    
    role_instruction = (
        "You are 'UniGuard', a Campus Transparency AI. "
        "Your priority is to prevent panic and debunk rumors using verified logs. "
        "NEVER share student names or IDs with students. Keep data abstract (e.g., '3 cases reported')."
    ) if request.role == "student" else (
        "You are in ADMIN MODE. You have FULL CLEARANCE. "
        "When an administrator asks for names, student IDs, or room numbers, provide them DIRECTLY from the logs. "
        "Do not be vague. This is for medical isolation and emergency protocols."
    )

    prompt = f"""
    {role_instruction}
    
    VERIFIED CONTEXT (CURRENT LOGS):
    {json.dumps(context_logs, indent=2)}
    
    USER QUESTION:
    {request.message}
    
    TASK:
    - If Student: Be reassuring, use abstract data, debunk rumors.
    - If Admin: Be specific, provide IDs/Names if requested, give protocol details.
    - List the specific details (Room, Name, ID) clearly in a list format for Admins.
    """

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        print(f"Error calling Gemini: {str(e)}")
        raise HTTPException(status_code=500, detail="AI response failed.")

@app.post("/ingest")
async def ingest_document(req: IngestRequest):
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key missing.")
    
    prompt = f"""
    You are an AI document processor for a university operations dashboard.
    Read the following RAW TEXT REPORT and extract the information into TWO structured JSON objects.

    RAW TEXT:
    {req.text_content}

    TASK:
    Output pure JSON matching exactly this schema, with no markdown code blocks starting with ```json:
    {{
      "public": {{
        "date": "YYYY-MM-DD",
        "block": "Block name/number",
        "indicator": "Health Alert or Mess Quality or Water",
        "summary": "Brief, summary (no names, no IDs).",
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

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        parsed_data = json.loads(clean_text)
        
        # public
        public_file = DATA_DIR / "public_status.json"
        public_logs = []
        if public_file.exists():
            with open(public_file, "r") as f:
                public_logs = json.load(f)
        public_logs.insert(0, parsed_data["public"])
        with open(public_file, "w") as f:
            json.dump(public_logs, f, indent=2)

        # private
        private_file = DATA_DIR / "health" / "private_admin.json"
        private_logs = []
        if private_file.exists():
            with open(private_file, "r") as f:
                private_logs = json.load(f)
        private_logs.insert(0, parsed_data["private"])
        with open(private_file, "w") as f:
            json.dump(private_logs, f, indent=2)

        return {"status": "success", "message": "Document ingested and knowledge base updated."}
    except Exception as e:
        print(f"Ingest Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse document.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
