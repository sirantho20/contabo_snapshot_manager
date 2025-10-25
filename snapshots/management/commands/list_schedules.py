from django.core.management.base import BaseCommand
from django_q.models import Schedule, Task
from django.utils import timezone


class Command(BaseCommand):
    help = 'List all Django-Q scheduled tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about schedules',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        self.stdout.write("=== Django-Q Scheduled Tasks ===\n")
        
        # Get all schedules
        schedules = Schedule.objects.all().order_by('name')
        
        if not schedules.exists():
            self.stdout.write(
                self.style.WARNING('No scheduled tasks found.')
            )
            return
        
        for schedule in schedules:
            self.stdout.write(f"📋 {schedule.name}")
            self.stdout.write(f"   Function: {schedule.func}")
            self.stdout.write(f"   Schedule: {schedule.cron}")
            self.stdout.write(f"   Next run: {schedule.next_run}")
            self.stdout.write(f"   Repeats: {schedule.repeats}")
            
            if verbose:
                # Check if created field exists
                if hasattr(schedule, 'created') and schedule.created:
                    self.stdout.write(f"   Created: {schedule.created}")
                
                # Check for last run - it might be a method or property
                try:
                    last_run = schedule.last_run() if callable(schedule.last_run) else schedule.last_run
                    if last_run:
                        self.stdout.write(f"   Last run: {last_run}")
                    else:
                        self.stdout.write(f"   Last run: Never")
                except (AttributeError, TypeError):
                    self.stdout.write(f"   Last run: Never")
                
                # Show recent task executions
                recent_tasks = Task.objects.filter(
                    name=schedule.name
                ).order_by('-started')[:3]
                
                if recent_tasks.exists():
                    self.stdout.write(f"   Recent executions:")
                    for task in recent_tasks:
                        status = "✅ Success" if task.success else "❌ Failed"
                        self.stdout.write(f"     - {task.started}: {status}")
                else:
                    self.stdout.write(f"   Recent executions: None")
            
            self.stdout.write("")  # Empty line
        
        # Summary
        total_schedules = schedules.count()
        active_schedules = schedules.filter(
            next_run__gt=timezone.now()
        ).count()
        
        self.stdout.write("=== Summary ===")
        self.stdout.write(f"Total schedules: {total_schedules}")
        self.stdout.write(f"Active schedules: {active_schedules}")
        
        if verbose:
            # Show recent task statistics
            recent_tasks = Task.objects.filter(
                started__gte=timezone.now() - timezone.timedelta(days=7)
            )
            
            if recent_tasks.exists():
                total_tasks = recent_tasks.count()
                successful_tasks = recent_tasks.filter(success=True).count()
                failed_tasks = total_tasks - successful_tasks
                
                self.stdout.write(f"\nLast 7 days task statistics:")
                self.stdout.write(f"  Total executions: {total_tasks}")
                self.stdout.write(f"  Successful: {successful_tasks}")
                self.stdout.write(f"  Failed: {failed_tasks}")
                
                if total_tasks > 0:
                    success_rate = (successful_tasks / total_tasks) * 100
                    self.stdout.write(f"  Success rate: {success_rate:.1f}%")
