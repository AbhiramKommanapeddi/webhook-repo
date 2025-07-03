# GitHub Webhook Monitor - Testing Guide

This guide covers testing strategies and procedures for the GitHub Webhook Monitor application.

## Testing Setup

### Prerequisites

- Python 3.7+
- MongoDB (local or test instance)
- GitHub repository for testing webhooks

### Install Test Dependencies

```bash
pip install pytest pytest-cov requests-mock
```

### Test Environment Setup

Create a `.env.test` file:

```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=github_webhooks_test
COLLECTION_NAME=actions_test
SECRET_KEY=test-secret-key
FLASK_ENV=testing
```

## Unit Tests

### Test Structure

```
tests/
├── __init__.py
├── test_app.py
├── test_webhook_processing.py
├── test_database.py
└── conftest.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app.py

# Run tests with verbose output
pytest -v
```

## Integration Tests

### Testing Webhook Endpoints

#### Test Push Event

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "pusher": {"name": "testuser"},
    "ref": "refs/heads/main",
    "commits": [{"message": "Test commit"}]
  }'
```

#### Test Pull Request Event

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "opened",
    "pull_request": {
      "user": {"login": "testuser"},
      "head": {"ref": "feature-branch"},
      "base": {"ref": "main"}
    }
  }'
```

#### Test Merge Event

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "closed",
    "pull_request": {
      "merged": true,
      "merged_by": {"login": "testuser"},
      "user": {"login": "testuser"},
      "head": {"ref": "feature-branch"},
      "base": {"ref": "main"}
    }
  }'
```

### Testing API Endpoints

#### Get Actions API

```bash
curl http://localhost:5000/api/actions
```

#### Health Check

```bash
curl http://localhost:5000/health
```

## Load Testing

### Using Apache Bench (ab)

```bash
# Test webhook endpoint
ab -n 1000 -c 10 -p webhook_payload.json -T application/json http://localhost:5000/webhook

# Test API endpoint
ab -n 1000 -c 10 http://localhost:5000/api/actions
```

### Using Python locust

```python
# locustfile.py
from locust import HttpUser, task, between

class WebhookUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_webhook(self):
        payload = {
            "pusher": {"name": "testuser"},
            "ref": "refs/heads/main"
        }
        self.client.post("/webhook", json=payload)

    @task
    def test_api(self):
        self.client.get("/api/actions")
```

Run with: `locust -f locustfile.py --host=http://localhost:5000`

## End-to-End Testing

### GitHub Integration Test

1. Create a test repository
2. Configure webhook pointing to your test instance
3. Perform actual GitHub actions:
   - Push commits
   - Create pull requests
   - Merge pull requests
4. Verify events appear in the UI

### UI Testing

1. Open browser to `http://localhost:5000`
2. Verify page loads correctly
3. Check that events display properly
4. Test auto-refresh functionality
5. Verify responsive design on mobile

## Database Testing

### MongoDB Test Setup

```python
import pymongo
from pymongo import MongoClient

# Connect to test database
client = MongoClient('mongodb://localhost:27017/')
test_db = client['github_webhooks_test']
test_collection = test_db['actions_test']

# Insert test data
test_data = {
    'action': 'push',
    'author': 'testuser',
    'to_branch': 'main',
    'timestamp': datetime.utcnow()
}
test_collection.insert_one(test_data)

# Query test data
results = list(test_collection.find().sort('timestamp', -1))
```

### Test Data Cleanup

```python
# Clear test collection
test_collection.drop()

# Or delete specific test data
test_collection.delete_many({'author': 'testuser'})
```

## Performance Testing

### Response Time Testing

```python
import time
import requests

def test_response_time():
    start_time = time.time()
    response = requests.get('http://localhost:5000/api/actions')
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should respond in under 1 second
```

### Memory Usage Testing

```python
import psutil
import os

def test_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    # Check memory usage is reasonable
    assert memory_info.rss < 100 * 1024 * 1024  # Less than 100MB
```

## Security Testing

### Input Validation Testing

```python
def test_malicious_input():
    malicious_payloads = [
        {'malicious': '<script>alert("xss")</script>'},
        {'sql_injection': "'; DROP TABLE actions; --"},
        {'large_payload': 'x' * 1000000}  # 1MB payload
    ]

    for payload in malicious_payloads:
        response = requests.post('http://localhost:5000/webhook', json=payload)
        # Should not cause server error
        assert response.status_code != 500
```

### Authentication Testing

```python
def test_webhook_without_auth():
    response = requests.post('http://localhost:5000/webhook')
    # Should handle missing content type gracefully
    assert response.status_code in [400, 401]
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:5.0
        ports:
          - 27017:27017

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Test Data Management

### Sample Test Data

```json
{
  "push_event": {
    "pusher": { "name": "testuser" },
    "ref": "refs/heads/main",
    "commits": [{ "message": "Test commit" }]
  },
  "pr_event": {
    "action": "opened",
    "pull_request": {
      "user": { "login": "testuser" },
      "head": { "ref": "feature" },
      "base": { "ref": "main" }
    }
  },
  "merge_event": {
    "action": "closed",
    "pull_request": {
      "merged": true,
      "merged_by": { "login": "testuser" },
      "user": { "login": "testuser" },
      "head": { "ref": "feature" },
      "base": { "ref": "main" }
    }
  }
}
```

### Test Data Generator

```python
import random
from datetime import datetime, timedelta

def generate_test_data(count=100):
    actions = ['push', 'pull_request', 'merge']
    authors = ['alice', 'bob', 'charlie', 'diana']
    branches = ['main', 'develop', 'feature/xyz', 'hotfix/abc']

    test_data = []
    for _ in range(count):
        data = {
            'action': random.choice(actions),
            'author': random.choice(authors),
            'from_branch': random.choice(branches),
            'to_branch': random.choice(branches),
            'timestamp': datetime.utcnow() - timedelta(
                minutes=random.randint(0, 1440)
            )
        }
        test_data.append(data)

    return test_data
```

## Troubleshooting Test Issues

### Common Test Failures

1. **MongoDB Connection**: Ensure MongoDB is running
2. **Port Conflicts**: Check if port 5000 is available
3. **Environment Variables**: Verify test environment configuration
4. **Network Issues**: Check firewall settings for local testing

### Debug Mode Testing

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run app in debug mode
app.run(debug=True)
```

### Test Isolation

```python
# Use separate test database
@pytest.fixture(scope='function')
def test_database():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['test_db']
    yield db
    client.drop_database('test_db')
```

## Best Practices

1. **Test Independence**: Each test should be independent
2. **Data Cleanup**: Clean up test data after each test
3. **Mocking**: Use mocks for external dependencies
4. **Coverage**: Aim for >90% code coverage
5. **Documentation**: Document complex test scenarios
6. **Automation**: Run tests automatically on CI/CD

## Test Reporting

### Coverage Report

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Results

```bash
pytest --junitxml=test-results.xml
# Import to CI/CD system
```

This comprehensive testing approach ensures the reliability and robustness of the GitHub Webhook Monitor application.
