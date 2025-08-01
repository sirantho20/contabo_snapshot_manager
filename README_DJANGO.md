# Contabo Snapshot Manager - Django Project

This is a Django-based re-engineering of the Contabo Snapshot Manager, using cron for task scheduling.

## Project Structure

```
snapshot_manager/
├── snapshot_manager/          # Main Django project
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI application
├── snapshots/                # Django app
│   ├── __init__.py
│   ├── apps.py               # App configuration
│   ├── urls.py               # App URL configuration
│   ├── views.py              # Web views
│   └── management/           # Management commands
│       └── commands/
│           └── run_snapshot_job.py
├── templates/                # HTML templates
│   └── snapshots/
│       ├── base.html
│       ├── home.html
│       └── status.html
├── lib.py                    # Original Contabo manager logic
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
└── setup_dev.py             # Development setup script
```

## Features

- **Django Management Command**: The snapshot job is now a Django management command
- **Web Interface**: Simple web interface to monitor task status
- **Cron Scheduling**: Automatic scheduling every 12 hours using cron
- **Task Monitoring**: View recent successful and failed task executions
- **Admin Interface**: Django admin for managing scheduled tasks

## Installation & Setup

### Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the development setup script:
   ```bash
   python setup_dev.py
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. The cron daemon will automatically handle scheduled tasks (no separate process needed)

### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t snapshot-manager .
   ```

2. Run the container:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -v $(pwd)/logs:/app/logs \
     -e SMTP_SERVER=your-smtp-server \
     -e TZ=Asia/Manila \
     -e CRON_SCHEDULE="0 0,12 * * *" \
     snapshot-manager
   ```

## Usage

### Management Commands

- **Run snapshot job manually**:
  ```bash
  python manage.py run_snapshot_job
  ```

- **Setup scheduled task (every 12 hours)**:
  ```bash
  python manage.py run_snapshot_job --schedule
  ```

- **List scheduled tasks**:
  ```bash
  python manage.py run_snapshot_job --list-schedules
  ```

### Web Interface

- **Home**: `http://localhost:8000/` - Overview and quick actions
- **Status**: `http://localhost:8000/status/` - Task execution history
- **Admin**: `http://localhost:8000/admin/` - Django admin interface

### Environment Variables

- `SMTP_SERVER`: SMTP server for email notifications
- `TZ`: Timezone for all logs and timestamps (default: Asia/Manila)
- `CRON_SCHEDULE`: Cron schedule for snapshot jobs (default: "0 0,12 * * *" - every 12 hours)
- `DJANGO_SETTINGS_MODULE`: Django settings module (set automatically)

## How It Works

1. **Cron Daemon**: Runs in the background to handle scheduled tasks
2. **Management Command**: `run_snapshot_job` executes the snapshot management logic
3. **Scheduling**: Tasks are scheduled according to the `CRON_SCHEDULE` environment variable
4. **Monitoring**: All task executions are logged and streamed to Docker stdout
5. **Logging**: All logs (Django, cron, supervisor) are streamed to Docker stdout for easy monitoring
6. **Timezone**: All timestamps use the timezone specified by the `TZ` environment variable

## Cron Schedule Examples

The `CRON_SCHEDULE` environment variable accepts standard cron expressions:

```bash
# Every 12 hours (default)
-e CRON_SCHEDULE="0 0,12 * * *"

# Every 6 hours
-e CRON_SCHEDULE="0 */6 * * *"

# Every day at 2 AM
-e CRON_SCHEDULE="0 2 * * *"

# Every Monday at 9 AM
-e CRON_SCHEDULE="0 9 * * 1"

# Every hour
-e CRON_SCHEDULE="0 * * * *"

# Every 30 minutes
-e CRON_SCHEDULE="*/30 * * * *"
```

## Benefits of Cron

- **System Standard**: Uses the standard Unix cron system
- **Reliability**: Proven and stable scheduling mechanism
- **Simple Configuration**: Easy to understand and modify
- **System Integration**: Works with standard system tools
- **Resource Efficient**: Lightweight compared to task queues
- **Flexible Scheduling**: Customize schedule via environment variable

## Development

### Adding New Management Commands

Create new commands in `snapshots/management/commands/`:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of your command'
    
    def handle(self, *args, **options):
        # Your command logic here
        pass
```

### Adding New Views

Add views to `snapshots/views.py` and update `snapshots/urls.py` accordingly.

### Database Migrations

When making model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Cron Daemon Not Starting

Check if cron is running:
```bash
service cron status
```

### Tasks Not Running

Verify the scheduled task exists:
```bash
python manage.py run_snapshot_job --list-schedules
```

Check container logs:
```bash
docker logs <container_name>
```

Follow logs in real-time:
```bash
docker logs -f <container_name>
```

### Web Interface Not Loading

Ensure the Django development server is running:
```bash
python manage.py runserver
```

### Timezone Issues

If logs show incorrect timestamps, check the timezone setting:
```bash
# Check current timezone in container
docker exec <container_name> date

# Set custom timezone when running container
docker run -d -e TZ=UTC snapshot-manager
```

### Cron Schedule Issues

If tasks are not running at expected times, check the cron schedule:
```bash
# Check current cron schedule in container
docker exec <container_name> crontab -l

# Verify cron schedule format
docker exec <container_name> python -c "import os; print('CRON_SCHEDULE:', os.environ.get('CRON_SCHEDULE', '0 0,12 * * *'))"
``` 