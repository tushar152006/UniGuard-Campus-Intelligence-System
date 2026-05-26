import io
import json
import os
import pathlib
from collections import Counter

import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Pathing
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR.parent / "data" / "logs"
PUBLIC_LOG_FILE = DATA_DIR / "public_status.json"
PRIVATE_LOG_FILE = DATA_DIR / "health" / "private_admin.json"

load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="UniGuard Campus Intelligence API")

# Enable CORS for local demos.
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

DEMO_USERS = {
    "student": {
        "24mim10001": {"password": "password123", "name": "Demo Student"},
    },
    "admin": {
        "emp001": {"password": "admin123", "name": "Demo Admin"},
    },
}


class ChatRequest(BaseModel):
    message: str
    role: str = "student"


class IngestRequest(BaseModel):
    text_content: str


class LoginRequest(BaseModel):
    username: str
    password: str
    role: str


def read_json_records(path: pathlib.Path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data if isinstance(data, list) else [data]


def write_json_records(path: pathlib.Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def get_logs(role: str):
    logs = []

    for path in DATA_DIR.rglob("*.json"):
        if role == "student" and ("private" in path.name or "health" in str(path)):
            continue

        try:
            logs.extend(read_json_records(path))
        except Exception as exc:
            print(f"Error reading log at {path}: {exc}")

    return logs


def ensure_gemini_available():
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key missing. Copy server/.env.example to server/.env and set GEMINI_API_KEY.",
        )


def generate_gemini_json(prompt: str):
    ensure_gemini_available()
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return json.loads(response.text.replace("```json", "").replace("```", "").strip())


def append_public_private_logs(parsed_data):
    public_logs = read_json_records(PUBLIC_LOG_FILE)
    private_logs = read_json_records(PRIVATE_LOG_FILE)

    public_logs.insert(0, parsed_data["public"])
    private_logs.insert(0, parsed_data["private"])

    write_json_records(PUBLIC_LOG_FILE, public_logs)
    write_json_records(PRIVATE_LOG_FILE, private_logs)


def append_excel_logs(parsed_data_array):
    if not isinstance(parsed_data_array, list):
        raise HTTPException(status_code=500, detail="AI output for Excel ingestion was not a list.")

    public_logs = read_json_records(PUBLIC_LOG_FILE)
    private_logs = read_json_records(PRIVATE_LOG_FILE)

    for item in parsed_data_array:
        if "public" in item:
            public_logs.insert(0, item["public"])
        if "private" in item:
            private_logs.insert(0, item["private"])

    write_json_records(PUBLIC_LOG_FILE, public_logs)
    write_json_records(PRIVATE_LOG_FILE, private_logs)


def build_alert_status():
    public_logs = read_json_records(PUBLIC_LOG_FILE)
    indicators = [
        entry.get("indicator", "").strip()
        for entry in public_logs
        if isinstance(entry, dict) and entry.get("indicator")
    ]

    if not indicators:
        return {"outbreak": False, "disease": "", "count": 0}

    indicator, count = Counter(indicators).most_common(1)[0]
    return {
        "outbreak": count >= 2 and indicator.lower() not in {"general health", "mess quality"},
        "disease": indicator,
        "count": count,
    }


def process_excel_bytes(file_bytes: bytes):
    csv_content = pd.read_excel(io.BytesIO(file_bytes)).to_csv(index=False)

    prompt = f"""
    You are an AI document processor for a university operations dashboard.
    Read the following EXCEL SHEET DATA (in CSV format) and extract the information into a structured JSON array of objects.
    Each row in the dataset represents an individual case that should have its own public and private entries.

    DATA (CSV):
    {csv_content}

    TASK:
    Output pure JSON matching exactly this schema (an array of objects), with no markdown code blocks:
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
          "action": "Prescribed medicines and action taken",
          "contact": "Mobile Number"
        }}
      }}
    ]

    If data is missing for a field, put "N/A". Ensure valid JSON structure.
    """

    return generate_gemini_json(prompt)


@app.post("/auth/login")
async def login(request: LoginRequest):
    role = request.role.lower()
    users_for_role = DEMO_USERS.get(role, {})
    account = users_for_role.get(request.username)

    if not account or account["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid demo credentials.")

    return {
        "user": {
            "id": request.username,
            "name": account["name"],
            "role": role,
        }
    }


@app.get("/admin/data")
async def admin_data(role: str = "admin"):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return read_json_records(PRIVATE_LOG_FILE)


@app.get("/status/alert")
async def alert_status():
    return build_alert_status()


@app.post("/chat")
async def chat(request: ChatRequest):
    ensure_gemini_available()
    context_logs = get_logs(request.role)

    role_instruction = (
        "You are 'UniGuard', a Campus Transparency AI. "
        "Your priority is to prevent panic and debunk rumors using verified logs. "
        "Never share student names or IDs with students. Keep data abstract."
    ) if request.role == "student" else (
        "You are in admin mode for a controlled demo environment. "
        "When an administrator asks for names, student IDs, or room numbers, provide them directly from the logs. "
        "Be concise and action-oriented."
    )

    prompt = f"""
    {role_instruction}

    VERIFIED CONTEXT (CURRENT LOGS):
    {json.dumps(context_logs, indent=2)}

    USER QUESTION:
    {request.message}

    TASK:
    - If Student: Be reassuring, use abstract data, debunk rumors.
    - If Admin: Be specific, provide IDs/names if requested, give protocol details.
    - Use short paragraphs or bullet points when that improves clarity.
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as exc:
        print(f"Error calling Gemini: {exc}")
        raise HTTPException(status_code=500, detail="AI response failed.")


@app.post("/ingest")
async def ingest_document(req: IngestRequest):
    prompt = f"""
    You are an AI document processor for a university operations dashboard.
    Read the following raw text report and extract the information into two structured JSON objects.

    RAW TEXT:
    {req.text_content}

    TASK:
    Output pure JSON matching exactly this schema, with no markdown code blocks:
    {{
      "public": {{
        "date": "YYYY-MM-DD",
        "block": "Block name/number",
        "indicator": "Health Alert or Mess Quality or Water",
        "summary": "Brief summary with no names or IDs.",
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
        parsed_data = generate_gemini_json(prompt)
        append_public_private_logs(parsed_data)
        return {"status": "success", "message": "Document ingested and knowledge base updated."}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Ingest Error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to parse document.")


@app.post("/upload/excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    try:
        file_bytes = await file.read()
        parsed_array = process_excel_bytes(file_bytes)
        append_excel_logs(parsed_array)
        return {"status": "success", "message": f"Processed {file.filename}."}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Excel ingest error: {exc}")
        raise HTTPException(status_code=500, detail="Failed to process Excel file.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
