from django.shortcuts import render
from django.http import JsonResponse
from django_q.models import Schedule, Success, Failure
from django.utils import timezone
from datetime import timedelta


def home(request):
    """Home page view."""
    return render(request, 'snapshots/home.html')


def status(request):
    """Status page showing recent task executions."""
    # Get recent successful and failed tasks
    recent_successes = Success.objects.filter(
        func='snapshots.management.commands.run_snapshot_job'
    ).order_by('-started')[:10]
    
    recent_failures = Failure.objects.filter(
        func='snapshots.management.commands.run_snapshot_job'
    ).order_by('-started')[:10]
    
    # Get scheduled tasks
    scheduled_tasks = Schedule.objects.filter(
        func='snapshots.management.commands.run_snapshot_job'
    )
    
    context = {
        'recent_successes': recent_successes,
        'recent_failures': recent_failures,
        'scheduled_tasks': scheduled_tasks,
    }
    
    return render(request, 'snapshots/status.html', context) 