from django.core.management.base import BaseCommand
import logging
import sys
import os
from datetime import datetime
import pytz
from django_q.tasks import async_task
from django_q.models import Schedule

# Add the parent directory to the path so we can import lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from lib import ContaboSnapshotManager
from snapshots.tasks import run_snapshot_job, setup_scheduled_task, run_test_job


class Command(BaseCommand):
    help = 'Run the Contabo snapshot management job'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Setup the scheduled task to run every 6 hours using django-q',
        )
        parser.add_argument(
            '--list-schedules',
            action='store_true',
            help='List all scheduled snapshot jobs',
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (skip actual snapshot operations)',
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run the job asynchronously using django-q',
        )

    def handle(self, *args, **options):
        # Set up timezone-aware logging
        timezone_name = os.environ.get('TZ', 'Asia/Manila')
        self.stdout.write(f"Using timezone: {timezone_name}")
        
        if options['schedule']:
            self.setup_scheduled_task()
        elif options['list_schedules']:
            self.list_scheduled_tasks()
        elif options['test_mode']:
            self.run_test_job()
        elif options['async']:
            self.run_async_job()
        else:
            self.run_snapshot_job()

    def run_snapshot_job(self):
        """Run the snapshot management job synchronously."""
        try:
            timezone_name = os.environ.get('TZ', 'Asia/Manila')
            current_time = datetime.now(pytz.timezone(timezone_name))
            
            self.stdout.write(
                self.style.SUCCESS(f'Starting Contabo snapshot management job at {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}...')
            )
            
            manager = ContaboSnapshotManager()
            manager.manage_snapshots()
            
            self.stdout.write(
                self.style.SUCCESS('Snapshot management job completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in snapshot job: {str(e)}')
            )
            logging.error(f"Error in snapshot job: {str(e)}")
            raise

    def setup_scheduled_task(self):
        """Setup the scheduled task using django-q."""
        try:
            result = setup_scheduled_task()
            self.stdout.write(
                self.style.SUCCESS(f'Django-Q scheduled task setup: {result}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up scheduled task: {str(e)}')
            )

    def list_scheduled_tasks(self):
        """List all scheduled snapshot tasks."""
        try:
            schedules = Schedule.objects.filter(func='snapshots.tasks.run_snapshot_job')
            if schedules.exists():
                self.stdout.write('Scheduled snapshot tasks:')
                for schedule in schedules:
                    self.stdout.write(f'  - {schedule.name}: {schedule.cron} (Next run: {schedule.next_run})')
            else:
                self.stdout.write('No scheduled snapshot tasks found.')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error listing scheduled tasks: {str(e)}')
            )

    def run_test_job(self):
        """Run the test job synchronously."""
        try:
            result = run_test_job()
            self.stdout.write(
                self.style.SUCCESS(f'Test job result: {result}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in test job: {str(e)}')
            )

    def run_async_job(self):
        """Run the snapshot job asynchronously using django-q."""
        try:
            task_id = async_task('snapshots.tasks.run_snapshot_job')
            self.stdout.write(
                self.style.SUCCESS(f'Snapshot job queued with task ID: {task_id}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error queuing async job: {str(e)}')
            ) 