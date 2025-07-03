# GitHub Webhook Monitor

A Flask-based application that receives GitHub webhook events and displays them in real-time.

## Features

- Receives GitHub webhook events for Push, Pull Request, and Merge actions
- Stores webhook data in MongoDB
- Real-time UI that polls for updates every 15 seconds
- Clean and responsive web interface
- RESTful API endpoints

## Setup Instructions

### Prerequisites

- Python 3.7+
- MongoDB (local installation or MongoDB Atlas)
- GitHub repository with webhook access

### Installation

1. Clone this repository:

   ```bash
   git clone <your-repo-url>
   cd webhook-repo
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and configure:

   ```
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=github_webhooks
   COLLECTION_NAME=actions
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   ```

5. Start MongoDB service (if running locally)

6. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## GitHub Webhook Configuration

1. Go to your GitHub repository settings
2. Navigate to "Webhooks" section
3. Click "Add webhook"
4. Set the payload URL to: `http://your-domain.com/webhook`
5. Set content type to: `application/json`
6. Select individual events:
   - Push events
   - Pull request events
7. Make sure the webhook is active

## API Endpoints

- `GET /` - Main dashboard UI
- `POST /webhook` - GitHub webhook receiver
- `GET /api/actions` - Get latest actions (JSON)
- `GET /health` - Health check endpoint

## MongoDB Schema

The application stores webhook data with the following structure:

```json
{
  "action": "push|pull_request|merge",
  "author": "username",
  "from_branch": "source-branch",
  "to_branch": "target-branch",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Display Formats

- **Push**: "{author} pushed to {to_branch} on {timestamp}"
- **Pull Request**: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
- **Merge**: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"

## Development

To run in development mode:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## Production Deployment

For production deployment, consider using:

- Gunicorn as WSGI server
- Nginx as reverse proxy
- SSL certificates for HTTPS
- Environment-specific configuration

Example Gunicorn command:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Testing

You can test the webhook endpoint using curl:

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
