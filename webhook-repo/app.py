from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'github_webhooks')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'actions')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def extract_webhook_data(payload):
    """Extract relevant data from GitHub webhook payload"""
    try:
        action_type = None
        author = None
        from_branch = None
        to_branch = None
        timestamp = datetime.utcnow()
        
        # Determine action type and extract data
        if 'pusher' in payload:
            # Push event
            action_type = 'push'
            author = payload['pusher']['name']
            to_branch = payload['ref'].split('/')[-1]  # Extract branch name from refs/heads/branch_name
            
        elif 'pull_request' in payload:
            # Pull request event
            pull_request = payload['pull_request']
            action = payload.get('action', '')
            
            if action == 'opened' or action == 'synchronize':
                action_type = 'pull_request'
                author = pull_request['user']['login']
                from_branch = pull_request['head']['ref']
                to_branch = pull_request['base']['ref']
                
            elif action == 'closed' and pull_request.get('merged', False):
                action_type = 'merge'
                author = pull_request['merged_by']['login'] if pull_request['merged_by'] else pull_request['user']['login']
                from_branch = pull_request['head']['ref']
                to_branch = pull_request['base']['ref']
        
        return {
            'action': action_type,
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }
    except Exception as e:
        print(f"Error extracting webhook data: {e}")
        return None

@app.route('/')
def index():
    """Render the main UI"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events"""
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        # Extract relevant data
        webhook_data = extract_webhook_data(payload)
        
        if webhook_data and webhook_data['action']:
            # Store in MongoDB
            collection.insert_one(webhook_data)
            print(f"Stored webhook data: {webhook_data}")
            return jsonify({'status': 'success', 'message': 'Webhook processed successfully'}), 200
        else:
            return jsonify({'status': 'ignored', 'message': 'Event not relevant'}), 200
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/actions')
def get_actions():
    """API endpoint to get latest actions for the UI"""
    try:
        # Get latest 20 actions, sorted by timestamp descending
        actions = list(collection.find(
            {},
            {'_id': 0}  # Exclude MongoDB ObjectId
        ).sort('timestamp', -1).limit(20))
        
        return jsonify({'actions': actions})
    except Exception as e:
        print(f"Error fetching actions: {e}")
        return jsonify({'error': 'Failed to fetch actions'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
