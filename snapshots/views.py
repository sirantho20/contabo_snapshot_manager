from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import os
import subprocess
from pathlib import Path


def home(request):
    """Home page view."""
    return render(request, 'snapshots/home.html')


def status(request):
    """Status page showing recent task executions."""
    # Get cron logs - since logs are now streamed to stdout, we'll show a message
    recent_executions = [
        "Cron logs are now streamed to Docker stdout",
        "Check 'docker logs <container_name>' to view recent executions",
        "Or use 'docker logs -f <container_name>' to follow logs in real-time"
    ]
    
    # Get scheduled tasks from crontab
    scheduled_tasks = []
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            crontab_lines = result.stdout.strip().split('\n')
            snapshot_jobs = [line for line in crontab_lines if 'run_snapshot_wrapper.sh' in line]
            scheduled_tasks = snapshot_jobs
        else:
            scheduled_tasks = ["No crontab found"]
    except Exception as e:
        scheduled_tasks = [f"Error reading crontab: {str(e)}"]
    
    # Get current cron schedule from environment
    cron_schedule = os.environ.get('CRON_SCHEDULE', '0 0,12 * * *')
    
    context = {
        'recent_executions': recent_executions,
        'scheduled_tasks': scheduled_tasks,
        'cron_schedule': cron_schedule,
    }
    
    return render(request, 'snapshots/status.html', context) 