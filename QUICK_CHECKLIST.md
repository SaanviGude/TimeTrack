# Quick Setup Checklist ✅

## Before Starting (Must Have)
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed  
- [ ] PostgreSQL installed and running
- [ ] Git installed
- [ ] GitHub account created
- [ ] Added as repository collaborator
- [ ] Received API keys from team lead

## Setup Steps (In Order)
- [ ] Clone repository: `git clone https://github.com/SaanviGude/TimeTrack.git`
- [ ] Switch branch: `git checkout ACE-AI-chatbot`
- [ ] Create PostgreSQL database: `timetrackdb`
- [ ] Setup backend virtual environment: `python -m venv venv`
- [ ] Activate virtual environment: `venv\Scripts\activate`
- [ ] Install backend dependencies: `pip install -r requirements.txt`
- [ ] Create `backend/.env` file with database and API keys
- [ ] Initialize database: `python create_tables.py`
- [ ] Add sample data: `python add_sample_data.py`
- [ ] Install frontend dependencies: `npm install`
- [ ] Create `frontend/.env.local` file with API keys
- [ ] Start backend: `uvicorn app.main:app --reload`
- [ ] Start frontend: `npm run dev`

## Verification (Must All Work)
- [ ] Backend running at http://127.0.0.1:8000
- [ ] Frontend running at http://localhost:3000
- [ ] API docs accessible at http://127.0.0.1:8000/docs
- [ ] AI chatbot responds to questions
- [ ] No error messages in terminals
- [ ] Can see "TimeTrack Workspace" and "sainand@updated.com" in UI

## Environment Files Required

### backend/.env
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/timetrackdb
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### frontend/.env.local
```
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

## Success Test
Ask the AI chatbot: **"How many hours did I work this week?"**
Expected response should mention specific data about 37.5 hours, TimeTrack Development project, etc.

## If Something Fails
1. Check PostgreSQL is running
2. Verify API keys are correct
3. Ensure virtual environment is activated
4. Check ports 3000 and 8000 are free
5. Review terminal error messages
6. Contact team lead with specific error details
