\# HCP CRM - AI-First Interaction Logger



An AI-powered CRM system for Healthcare Professionals.



\## Tech Stack

\- Frontend: React.js + Redux + Google Inter Font

\- Backend: Python + FastAPI

\- AI Agent: LangGraph

\- LLM: Groq API (llama-3.3-70b-versatile)

\- Database: PostgreSQL



\## LangGraph Tools

1\. log\_interaction - Logs new HCP interaction using LLM entity extraction

2\. edit\_interaction - Edits existing interaction by ID

3\. get\_interaction\_history - Retrieves all past interactions with an HCP

4\. suggest\_followup\_actions - Suggests intelligent follow-up actions

5\. analyze\_sentiment\_trend - Analyzes sentiment trend across interactions



\## Backend Setup

cd backend

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000



\## Frontend Setup

cd frontend

npm install

npm start



\## Usage

1\. Open http://localhost:3001

2\. Fill the form on left to log an interaction

3\. Or use AI chat on right

4\. AI automatically extracts and fills the form

5\. Click Log Interaction to save to database

