from django.core.management.base import BaseCommand
from django_q.tasks import schedule
from django_q.models import Schedule
import logging
import sys
import os

# Add the parent directory to the path so we can import lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from lib import ContaboSnapshotManager


class Command(BaseCommand):
    help = 'Run the Contabo snapshot management job'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Setup the scheduled task to run every 12 hours',
        )
        parser.add_argument(
            '--list-schedules',
            action='store_true',
            help='List all scheduled snapshot jobs',
        )

    def handle(self, *args, **options):
        if options['schedule']:
            self.setup_scheduled_task()
        elif options['list_schedules']:
            self.list_scheduled_tasks()
        else:
            self.run_snapshot_job()

    def run_snapshot_job(self):
        """Run the snapshot management job."""
        try:
            self.stdout.write(
                self.style.SUCCESS('Starting Contabo snapshot management job...')
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
        """Setup the scheduled task to run every 12 hours."""
        # Check if the schedule already exists
        existing_schedule = Schedule.objects.filter(
            func='django.core.management.call_command',
            args=('run_snapshot_job')
        ).first()
        
        if not existing_schedule:
            # Create a new schedule to run every 12 hours
            schedule(
                'django.core.management.call_command',
                'run_snapshot_job',
                schedule_type=Schedule.CRON,
                cron='0 0,12 * * *',
                name='Contabo Snapshot Management Job',
            )
            self.stdout.write(
                self.style.SUCCESS('Scheduled snapshot job created - will run every 12 hours')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Scheduled snapshot job already exists')
            )

    def list_scheduled_tasks(self):
        """List all scheduled snapshot tasks."""
        scheduled_tasks = Schedule.objects.filter(
            func='django.core.management.call_command',
            args=('run_snapshot_job')
        )
        
        if scheduled_tasks:
            self.stdout.write('Scheduled snapshot tasks:')
            for task in scheduled_tasks:
                self.stdout.write(f'  - {task.name} (ID: {task.id})')
                self.stdout.write(f'    Next run: {task.next_run}')
                self.stdout.write(f'    Schedule: {task.schedule_type} every {task.hours} hours')
        else:
            self.stdout.write('No scheduled snapshot tasks found.') 