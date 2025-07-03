#!/bin/bash

# GitHub Webhook Monitor - Development Setup Script

echo "🚀 GitHub Webhook Monitor Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if MongoDB is available
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB is not installed locally"
    echo "   You can either:"
    echo "   1. Install MongoDB locally"
    echo "   2. Use MongoDB Atlas (cloud)"
    echo "   3. Use Docker: docker run -d -p 27017:27017 mongo:5.0"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env configuration file..."
    cat > .env << EOF
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=github_webhooks
COLLECTION_NAME=actions
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
EOF
    echo "✅ Created .env file - please review and update as needed"
fi

# Check if MongoDB is running
if command -v mongod &> /dev/null; then
    if ! pgrep mongod > /dev/null; then
        echo "🔄 Starting MongoDB..."
        mongod --fork --logpath /tmp/mongodb.log --dbpath /tmp/mongodb-data
    else
        echo "✅ MongoDB is already running"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the .env file and update configuration"
echo "2. Run the application: python app.py"
echo "3. Open http://localhost:5000 in your browser"
echo "4. Configure GitHub webhooks to point to your endpoint"
echo ""
echo "For production deployment, see DEPLOYMENT.md"
echo "For testing instructions, see TESTING.md"
