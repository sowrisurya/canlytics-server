import celery
import os
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

celery_app = celery.Celery(
    'celery_app', 
    broker='redis://localhost:6379/0', 
    include=[
        'backgroundTasks'
    ]
)

celery_app.conf.beat_schedule = {
    'schedule_logs': {
        'task': 'backgroundTasks.vehicle_logs_schedule',
        'schedule': 30.0,
    },
}
celery_app.conf.timezone = 'UTC'