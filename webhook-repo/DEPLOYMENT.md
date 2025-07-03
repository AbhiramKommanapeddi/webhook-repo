# Deployment Guide for GitHub Webhook Monitor

This guide covers different deployment options for the webhook receiver application.

## Local Development

### Prerequisites

- Python 3.7+
- MongoDB (local or cloud)
- Git

### Setup Steps

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables in `.env`
6. Run: `python app.py`

## Production Deployment

### Option 1: Heroku Deployment

1. **Prepare for Heroku**

   ```bash
   # Create Procfile
   echo "web: gunicorn app:app" > Procfile

   # Create runtime.txt
   echo "python-3.9.16" > runtime.txt
   ```

2. **Deploy to Heroku**

   ```bash
   heroku create your-webhook-app
   heroku config:set MONGODB_URI=your-mongodb-connection-string
   heroku config:set SECRET_KEY=your-secret-key
   git push heroku main
   ```

3. **Add MongoDB Atlas**
   - Sign up for MongoDB Atlas
   - Create cluster and database
   - Get connection string and add to Heroku config

### Option 2: AWS EC2 Deployment

1. **Launch EC2 Instance**

   - Choose Ubuntu Server 20.04 LTS
   - Configure security groups (open port 80/443)
   - Create and download key pair

2. **Server Setup**

   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-ec2-ip

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv nginx -y

   # Clone repository
   git clone your-repo-url
   cd webhook-repo

   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Configure Nginx**

   ```nginx
   # /etc/nginx/sites-available/webhook-app
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Create systemd service**

   ```ini
   # /etc/systemd/system/webhook-app.service
   [Unit]
   Description=GitHub Webhook Monitor
   After=network.target

   [Service]
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/home/ubuntu/webhook-repo
   ExecStart=/home/ubuntu/webhook-repo/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start services**
   ```bash
   sudo systemctl enable webhook-app
   sudo systemctl start webhook-app
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

### Option 3: Docker Deployment

1. **Create Dockerfile**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 5000

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

2. **Create docker-compose.yml**

   ```yaml
   version: "3.8"

   services:
     webhook-app:
       build: .
       ports:
         - "5000:5000"
       environment:
         - MONGODB_URI=mongodb://mongo:27017/
         - DATABASE_NAME=github_webhooks
         - SECRET_KEY=your-secret-key
       depends_on:
         - mongo

     mongo:
       image: mongo:5.0
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db

   volumes:
     mongodb_data:
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

### Option 4: DigitalOcean App Platform

1. **Create App**

   - Connect GitHub repository
   - Configure environment variables
   - Set build and run commands

2. **Configuration**
   ```yaml
   # .do/app.yaml
   name: github-webhook-monitor
   services:
     - name: web
       source_dir: /
       github:
         repo: your-username/webhook-repo
         branch: main
       run_command: gunicorn app:app
       environment_slug: python
       instance_count: 1
       instance_size_slug: basic-xxs
       env:
         - key: MONGODB_URI
           value: your-mongodb-connection-string
         - key: SECRET_KEY
           value: your-secret-key
   ```

## Environment Variables

Required environment variables for all deployments:

```env
MONGODB_URI=mongodb://localhost:27017/  # MongoDB connection string
DATABASE_NAME=github_webhooks           # Database name
COLLECTION_NAME=actions                 # Collection name
SECRET_KEY=your-secret-key-here         # Flask secret key
FLASK_ENV=production                    # Set to production
```

## SSL/HTTPS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Application Logs

```bash
# View logs
sudo journalctl -u webhook-app -f

# Log rotation
sudo nano /etc/logrotate.d/webhook-app
```

### Health Checks

- Endpoint: `/health`
- Returns: `{"status": "healthy", "timestamp": "..."}`

### Monitoring Tools

- New Relic
- Datadog
- Prometheus + Grafana

## Backup and Recovery

### MongoDB Backup

```bash
# Backup
mongodump --uri="mongodb://localhost:27017/github_webhooks" --out=backup/

# Restore
mongorestore --uri="mongodb://localhost:27017/github_webhooks" backup/github_webhooks/
```

### Application Backup

- Code: Git repository
- Configuration: Environment variables
- Database: Regular MongoDB dumps

## Performance Optimization

### Application Level

- Use connection pooling
- Implement caching
- Add database indexes
- Use async processing for heavy operations

### Database Level

```javascript
// Add indexes to MongoDB
db.actions.createIndex({ timestamp: -1 });
db.actions.createIndex({ action: 1 });
db.actions.createIndex({ author: 1 });
```

### Infrastructure Level

- Use CDN for static assets
- Implement load balancing
- Use Redis for session storage
- Enable gzip compression

## Security Checklist

- [ ] HTTPS enabled
- [ ] Webhook signature validation
- [ ] Rate limiting implemented
- [ ] Input validation
- [ ] Environment variables secured
- [ ] Database authentication
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Access logs monitored

## Troubleshooting Common Issues

### Application Won't Start

- Check Python version compatibility
- Verify all dependencies installed
- Check environment variables
- Review application logs

### Database Connection Issues

- Verify MongoDB is running
- Check connection string
- Verify network connectivity
- Check authentication credentials

### Webhook Not Receiving Events

- Check GitHub webhook configuration
- Verify endpoint URL is accessible
- Check firewall settings
- Review webhook delivery logs in GitHub

### High Memory Usage

- Monitor application metrics
- Check for memory leaks
- Optimize database queries
- Consider horizontal scaling

## Support and Maintenance

### Regular Tasks

- Update dependencies
- Monitor logs
- Check SSL certificate expiry
- Review security settings
- Backup database

### Scaling Considerations

- Horizontal scaling with load balancer
- Database sharding
- Caching layer
- Microservices architecture

For additional support, refer to the main README.md file or create an issue in the repository.
