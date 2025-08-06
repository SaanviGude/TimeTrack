# TimeTrack ACE Project - Team Member Setup Guide

## 🚀 Quick Start for New Team Members

### 1. Clone the Repository
```bash
git clone https://github.com/SaanviGude/TimeTrack.git
cd TimeTrack
git checkout ACE-AI-chatbot
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with these variables:
```
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/timetrackdb
SECRET_KEY=your-secret-key-here-change-in-production
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

```bash
# Create database tables
python create_tables.py

# Add sample data for testing
python add_sample_data.py

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create .env.local file with:
```
```env
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

```bash
# Start frontend server
npm run dev
```

### 4. Database Setup (PostgreSQL)
1. Install PostgreSQL on your machine
2. Create database: `timetrackdb`
3. Update connection details in backend/.env

### 5. API Keys Required
- **Gemini API**: Get from Google AI Studio
- **OpenAI API**: Get from OpenAI platform (optional backup)

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **Backend**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 🎯 Project Structure
```
TimeTrack/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routes/    # API endpoints
│   │   ├── models/    # Database models
│   │   └── main.py    # FastAPI app
│   └── requirements.txt
├── frontend/          # Next.js frontend
│   ├── src/app/       # App directory
│   └── package.json
└── README.md
```

## 🤖 ACE Chatbot Features
- ✅ AI-powered productivity insights
- ✅ Real-time time tracking analysis
- ✅ Project-based analytics
- ✅ Natural language queries
- ✅ Database-driven responses

## 🛠️ Development Tips
1. Always work on the `ACE-AI-chatbot` branch
2. Backend runs on port 8000, frontend on 3000
3. Sample data includes 15 time entries across 3 projects
4. AI responses use Gemini API with fallback to demo data

## 🐛 Common Issues
- **Database connection**: Check PostgreSQL is running
- **API keys**: Ensure both .env files have valid keys
- **Port conflicts**: Make sure ports 3000 and 8000 are free
- **Dependencies**: Run `pip install -r requirements.txt` and `npm install`

## 📞 Need Help?
Contact the team lead for:
- API keys
- Database access
- GitHub repository permissions
- Setup troubleshooting
