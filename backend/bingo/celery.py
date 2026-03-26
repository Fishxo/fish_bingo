"""
Celery configuration for Bingo project
"""
import os
from datetime import timedelta
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo.settings')

app = Celery('bingo')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks (requires Celery Beat: celery -A bingo beat)
_beat = dict(getattr(app.conf, 'beat_schedule', None) or {})
_beat['broadcast-active-game-state-sync'] = {
    'task': 'api.tasks.task_broadcast_active_game_state_sync',
    'schedule': timedelta(seconds=10),
}
app.conf.beat_schedule = _beat

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

