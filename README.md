# UniGuard Campus Intelligence System

AI-assisted campus operations dashboard for demoing privacy-aware incident ingestion, role-based access, and conversational search over campus logs.

## What It Does

- Ingests unstructured text reports into separate public and admin-facing JSON logs.
- Processes doctor Excel sheets into structured public summaries and private admin records.
- Offers a role-based chat flow for student and admin users.
- Shows a lightweight admin records view and alert banner in the frontend.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- AI layer: Gemini (`gemini-2.0-flash`)
- Data storage: JSON files for demo purposes

## Resume-Friendly Notes

- All repository data is demo data created for portfolio and exhibition use.
- The project uses a private admin data layer, but it is not an encrypted production database.
- Authentication is demo-only and uses local hardcoded credentials.

## Project Structure

- `client/`: React frontend
- `server/`: FastAPI backend and ingestion scripts
- `data/logs/`: Demo public/admin log data
- `data/daily_excels/`: Drop zone for `.xlsx` files

## Quick Start

### 1. Backend

Create a server env file from the example:

```bash
cd server
Copy-Item .env.example .env
```

Then add your Gemini API key to `server/.env`.

Install dependencies and start the API:

```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

On macOS/Linux, activate the virtual environment with:

```bash
source venv/bin/activate
```

### 2. Frontend

Create a client env file if you want to override the API base URL:

```bash
cd client
Copy-Item .env.example .env
```

Install dependencies and start the UI:

```bash
cd client
npm install
npm run dev
```

## Demo Credentials

- Student: `24mim10001` / `password123`
- Admin: `emp001` / `admin123`

## Demo Workflow

### Text report ingestion

1. Start the backend and frontend.
2. Log in as admin.
3. Use `Upload Text Log` to ingest [sample_raw_report.txt](/C:/Users/DELL/Downloads/uni-rag-chatbot/uni-rag-chatbot-main/server/sample_raw_report.txt).

### Excel ingestion

1. Generate a sample doctor report:

```bash
cd server
python generate_mock_excel.py
```

2. Upload the generated `sample_doctor_report.xlsx` from the admin dashboard.

## API Endpoints

- `POST /auth/login`
- `GET /admin/data`
- `GET /status/alert`
- `POST /chat`
- `POST /ingest`
- `POST /upload/excel`

## Current Limitations

- The project is optimized for local demo use, not production deployment.
- JSON files are used instead of a database.
- Admin authentication is mock authentication for demo flow only.
- Gemini output is parsed directly and may need extra validation for production.
