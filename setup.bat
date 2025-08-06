@echo off
echo Setting up TimeTrack ACE Project...
echo.

echo 1. Creating backend virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo 2. Installing backend dependencies...
pip install -r requirements.txt

echo 3. Setting up database...
python create_tables.py

echo 4. Adding sample data...
python add_sample_data.py

echo 5. Moving to frontend setup...
cd ..\frontend

echo 6. Installing frontend dependencies...
call npm install

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Create backend\.env file with database and API keys
echo 2. Create frontend\.env.local file with API keys
echo 3. Start backend: cd backend ^&^& uvicorn app.main:app --reload
echo 4. Start frontend: cd frontend ^&^& npm run dev
echo.
echo Access the app at: http://localhost:3000
echo API docs at: http://127.0.0.1:8000/docs
