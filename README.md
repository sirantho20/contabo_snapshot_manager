# Contabo Snapshot Manager - Simplified Django + Django-Q

A clean, simplified Django application for managing Contabo VPS snapshots using Django-Q for task scheduling.

## 🚀 Key Features

- **SQLite Database** - No external database required
- **Django-Q Scheduling** - Runs snapshot jobs every 6 hours
- **Clean Docker Setup** - Minimal layers, no supervisor/cron complexity
- **Web Interface** - Monitor tasks via Django admin
- **Timezone Support** - All operations in Asia/Manila timezone
- **Email Notifications** - HTML email summaries after each run

## 📁 Project Structure

```
contabo-snapshot-manager/
├── manage.py                    # Django management
├── lib.py                      # Contabo API logic
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Clean Docker setup
├── startup.sh                  # Simple startup script
├── snapshot_manager/           # Django project
│   └── settings.py            # SQLite + Django-Q config
├── snapshots/                  # Django app
│   ├── tasks.py               # Django-Q tasks
│   └── management/commands/
│       └── run_snapshot_job.py # Management command
└── templates/                  # Email templates
    └── email/
        └── snapshot_summary.html
```

## 🛠️ Setup & Installation

### 1. Verify Setup
```bash
# Verify project structure
python3 verify_setup.py

# Test Django admin configuration
python3 test_admin.py
```

### 2. Build Docker Image
```bash
docker build -t contabo-snapshot-manager .
```

### 3. Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -e CLIENT_ID=your_client_id \
  -e API_USER=your_api_user \
  -e API_PASSWORD=your_api_password \
  -e CLIENT_SECRET=your_client_secret \
  -e ADMIN_EMAIL=your_email@example.com \
  -e EMAIL_FROM=noreply@example.com \
  -e SMTP_SERVER=smtp.gmail.com \
  -e SMTP_PORT=587 \
  -e SMTP_USERNAME=your_smtp_user \
  -e SMTP_PASSWORD=your_smtp_password \
  --name contabo-snapshots \
  contabo-snapshot-manager
```

## 🔧 How It Works

### Startup Sequence
1. **Django Migrations** - Sets up SQLite database
2. **Create Superuser** - Creates admin user if needed
3. **Schedule Setup** - Creates Django-Q task (every 6 hours)
4. **Test Run** - Executes test job to verify setup
5. **Start Services** - Launches Django-Q cluster + web server

### Task Scheduling
- **Django-Q Cluster** - Background task processor
- **Schedule** - Every 6 hours (`0 */6 * * *`)
- **Database Storage** - Tasks stored in SQLite
- **Web Monitoring** - View task history via Django admin

### Container Architecture
```
Container
├── Django-Q Cluster (Background)
│   └── Processes scheduled snapshot tasks
└── Django Server (Port 8000)
    └── Web interface for monitoring
```

## 📋 Management Commands

### Run Snapshot Job
```bash
# Run immediately
python manage.py run_snapshot_job

# Run in test mode (no API calls)
python manage.py run_snapshot_job --test-mode

# Run asynchronously via Django-Q
python manage.py run_snapshot_job --async
```

### Manage Scheduling
```bash
# Setup 6-hour schedule
python manage.py run_snapshot_job --schedule

# List all scheduled tasks
python manage.py run_snapshot_job --list-schedules
```

## 🌐 Web Interface

- **Home**: `http://localhost:8000/` - Dashboard
- **Admin**: `http://localhost:8000/admin/` - Django admin
  - View scheduled tasks
  - Monitor task execution history
  - Manage users and settings

## 📊 Monitoring

### Container Logs
```bash
# View all logs
docker logs -f contabo-snapshots

# Check Django-Q cluster status
docker exec contabo-snapshots python manage.py qmonitor
```

### Task Status
```bash
# List scheduled tasks
docker exec contabo-snapshots python manage.py run_snapshot_job --list-schedules

# Run test job
docker exec contabo-snapshots python manage.py run_snapshot_job --test-mode
```

## 🔒 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `CLIENT_ID` | Contabo API Client ID | Yes | - |
| `API_USER` | Contabo API Username | Yes | - |
| `API_PASSWORD` | Contabo API Password | Yes | - |
| `CLIENT_SECRET` | Contabo API Client Secret | Yes | - |
| `ADMIN_EMAIL` | Email for notifications | Yes | - |
| `EMAIL_FROM` | From email address | Yes | - |
| `SMTP_SERVER` | SMTP server address | Yes | - |
| `SMTP_PORT` | SMTP server port | No | 587 |
| `SMTP_USERNAME` | SMTP username | Yes | - |
| `SMTP_PASSWORD` | SMTP password | Yes | - |
| `TZ` | Timezone | No | Asia/Manila |
| `LOG_MAX_MB` | Max log file size (MB) | No | 200 |
| `LOG_BACKUP_COUNT` | Log backup files | No | 5 |

## 🎯 Benefits of This Setup

### Simplified Architecture
- ✅ **No Supervisor** - Single process management
- ✅ **No Cron** - Django-Q handles scheduling
- ✅ **No PostgreSQL** - SQLite for simplicity
- ✅ **Clean Dockerfile** - Minimal layers and dependencies

### Easy Management
- ✅ **Django Admin** - Web-based task monitoring
- ✅ **Management Commands** - Easy CLI operations
- ✅ **Docker Logs** - All output in one place
- ✅ **Test Mode** - Safe testing without API calls

### Reliable Scheduling
- ✅ **Django-Q** - Robust task queue system
- ✅ **Database Storage** - Persistent task history
- ✅ **Error Handling** - Automatic retry and logging
- ✅ **Web Monitoring** - Real-time task status

## 🚨 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs contabo-snapshots

# Verify environment variables
docker exec contabo-snapshots env | grep -E "(CLIENT_ID|SMTP_SERVER)"
```

### Tasks Not Running
```bash
# Check Django-Q cluster
docker exec contabo-snapshots python manage.py qmonitor

# List scheduled tasks
docker exec contabo-snapshots python manage.py run_snapshot_job --list-schedules

# Run test job
docker exec contabo-snapshots python manage.py run_snapshot_job --test-mode
```

### Database Issues
```bash
# Run migrations
docker exec contabo-snapshots python manage.py migrate

# Check database
docker exec contabo-snapshots python manage.py shell
```

## 📝 Development

### Local Development
```bash
# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django-Q cluster
python manage.py qcluster &

# Start development server
python manage.py runserver
```

### Testing
```bash
# Verify setup
python3 verify_setup.py

# Test snapshot job
python manage.py run_snapshot_job --test-mode

# Test async execution
python manage.py run_snapshot_job --async
```

This simplified setup provides all the functionality of the original system with much cleaner architecture and easier maintenance! 🎉
