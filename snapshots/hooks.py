# snapshots/hooks.py
import logging
from django_q.models import Success, Failure
from django.core.cache import cache

logger = logging.getLogger(__name__)

def schedule_completed(task):
    """Hook called when schedule completes"""
    logger.info(f"Schedule completed: {task.func_name}")
    
    # Clear any running flags
    cache.delete('snapshot_job_running')

def prevent_duplicate_execution(func_name, *args, **kwargs):
    """Decorator to prevent duplicate task execution"""
    cache_key = f'{func_name}_running'
    
    if cache.get(cache_key):
        logger.warning(f"Task {func_name} already running, skipping...")
        return False
    
    # Set running flag
    cache.set(cache_key, True, timeout=600)  # 10 minute timeout
    
    try:
        # Execute the task
        result = func_name(*args, **kwargs)
        return result
    finally:
        # Clear running flag
        cache.delete(cache_key)