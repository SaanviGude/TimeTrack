# backend setup for AI

backend/.env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/timetrackdb
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

then run
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend setup for AI

frontend/.env.local
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

then run
npm install
npm run dev
