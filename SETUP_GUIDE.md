# TimeTrack ACE Project - Complete Setup Guide

## 🚀 **Step-by-Step Setup Instructions**

### **Phase 1: Install Required Software**

#### **1.1 Install Python 3.11+**
```bash
# Download from: https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
# Verify installation:
python --version
pip --version
```

#### **1.2 Install Node.js 18+**
```bash
# Download LTS from: https://nodejs.org/
# Verify installation:
node --version
npm --version
```

#### **1.3 Install PostgreSQL**
```bash
# Download from: https://www.postgresql.org/download/
# During setup:
# - Set password for postgres user (remember this!)
# - Default port: 5432
# - Remember the installation directory

# Verify installation:
psql --version
```

#### **1.4 Install Git**
```bash
# Download from: https://git-scm.com/download/win
# Use default settings during installation
# Verify:
git --version
```

#### **1.5 Install VS Code (Recommended)**
```bash
# Download from: https://code.visualstudio.com/
# Install these extensions:
# - Python
# - TypeScript and JavaScript Language Features
# - GitLens
# - PostgreSQL (optional)
```

---

### **Phase 2: Clone and Setup Project**

#### **2.1 Clone Repository**
```bash
# Open Command Prompt or PowerShell
git clone https://github.com/SaanviGude/TimeTrack.git
cd TimeTrack
git checkout ACE-AI-chatbot
```

#### **2.2 Setup PostgreSQL Database**
```sql
-- Open pgAdmin or command line psql
-- Connect as postgres user
CREATE DATABASE timetrackdb;
-- Note: Remember this database name!
```

---

### **Phase 3: Backend Setup**

#### **3.1 Navigate to Backend Directory**
```bash
cd backend
```

#### **3.2 Create Python Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Windows Command Prompt:
venv\Scripts\activate
# For Windows PowerShell:
venv\Scripts\Activate.ps1
# For Git Bash:
source venv/Scripts/activate

# You should see (venv) in your prompt
```

#### **3.3 Install Python Dependencies**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

#### **3.4 Create Backend Environment File**
Create a file named `.env` in the `backend` folder with this content:
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/timetrackdb

# Security
SECRET_KEY=your-secret-key-here-change-in-production-environment

# AI API Keys (Get these from team lead)
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

**Important**: Replace `YOUR_PASSWORD` with your PostgreSQL password!

#### **3.5 Initialize Database**
```bash
# Create database tables
python create_tables.py

# Add sample data for testing
python add_sample_data.py
```

---

### **Phase 4: Frontend Setup**

#### **4.1 Navigate to Frontend Directory**
```bash
# Open a new terminal/command prompt
cd TimeTrack/frontend
```

#### **4.2 Install Node Dependencies**
```bash
npm install
```

#### **4.3 Create Frontend Environment File**
Create a file named `.env.local` in the `frontend` folder with this content:
```env
# AI API Keys (same as backend)
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

---

### **Phase 5: Test the Setup**

#### **5.1 Start Backend Server**
```bash
# In backend directory with venv activated
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### **5.2 Start Frontend Server**
```bash
# In a NEW terminal, navigate to frontend
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 15.4.5
- Local:        http://localhost:3000
✓ Ready in 2.4s
```

#### **5.3 Verify Everything Works**
1. **Backend API**: Visit http://127.0.0.1:8000/docs
2. **Frontend**: Visit http://localhost:3000
3. **Test AI Chatbot**: Try asking "How many hours did I work this week?"

---

### **Phase 6: Troubleshooting Common Issues**

#### **6.1 Python Virtual Environment Issues**
```bash
# If activation doesn't work:
# Try different activation methods based on your shell
# PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1

# Command Prompt:
venv\Scripts\activate.bat
```

#### **6.2 Database Connection Issues**
```bash
# Check if PostgreSQL is running:
# Windows: Check Services or Task Manager
# Test connection:
psql -U postgres -d timetrackdb
```

#### **6.3 Port Already in Use**
```bash
# If port 8000 is busy:
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001

# If port 3000 is busy:
npm run dev -- --port 3001
```

#### **6.4 API Key Issues**
- Verify API keys are correct in both `.env` files
- Check for extra spaces or quotes
- Ensure files are named exactly `.env` and `.env.local`

---

### **Phase 7: Development Workflow**

#### **7.1 Daily Startup**
```bash
# Terminal 1 - Backend
cd TimeTrack/backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd TimeTrack/frontend
npm run dev
```

#### **7.2 Making Changes**
```bash
# Always create a new branch for features
git checkout -b feature/your-feature-name
# Make your changes
git add .
git commit -m "Description of changes"
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

---

### **Phase 8: Verification Checklist**

- [ ] All software installed and versions verified
- [ ] Repository cloned successfully
- [ ] PostgreSQL running and database created
- [ ] Backend virtual environment activated
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment files created with API keys
- [ ] Database tables created (create_tables.py)
- [ ] Sample data loaded (add_sample_data.py)
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Can access API docs at http://127.0.0.1:8000/docs
- [ ] Can access frontend at http://localhost:3000
- [ ] AI chatbot responds to test questions
- [ ] No error messages in either terminal

---

### **📞 Need Help?**

**Common Commands Reference:**
```bash
# Activate Python environment
cd backend && venv\Scripts\activate

# Start backend
uvicorn app.main:app --reload

# Start frontend (new terminal)
cd frontend && npm run dev

# Check what's running on ports
netstat -an | findstr "3000\|8000"
```

**If Setup Fails:**
1. Check each step carefully
2. Verify all software versions
3. Ensure environment files have correct API keys
4. Check PostgreSQL is running
5. Contact team lead with specific error messages

**Success Indicators:**
- Both servers start without errors
- Can see API documentation at /docs
- Frontend loads the chatbot interface
- AI responds to questions with actual data insights

Once everything is working, you're ready to start developing! 🎉
