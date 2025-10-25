"""
Django-Q tasks for snapshot management.
"""
import logging
from django_q.tasks import schedule
from django_q.models import Schedule
from lib import ContaboSnapshotManager

logger = logging.getLogger(__name__)


def run_snapshot_job():
    """
    Task function to run the snapshot management job.
    This function will be executed by django-q workers.
    """
    try:
        logger.info("Starting Contabo snapshot management job via django-q...")
        manager = ContaboSnapshotManager()
        manager.manage_snapshots()
        logger.info("Snapshot management job completed successfully!")
        return "Snapshot job completed successfully"
    except Exception as e:
        logger.error(f"Error in snapshot job: {str(e)}")
        raise


def setup_scheduled_task():
    """
    Set up the scheduled task to run every 6 hours.
    This should be called once during setup.
    """
    try:
        # Check if the schedule already exists
        existing_schedule = Schedule.objects.filter(
            func='snapshots.tasks.run_snapshot_job',
            name='snapshot_job_6h'
        ).first()
        
        if existing_schedule:
            logger.info("Scheduled task already exists")
            return "Schedule already exists"
        
        # Create a new schedule to run every 6 hours
        schedule(
            'snapshots.tasks.run_snapshot_job',
            name='snapshot_job_6h',
            schedule_type=Schedule.CRON,
            cron='0 */6 * * *',  # Every 6 hours
            repeats=-1  # Repeat indefinitely
        )
        
        logger.info("Scheduled task created successfully - runs every 6 hours")
        return "Schedule created successfully"
        
    except Exception as e:
        logger.error(f"Error setting up scheduled task: {str(e)}")
        raise


def run_test_job():
    """
    Test task function that doesn't make actual API calls.
    """
    try:
        logger.info("Running test snapshot job (no API calls)...")
        logger.info("TEST MODE: Would normally connect to Contabo API...")
        logger.info("TEST MODE: Would normally list instances...")
        logger.info("TEST MODE: Would normally create snapshots...")
        logger.info("TEST MODE: Would normally send email summary...")
        logger.info("Test snapshot job completed successfully!")
        return "Test job completed successfully"
    except Exception as e:
        logger.error(f"Error in test job: {str(e)}")
        raise
