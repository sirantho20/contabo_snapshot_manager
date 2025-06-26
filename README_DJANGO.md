# Contabo Snapshot Manager - Django Project

This is a Django-based re-engineering of the Contabo Snapshot Manager, using django-q2 for task scheduling instead of cron jobs.

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
- **Django Q2 Scheduling**: Automatic scheduling every 12 hours using django-q2
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

4. Start the Django Q cluster (in a separate terminal):
   ```bash
   python -m django_q.cluster
   ```

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
- `DJANGO_SETTINGS_MODULE`: Django settings module (set automatically)

## How It Works

1. **Django Q2 Cluster**: Runs in the background to handle scheduled tasks
2. **Management Command**: `run_snapshot_job` executes the snapshot management logic
3. **Scheduling**: Tasks are scheduled to run every 12 hours automatically
4. **Monitoring**: All task executions are logged and can be viewed via the web interface
5. **Persistence**: Task history and schedules are stored in the Django database

## Benefits Over Cron

- **Better Error Handling**: Failed tasks are logged and can be retried
- **Web Interface**: Monitor task status without SSH access
- **Flexible Scheduling**: Easy to modify schedules without restarting containers
- **Task History**: Complete history of all task executions
- **Django Integration**: Leverages Django's admin interface and ORM

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

### Django Q Cluster Not Starting

Check if the database is properly migrated:
```bash
python manage.py migrate
```

### Tasks Not Running

Verify the scheduled task exists:
```bash
python manage.py run_snapshot_job --list-schedules
```

### Web Interface Not Loading

Ensure the Django development server is running:
```bash
python manage.py runserver
``` 