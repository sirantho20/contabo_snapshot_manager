from django.core.management.base import BaseCommand
import logging
import sys
import os
import subprocess
from datetime import datetime
import pytz

# Add the parent directory to the path so we can import lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from lib import ContaboSnapshotManager


class Command(BaseCommand):
    help = 'Run the Contabo snapshot management job'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Setup the scheduled task to run every 12 hours using cron',
        )
        parser.add_argument(
            '--list-schedules',
            action='store_true',
            help='List all scheduled snapshot jobs',
        )

    def handle(self, *args, **options):
        # Set up timezone-aware logging
        timezone_name = os.environ.get('TZ', 'Asia/Manila')
        self.stdout.write(f"Using timezone: {timezone_name}")
        
        if options['schedule']:
            self.setup_scheduled_task()
        elif options['list_schedules']:
            self.list_scheduled_tasks()
        else:
            self.run_snapshot_job()

    def run_snapshot_job(self):
        """Run the snapshot management job."""
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
        """Setup the scheduled task using cron schedule from environment variable."""
        try:
            # Get cron schedule from environment variable with fallback to default 12-hour schedule
            cron_schedule = os.environ.get('CRON_SCHEDULE', '0 0,12 * * *')
            
            # Create the cron job command that redirects to stdout
            cron_command = f"{cron_schedule} cd /app && python manage.py run_snapshot_job 2>&1"
            
            self.stdout.write(f"Setting up cron job with schedule: {cron_schedule}")
            self.stdout.write(f"Cron command: {cron_command}")
            
            # Check if the cron job already exists
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_crontab = result.stdout if result.returncode == 0 else ""
            
            self.stdout.write(f"Existing crontab: {repr(existing_crontab)}")
            
            if cron_command not in existing_crontab:
                # Add the new cron job with proper newline handling
                if existing_crontab.strip():
                    # If there's existing content, add newline + command + newline
                    new_crontab = existing_crontab.rstrip() + "\n" + cron_command + "\n"
                else:
                    # If no existing content, just add command + newline
                    new_crontab = cron_command + "\n"
                
                self.stdout.write(f"New crontab content: {repr(new_crontab)}")
                
                # Write the new crontab
                subprocess.run(['crontab', '-'], input=new_crontab, text=True, check=True)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Scheduled snapshot job created with schedule: {cron_schedule}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Scheduled snapshot job already exists')
                )
                
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up cron job: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR(f'Command output: {e.stdout if e.stdout else "No output"}')
            )
            self.stdout.write(
                self.style.ERROR(f'Command error: {e.stderr if e.stderr else "No error output"}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up cron job: {str(e)}')
            )

    def list_scheduled_tasks(self):
        """List all scheduled snapshot tasks."""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                crontab_lines = result.stdout.strip().split('\n')
                snapshot_jobs = [line for line in crontab_lines if 'run_snapshot_job' in line]
                
                if snapshot_jobs:
                    self.stdout.write('Scheduled snapshot tasks:')
                    for job in snapshot_jobs:
                        self.stdout.write(f'  - {job}')
                else:
                    self.stdout.write('No scheduled snapshot tasks found.')
            else:
                self.stdout.write('No crontab found.')
                
        except subprocess.CalledProcessError:
            self.stdout.write('No crontab found.')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error listing cron jobs: {str(e)}')
            ) 