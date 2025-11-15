# AWS Elastic Beanstalk Deployment Guide
## Campus Resource Hub

This guide will walk you through deploying the Campus Resource Hub Flask application to AWS Elastic Beanstalk.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Setup](#pre-deployment-setup)
3. [Initial Deployment](#initial-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Updating Your Application](#updating-your-application)
7. [Troubleshooting](#troubleshooting)
8. [Cost Considerations](#cost-considerations)

---

## Prerequisites

### 1. AWS Account Setup
- Create an AWS account at https://aws.amazon.com
- Set up billing alerts to monitor costs
- Create an IAM user with appropriate permissions:
  - AWSElasticBeanstalkFullAccess
  - AmazonS3FullAccess
  - AmazonEC2FullAccess

### 2. Install AWS EB CLI
```bash
# macOS (using Homebrew)
brew install awsebcli

# Windows (using pip)
pip install awsebcli

# Linux (using pip)
pip install awsebcli --upgrade --user

# Verify installation
eb --version
```

### 3. Configure AWS Credentials
```bash
# Configure AWS credentials
aws configure

# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

---

## Pre-Deployment Setup

### 1. Review Configuration Files

Ensure these files exist in your project:

- `application.py` - WSGI entry point
- `.ebextensions/01_flask.config` - Flask configuration
- `.ebextensions/02_python.config` - Python settings
- `.ebextensions/03_db_init.config` - Database initialization
- `init_production_db.py` - Production database script
- `requirements.txt` - Python dependencies
- `schema.sql` - Database schema

### 2. Create .ebignore (Optional)

Create a `.ebignore` file to exclude unnecessary files from deployment:

```bash
# Create .ebignore
cat > .ebignore << 'EOF'
.git/
.gitignore
__pycache__/
*.pyc
*.pyo
*.db
*.sqlite
*.sqlite3
venv/
env/
.vscode/
.idea/
*.log
test_*.py
tests/
.pytest_cache/
.coverage
htmlcov/
EOF
```

### 3. Test Locally with Gunicorn

Before deploying, test that your app works with Gunicorn:

```bash
# Install dependencies
pip install -r requirements.txt

# Test with Gunicorn
gunicorn -b 127.0.0.1:8000 application:application

# Visit http://localhost:8000 to verify
```

---

## Initial Deployment

### Step 1: Initialize Elastic Beanstalk Application

```bash
# Navigate to your project directory
cd "/Users/hii/Desktop/AiDD Final Project/Final_Project"

# Initialize EB application
eb init

# Follow the prompts:
# 1. Select region (e.g., us-east-1)
# 2. Enter application name: campus-resource-hub
# 3. Select Python platform
# 4. Select Python 3.11 (or latest compatible version)
# 5. Do you want to set up SSH? Yes (recommended)
# 6. Select or create a keypair
```

### Step 2: Create Environment

```bash
# Create production environment
eb create campus-resource-hub-prod

# This will:
# - Create EC2 instances
# - Set up load balancer
# - Configure security groups
# - Deploy your application
# - Run database initialization

# Wait 5-10 minutes for environment creation
```

### Step 3: Set Environment Variables

```bash
# Set SECRET_KEY (CRITICAL - generate a secure key)
eb setenv SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# Set Flask environment
eb setenv FLASK_ENV=production

# Enable secure cookies
eb setenv SESSION_COOKIE_SECURE=true

# Optional: Email configuration (if using notifications)
eb setenv MAIL_SERVER=smtp.gmail.com
eb setenv MAIL_PORT=587
eb setenv MAIL_USE_TLS=true
eb setenv MAIL_USERNAME=your-email@gmail.com
eb setenv MAIL_PASSWORD=your-app-password
eb setenv MAIL_DEFAULT_SENDER=noreply@campusresourcehub.edu

# Optional: AI features (if using)
# eb setenv OPENAI_API_KEY=your-openai-key
# eb setenv ANTHROPIC_API_KEY=your-anthropic-key

# Optional: Google Calendar integration
# eb setenv GOOGLE_CLIENT_ID=your-client-id
# eb setenv GOOGLE_CLIENT_SECRET=your-client-secret
```

---

## Environment Configuration

### Configure Environment Settings via AWS Console

1. Log into AWS Console: https://console.aws.amazon.com
2. Navigate to Elastic Beanstalk
3. Select your application: `campus-resource-hub`
4. Select environment: `campus-resource-hub-prod`
5. Click "Configuration"

### Recommended Configuration Changes:

#### 1. Instances
- **Instance type**: t3.micro (Free tier eligible) or t3.small
- **EC2 security groups**: Ensure HTTP (80) and HTTPS (443) are open

#### 2. Capacity
- **Environment type**: Load balanced (for production) or Single instance (for testing)
- **Min instances**: 1
- **Max instances**: 4 (adjust based on expected traffic)

#### 3. Load Balancer (if using load balanced environment)
- **Type**: Application Load Balancer
- **Health check path**: `/` or `/health` (if you create a health endpoint)

#### 4. Rolling Updates and Deployments
- **Deployment policy**: Rolling
- **Batch size**: 50%

#### 5. Security
- **SSL Certificate**: Add SSL certificate for HTTPS (recommended)
- Go to Configuration → Load Balancer → Add listener (port 443)

---

## Post-Deployment Verification

### 1. Check Environment Health

```bash
# Check environment status
eb status

# View recent logs
eb logs

# Open application in browser
eb open
```

### 2. Verify Database Initialization

```bash
# SSH into the instance
eb ssh

# Check if database exists
ls -l campus_resource_hub.db

# Check database tables
sqlite3 campus_resource_hub.db ".tables"

# Exit SSH
exit
```

### 3. Test Application Features

Visit your application URL and test:
- [ ] Home page loads
- [ ] User registration works
- [ ] Login/logout works
- [ ] Browse resources page loads
- [ ] Create resource (if logged in)
- [ ] Search functionality
- [ ] Static files (images, CSS, JS) load correctly

### 4. Monitor Application

```bash
# Monitor real-time logs
eb logs --stream

# Check CloudWatch metrics via AWS Console
# - Request count
# - Response time
# - Error rate
# - CPU utilization
```

---

## Updating Your Application

### Deploy Code Changes

```bash
# Make your code changes locally
# Test changes locally

# Commit changes to git (EB deploys from git)
git add .
git commit -m "Your commit message"

# Deploy to Elastic Beanstalk
eb deploy

# Monitor deployment
eb status
```

### Update Environment Variables

```bash
# Update single variable
eb setenv VARIABLE_NAME=new-value

# Update multiple variables
eb setenv VAR1=value1 VAR2=value2 VAR3=value3

# Restart environment (if needed)
eb restart
```

### Update Configuration

```bash
# Modify .ebextensions/*.config files
# Commit changes
# Deploy
eb deploy
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Returns 502 Bad Gateway

**Possible causes:**
- Application failed to start
- Gunicorn configuration error
- Import errors

**Solution:**
```bash
# Check recent logs
eb logs --all

# Look for Python errors in:
# - /var/log/eb-engine.log
# - /var/log/web.stdout.log

# Common fix: Verify application.py imports correctly
eb ssh
cd /var/app/current
python3 -c "from application import application"
exit
```

#### 2. Static Files Not Loading

**Solution:**
- Verify `01_flask.config` has correct static file mapping
- Check that `src/static` directory exists
- Clear browser cache and retry

#### 3. Database Not Initialized

**Solution:**
```bash
eb ssh
cd /var/app/current
python3 init_production_db.py
exit
eb restart
```

#### 4. Environment Variables Not Set

**Solution:**
```bash
# List current environment variables
eb printenv

# Set missing variables
eb setenv SECRET_KEY=your-secret-key

# Restart to apply
eb restart
```

#### 5. Python Version Mismatch

**Solution:**
- Check `.python-version` file or `.ebextensions` config
- Ensure Python version matches your local development
- EB supports Python 3.11, 3.9, 3.8

#### 6. Timeout During Deployment

**Solution:**
```bash
# Increase deployment timeout in .ebextensions/02_python.config
# Already set to 300 seconds (5 minutes)

# If still timing out, check application startup time
eb logs
```

### Getting More Help

```bash
# View detailed health information
eb health --refresh

# Download all logs for analysis
eb logs --all --zip

# Check environment events
eb events --follow
```

---

## Cost Considerations

### Estimated Monthly Costs (as of 2025)

**Single Instance (t3.micro - Free Tier Eligible):**
- EC2 Instance: $0 - $10/month (free tier: 750 hours/month)
- Elastic Load Balancer: $0 (single instance doesn't need ELB)
- Data Transfer: $0 - $5/month (free tier: 1 GB outbound)
- **Total: ~$0-$15/month**

**Load Balanced (Production):**
- EC2 Instances (2x t3.small): ~$30/month
- Application Load Balancer: ~$16/month
- Data Transfer: $5-$20/month
- **Total: ~$51-$66/month**

### Cost Optimization Tips

1. **Use t3.micro for development/testing** (free tier eligible)
2. **Enable auto-scaling** to scale down during low traffic
3. **Set up billing alerts** in AWS Console
4. **Use single instance** for low-traffic applications
5. **Consider RDS for database** only if you need PostgreSQL/MySQL
6. **Delete unused environments** to avoid charges

### Clean Up Resources

```bash
# Terminate environment when done testing
eb terminate campus-resource-hub-prod

# Delete application
eb terminate --all
```

---

## Production Checklist

Before going live, ensure:

- [ ] SECRET_KEY is set to a secure random value (not dev-secret-key)
- [ ] SESSION_COOKIE_SECURE is set to true
- [ ] FLASK_ENV is set to production
- [ ] Debug mode is disabled
- [ ] Database is initialized with schema
- [ ] SSL certificate is configured for HTTPS
- [ ] Email settings are configured (if using notifications)
- [ ] Error monitoring is set up (CloudWatch)
- [ ] Backup strategy is in place for database
- [ ] Rate limiting is enabled
- [ ] All security headers are configured
- [ ] Application has been load tested
- [ ] Logging is configured appropriately
- [ ] Cost alerts are set up in AWS

---

## Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Documentation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## Support

For issues specific to this application, refer to:
- `PROJECT_DOCUMENTATION.md` - Application overview
- `IMPLEMENTATION_ARCHITECTURE.md` - Technical architecture
- `TESTING_GUIDE.md` - Testing procedures

For AWS-specific issues:
- AWS Support (if you have a support plan)
- AWS Developer Forums
- Stack Overflow (tag: amazon-elastic-beanstalk)
