@echo off
REM GitHub Webhook Monitor - Development Setup Script for Windows

echo 🚀 GitHub Webhook Monitor Setup
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if MongoDB is available
mongod --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  MongoDB is not installed locally
    echo    You can either:
    echo    1. Install MongoDB locally
    echo    2. Use MongoDB Atlas (cloud)
    echo    3. Use Docker: docker run -d -p 27017:27017 mongo:5.0
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔨 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️  Creating .env configuration file...
    (
        echo MONGODB_URI=mongodb://localhost:27017/
        echo DATABASE_NAME=github_webhooks
        echo COLLECTION_NAME=actions
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=dev-secret-key-change-in-production
    ) > .env
    echo ✅ Created .env file - please review and update as needed
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Review the .env file and update configuration
echo 2. Start MongoDB service if not already running
echo 3. Run the application: python app.py
echo 4. Open http://localhost:5000 in your browser
echo 5. Configure GitHub webhooks to point to your endpoint
echo.
echo For production deployment, see DEPLOYMENT.md
echo For testing instructions, see TESTING.md
echo.
pause
