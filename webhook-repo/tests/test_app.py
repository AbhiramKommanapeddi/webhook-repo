import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, extract_webhook_data

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_mongo_collection():
    """Mock MongoDB collection for testing."""
    with patch('app.collection') as mock_collection:
        yield mock_collection

class TestWebhookProcessing:
    """Test webhook data processing functionality."""
    
    def test_extract_push_event_data(self):
        """Test extracting data from push webhook payload."""
        payload = {
            "pusher": {"name": "testuser"},
            "ref": "refs/heads/main",
            "commits": [{"message": "Test commit"}]
        }
        
        result = extract_webhook_data(payload)
        
        assert result is not None
        assert result['action'] == 'push'
        assert result['author'] == 'testuser'
        assert result['to_branch'] == 'main'
        assert result['from_branch'] is None
        assert result['timestamp'] is not None
    
    def test_extract_pull_request_event_data(self):
        """Test extracting data from pull request webhook payload."""
        payload = {
            "action": "opened",
            "pull_request": {
                "user": {"login": "testuser"},
                "head": {"ref": "feature-branch"},
                "base": {"ref": "main"}
            }
        }
        
        result = extract_webhook_data(payload)
        
        assert result is not None
        assert result['action'] == 'pull_request'
        assert result['author'] == 'testuser'
        assert result['from_branch'] == 'feature-branch'
        assert result['to_branch'] == 'main'
        assert result['timestamp'] is not None
    
    def test_extract_merge_event_data(self):
        """Test extracting data from merge webhook payload."""
        payload = {
            "action": "closed",
            "pull_request": {
                "merged": True,
                "merged_by": {"login": "merger"},
                "user": {"login": "testuser"},
                "head": {"ref": "feature-branch"},
                "base": {"ref": "main"}
            }
        }
        
        result = extract_webhook_data(payload)
        
        assert result is not None
        assert result['action'] == 'merge'
        assert result['author'] == 'merger'
        assert result['from_branch'] == 'feature-branch'
        assert result['to_branch'] == 'main'
        assert result['timestamp'] is not None
    
    def test_extract_invalid_payload(self):
        """Test handling of invalid webhook payload."""
        payload = {"invalid": "data"}
        
        result = extract_webhook_data(payload)
        
        assert result is None or result['action'] is None

class TestWebhookEndpoint:
    """Test webhook endpoint functionality."""
    
    def test_webhook_endpoint_with_valid_push_data(self, client, mock_mongo_collection):
        """Test webhook endpoint with valid push data."""
        payload = {
            "pusher": {"name": "testuser"},
            "ref": "refs/heads/main",
            "commits": [{"message": "Test commit"}]
        }
        
        response = client.post('/webhook', json=payload)
        
        assert response.status_code == 200
        assert response.json['status'] == 'success'
        mock_mongo_collection.insert_one.assert_called_once()
    
    def test_webhook_endpoint_with_no_payload(self, client):
        """Test webhook endpoint with no payload."""
        response = client.post('/webhook')
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_webhook_endpoint_with_irrelevant_data(self, client, mock_mongo_collection):
        """Test webhook endpoint with irrelevant data."""
        payload = {"irrelevant": "data"}
        
        response = client.post('/webhook', json=payload)
        
        assert response.status_code == 200
        assert response.json['status'] == 'ignored'
        mock_mongo_collection.insert_one.assert_not_called()

class TestAPIEndpoints:
    """Test API endpoint functionality."""
    
    def test_index_endpoint(self, client):
        """Test the main index endpoint."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'GitHub Webhook Monitor' in response.data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        assert 'status' in response.json
        assert response.json['status'] == 'healthy'
    
    def test_actions_api_endpoint(self, client, mock_mongo_collection):
        """Test the actions API endpoint."""
        # Mock the MongoDB query result
        mock_mongo_collection.find.return_value.sort.return_value.limit.return_value = [
            {
                'action': 'push',
                'author': 'testuser',
                'to_branch': 'main',
                'timestamp': '2024-01-01T12:00:00Z'
            }
        ]
        
        response = client.get('/api/actions')
        
        assert response.status_code == 200
        assert 'actions' in response.json
        assert len(response.json['actions']) > 0

if __name__ == '__main__':
    pytest.main([__file__])
