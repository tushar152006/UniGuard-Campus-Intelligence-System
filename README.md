# UniGuard Campus Intelligence System

**An AI-Powered Operations and Crisis Management Dashboard for University Administrators.**

UniGuard is an intelligent campus governance platform that automatically ingests unstructured reports (text logs and doctor's daily Excel sheets), structures them into a privacy-first, two-tier database, and acts as a dynamic conversational AI for both students and administrators.

## Key Features for Exhibition

### 1. Neural Document Ingestion
Instead of manual data entry, UniGuard uses an AI pipeline (`gemini-2.0-flash`) to parse messy, unstructured daily reports (Text files and daily `.xlsx` doctor sheets).
- **Auto-Structuring:** Extracts symptoms, medication, location, and dates from natural language or spreadsheets.
- **Drop-Zone Processing:** A dedicated `data/daily_excels/` folder acts as an automated ingestion workflow. 

### 2. Privacy-First Data Segregation (Two-Tier DB)
When processing documents, the system automatically creates two versions of the data:
- **Public Layer (`public_status.json`)**: Anonymized, abstract summaries designed to prevent panic and debunk rumors (e.g., "A student in Block 3 has an allergy, it is not measles").
- **Private Layer (`private_admin.json`)**: Highly confidential records containing PII (Names, Student IDs, Room numbers, and Medical history) reserved exclusively for Admin staff.

### 3. Role-Based AI Chatbot
The system features a dynamic chat interface with context-aware permissions:
- **Student Mode:** Acts as a Campus Transparency AI. Reassures students, debunks rumors using the Public database, and strictly blocks any leakage of student identities.
- **Admin Mode:** Acts as a Crisis Command Center. Has full clearance across all databases to provide exact room numbers, patient IDs, and protocol actionable intelligence.

---

## System Architecture

- **Frontend (`client/`)**: A modern React application (Vite) featuring a responsive dashboard and chat interface.
- **Backend (`server/`)**: A FastAPI Python server handling document ingestion APIs, file watching, and the Gemini AI conversational logic.
- **Data Layer (`data/`)**: A JSON-based knowledge graph acting as a lightweight, fast, unstructured-to-structured database.

---

## How to Demo This to Your Supervisor

Here is exactly how you should walk your supervisor through the project during the exhibition:

### Step 1: Show the Problem (The Messy Data)
1. Open up the `sample_raw_report.txt` and `sample_doctor_report.xlsx`. 
2. Show them how messy, human-written, and varied the incoming data can be. 
3. *Explain:* "Usually, tracking this across a university requires manual database entry. Our system automates it."

### Step 2: Show the AI Ingestion Pipeline
1. Run the daily batch processor: `python server/process_daily_excels.py`.
2. Open `data/logs/public_status.json` and `data/logs/health/private_admin.json`.
3. *Explain:* "The AI automatically split the doctor's sheet into two. It abstracted the medical symptoms into general 'Health Alerts' for the public, but safely stored the precise Student ID and exact Room Number in the encrypted admin database."

### Step 3: Show the Student Experience (Panic Prevention)
1. On the frontend chat, select the **Student** role.
2. Ask: *"I heard there's an outbreak of measles in Block 3, who got infected?"*
3. *Demonstrate:* Show how the AI calms the user down, confirms it's just an allergy based on the logged data, and strictly **refuses** to give the name or room number of the student.

### Step 4: Show the Admin Experience (Crisis Management)
1. Switch the chat role to **Admin**.
2. Ask: *"Give me the exact room number and student ID of the latest asthma case in Block 4."*
3. *Demonstrate:* Show how the AI now instantly pulls the PII from the private database, allowing administrators to lock down operations or dispatch help immediately.

---

## Tech Stack Setup

### Backend (Server)
Run this in a terminal to start the AI API:
```bash
cd server
source venv/bin/activate
# If requirements aren't installed: pip install fastapi uvicorn google-generativeai pandas openpyxl python-dotenv pydantic python-multipart
uvicorn main:app --reload --port 8001
```

### Frontend (Client)
Run this in a second terminal to start the UI:
```bash
cd client
npm install
npm run dev
```

*Note: Ensure your `.env` file is present in the `/server` directory with your valid `GEMINI_API_KEY`!*
