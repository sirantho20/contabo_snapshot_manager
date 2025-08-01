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
        parser.add_argument(
            '--test-cron',
            action='store_true',
            help='Test the cron job execution manually',
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run in test mode (skip actual snapshot operations)',
        )

    def handle(self, *args, **options):
        # Set up timezone-aware logging
        timezone_name = os.environ.get('TZ', 'Asia/Manila')
        self.stdout.write(f"Using timezone: {timezone_name}")
        
        if options['schedule']:
            self.setup_scheduled_task()
        elif options['list_schedules']:
            self.list_scheduled_tasks()
        elif options['test_cron']:
            self.test_cron_execution()
        elif options['test_mode']:
            self.run_snapshot_job_test()
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
            
            # Create a wrapper script to ensure proper environment
            wrapper_script = """#!/bin/bash
set -e
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Starting snapshot job wrapper..."
cd /app
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Changed to /app directory"
export PYTHONPATH=/app
export DJANGO_SETTINGS_MODULE=snapshot_manager.settings
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Environment set up, running Django command..."
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Current directory: $(pwd)"
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Python path: $PYTHONPATH"
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Django settings: $DJANGO_SETTINGS_MODULE"
timeout 300 python manage.py run_snapshot_job 2>&1
echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] Snapshot job wrapper completed"
"""
            
            # Write the wrapper script
            with open('/app/run_snapshot_wrapper.sh', 'w') as f:
                f.write(wrapper_script)
            
            # Make it executable
            subprocess.run(['chmod', '+x', '/app/run_snapshot_wrapper.sh'], check=True)
            
            # Create the cron job command using the wrapper script
            cron_command = f"{cron_schedule} /app/run_snapshot_wrapper.sh"
            
            self.stdout.write(f"Setting up cron job with schedule: {cron_schedule}")
            self.stdout.write(f"Cron command: {cron_command}")
            self.stdout.write(f"Wrapper script created: /app/run_snapshot_wrapper.sh")
            
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
                snapshot_jobs = [line for line in crontab_lines if 'run_snapshot_wrapper.sh' in line]
                
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

    def test_cron_execution(self):
        """Test the cron job execution manually."""
        try:
            self.stdout.write("Testing cron job execution...")
            
            # First test basic Django command
            self.stdout.write("Testing basic Django command...")
            result = subprocess.run(['python', 'manage.py', 'run_snapshot_job'], 
                                  capture_output=True, text=True, timeout=30)
            
            self.stdout.write(f"Basic Django command exit code: {result.returncode}")
            self.stdout.write(f"Basic Django command stdout: {result.stdout}")
            self.stdout.write(f"Basic Django command stderr: {result.stderr}")
            
            # Check if wrapper script exists
            if os.path.exists('/app/run_snapshot_wrapper.sh'):
                self.stdout.write("Wrapper script exists, testing execution...")
                
                # Execute the wrapper script with shorter timeout for testing
                result = subprocess.run(['/app/run_snapshot_wrapper.sh'], 
                                      capture_output=True, text=True, timeout=30)
                
                self.stdout.write(f"Wrapper script exit code: {result.returncode}")
                self.stdout.write(f"Wrapper script stdout: {result.stdout}")
                self.stdout.write(f"Wrapper script stderr: {result.stderr}")
                
                if result.returncode == 0:
                    self.stdout.write(self.style.SUCCESS("Cron job test successful!"))
                else:
                    self.stdout.write(self.style.ERROR("Cron job test failed!"))
            else:
                self.stdout.write(self.style.WARNING("Wrapper script not found. Run --schedule first."))
                
        except subprocess.TimeoutExpired:
            self.stdout.write(self.style.ERROR("Cron job test timed out after 30 seconds"))
            # Try to get partial output
            try:
                result = subprocess.run(['/app/run_snapshot_wrapper.sh'], 
                                      capture_output=True, text=True, timeout=5)
                self.stdout.write(f"Partial output before timeout: {result.stdout}")
                self.stdout.write(f"Partial error before timeout: {result.stderr}")
            except:
                self.stdout.write("Could not get partial output")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing cron job: {str(e)}")) 

    def run_snapshot_job_test(self):
        """Run the snapshot management job in test mode."""
        try:
            timezone_name = os.environ.get('TZ', 'Asia/Manila')
            current_time = datetime.now(pytz.timezone(timezone_name))
            
            self.stdout.write(
                self.style.SUCCESS(f'Starting Contabo snapshot management job (TEST MODE) at {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}...')
            )
            
            # Simulate the job without making actual API calls
            self.stdout.write("TEST MODE: Simulating snapshot management job...")
            self.stdout.write("TEST MODE: Would normally connect to Contabo API...")
            self.stdout.write("TEST MODE: Would normally list instances...")
            self.stdout.write("TEST MODE: Would normally create snapshots...")
            self.stdout.write("TEST MODE: Would normally send email summary...")
            
            # Simulate some delay
            import time
            time.sleep(2)
            
            self.stdout.write(
                self.style.SUCCESS('Snapshot management job (TEST MODE) completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in snapshot job test: {str(e)}')
            )
            logging.error(f"Error in snapshot job test: {str(e)}")
            raise 