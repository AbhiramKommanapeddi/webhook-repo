# API Documentation

## Overview

The GitHub Webhook Monitor provides RESTful API endpoints for receiving GitHub webhook events and retrieving action data.

## Base URL

- Development: `http://localhost:5000`
- Production: `https://your-domain.com`

## Authentication

Currently, the API does not require authentication. For production use, consider implementing:

- API key authentication
- GitHub webhook signature validation
- Rate limiting

## Endpoints

### 1. Main Dashboard

**GET /**

Returns the main HTML dashboard interface.

**Response:**

- Content-Type: `text/html`
- Status: `200 OK`

**Example:**

```http
GET / HTTP/1.1
Host: localhost:5000
```

### 2. Webhook Receiver

**POST /webhook**

Receives GitHub webhook events and processes them.

**Request Headers:**

- Content-Type: `application/json`
- X-GitHub-Event: `push|pull_request` (GitHub specific)
- X-GitHub-Delivery: `<unique-id>` (GitHub specific)

**Request Body:**
GitHub webhook payload (varies by event type)

**Response:**

```json
{
  "status": "success|ignored|error",
  "message": "Description of the result"
}
```

**Status Codes:**

- `200 OK`: Event processed successfully
- `400 Bad Request`: Invalid payload
- `500 Internal Server Error`: Server error

**Examples:**

Push Event:

```http
POST /webhook HTTP/1.1
Content-Type: application/json

{
  "pusher": {"name": "john_doe"},
  "ref": "refs/heads/main",
  "commits": [{"message": "Fix bug in user authentication"}]
}
```

Pull Request Event:

```http
POST /webhook HTTP/1.1
Content-Type: application/json

{
  "action": "opened",
  "pull_request": {
    "user": {"login": "jane_smith"},
    "head": {"ref": "feature/new-dashboard"},
    "base": {"ref": "main"}
  }
}
```

### 3. Get Actions

**GET /api/actions**

Retrieves the latest GitHub actions from the database.

**Query Parameters:**

- `limit` (optional): Number of actions to return (default: 20, max: 100)
- `action` (optional): Filter by action type (`push`, `pull_request`, `merge`)
- `author` (optional): Filter by author name

**Response:**

```json
{
  "actions": [
    {
      "action": "push",
      "author": "john_doe",
      "from_branch": null,
      "to_branch": "main",
      "timestamp": "2024-01-01T12:00:00.000Z"
    },
    {
      "action": "pull_request",
      "author": "jane_smith",
      "from_branch": "feature/new-dashboard",
      "to_branch": "main",
      "timestamp": "2024-01-01T11:30:00.000Z"
    }
  ]
}
```

**Status Codes:**

- `200 OK`: Success
- `500 Internal Server Error`: Database error

**Examples:**

Get all actions:

```http
GET /api/actions HTTP/1.1
Host: localhost:5000
```

Get only push actions:

```http
GET /api/actions?action=push HTTP/1.1
Host: localhost:5000
```

Get actions by specific author:

```http
GET /api/actions?author=john_doe HTTP/1.1
Host: localhost:5000
```

### 4. Health Check

**GET /health**

Returns the health status of the application.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

**Status Codes:**

- `200 OK`: Application is healthy
- `503 Service Unavailable`: Application is unhealthy

**Example:**

```http
GET /health HTTP/1.1
Host: localhost:5000
```

## Data Models

### Action Object

```json
{
  "action": "push|pull_request|merge",
  "author": "string",
  "from_branch": "string|null",
  "to_branch": "string",
  "timestamp": "ISO 8601 datetime string"
}
```

**Field Descriptions:**

- `action`: Type of GitHub action
- `author`: GitHub username who performed the action
- `from_branch`: Source branch (null for push events)
- `to_branch`: Target branch
- `timestamp`: UTC timestamp when the action occurred

### GitHub Webhook Payload Examples

#### Push Event Payload

```json
{
  "ref": "refs/heads/main",
  "before": "previous-commit-sha",
  "after": "new-commit-sha",
  "pusher": {
    "name": "john_doe",
    "email": "john@example.com"
  },
  "commits": [
    {
      "id": "commit-sha",
      "message": "Commit message",
      "timestamp": "2024-01-01T12:00:00Z",
      "author": {
        "name": "John Doe",
        "email": "john@example.com"
      }
    }
  ]
}
```

#### Pull Request Event Payload

```json
{
  "action": "opened|synchronize|closed",
  "pull_request": {
    "id": 123,
    "state": "open|closed",
    "merged": false,
    "merged_by": null,
    "user": {
      "login": "jane_smith",
      "id": 456
    },
    "head": {
      "ref": "feature/new-feature",
      "sha": "commit-sha"
    },
    "base": {
      "ref": "main",
      "sha": "commit-sha"
    }
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Common Error Codes

- `INVALID_PAYLOAD`: Webhook payload is malformed
- `DATABASE_ERROR`: Database operation failed
- `PROCESSING_ERROR`: Error processing webhook data

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider:

- Implementing rate limiting per IP address
- Setting up request quotas
- Using Redis for distributed rate limiting

## Security Considerations

### Webhook Signature Validation

GitHub signs webhook payloads with a secret key. To validate:

1. Configure webhook secret in GitHub
2. Verify signature in webhook endpoint:

```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, f'sha256={expected}')
```

### HTTPS in Production

Always use HTTPS in production to protect webhook payloads:

- Use SSL certificates
- Enable HSTS headers
- Validate certificate chains

## Usage Examples

### JavaScript (Fetch API)

```javascript
// Get latest actions
fetch("/api/actions")
  .then((response) => response.json())
  .then((data) => console.log(data.actions));

// Poll for updates every 15 seconds
setInterval(() => {
  fetch("/api/actions")
    .then((response) => response.json())
    .then((data) => updateUI(data.actions));
}, 15000);
```

### Python (Requests)

```python
import requests

# Get actions
response = requests.get('http://localhost:5000/api/actions')
actions = response.json()['actions']

# Send test webhook
payload = {
    "pusher": {"name": "test_user"},
    "ref": "refs/heads/main"
}
response = requests.post('http://localhost:5000/webhook', json=payload)
print(response.json())
```

### cURL

```bash
# Get actions
curl http://localhost:5000/api/actions

# Send test webhook
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"pusher":{"name":"test_user"},"ref":"refs/heads/main"}'

# Health check
curl http://localhost:5000/health
```

## Monitoring and Observability

### Metrics to Monitor

- Request count and rate
- Response times
- Error rates
- Database query performance
- Memory and CPU usage

### Logging

The application logs important events:

- Webhook events received
- Database operations
- Errors and exceptions

### Health Check Integration

The `/health` endpoint can be used with:

- Load balancers
- Monitoring systems (Prometheus, Datadog)
- Container orchestration platforms

## Development and Testing

### Local Development

```bash
# Start application
python app.py

# Test webhook endpoint
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Testing with ngrok

For testing with real GitHub webhooks:

```bash
# Install ngrok
# Start your application
python app.py

# In another terminal, expose local server
ngrok http 5000

# Use the ngrok URL in GitHub webhook configuration
```

## Changelog

### Version 1.0.0

- Initial API implementation
- Basic webhook processing
- MongoDB storage
- Real-time UI updates

### Future Enhancements

- Authentication and authorization
- Rate limiting
- Webhook signature validation
- Advanced filtering and search
- Real-time WebSocket updates
- Batch operations
- Export functionality
