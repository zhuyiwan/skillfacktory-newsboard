import os
from celery import Celery
 
 
app = Celery('crm')
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379'),
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


app.autodiscover_tasks(['crm'])