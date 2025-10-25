from django.core.management.base import BaseCommand
from django_q.models import Schedule
from django_q.tasks import schedule
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up Django-Q scheduled task for snapshot management'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=6,
            help='Hours between snapshot runs (default: 6)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate the schedule even if it exists',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        force = options['force']
        
        schedule_name = f'snapshot_job_{hours}h'
        cron_expression = f'0 */{hours} * * *'  # Every N hours
        
        self.stdout.write(f"Setting up scheduled task: {schedule_name}")
        self.stdout.write(f"Cron expression: {cron_expression}")
        
        try:
            # Check if the schedule already exists
            existing_schedule = Schedule.objects.filter(
                func='snapshots.tasks.run_snapshot_job',
                name=schedule_name
            ).first()
            
            if existing_schedule and not force:
                self.stdout.write(
                    self.style.WARNING(f'Scheduled task "{schedule_name}" already exists')
                )
                self.stdout.write(f'Next run: {existing_schedule.next_run}')
                self.stdout.write(f'Repeats: {existing_schedule.repeats}')
                return
            
            # Delete existing schedule if force is True
            if existing_schedule and force:
                existing_schedule.delete()
                self.stdout.write(
                    self.style.WARNING(f'Deleted existing schedule: {schedule_name}')
                )
            
            # Create a new schedule
            new_schedule = schedule(
                'snapshots.tasks.run_snapshot_job',
                name=schedule_name,
                schedule_type=Schedule.CRON,
                cron=cron_expression,
                repeats=-1  # Repeat indefinitely
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Scheduled task created successfully!')
            )
            self.stdout.write(f'Task ID: {new_schedule}')
            self.stdout.write(f'Schedule: Every {hours} hours')
            self.stdout.write(f'Cron: {cron_expression}')
            
            # Display the created schedule details
            created_schedule = Schedule.objects.filter(
                func='snapshots.tasks.run_snapshot_job',
                name=schedule_name
            ).first()
            
            if created_schedule:
                self.stdout.write(f'Next run: {created_schedule.next_run}')
                self.stdout.write(f'Repeats: {created_schedule.repeats}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up scheduled task: {str(e)}')
            )
            logger.error(f"Error setting up scheduled task: {str(e)}")
            raise
