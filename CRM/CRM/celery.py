import os
from celery import Celery
from celery.schedules import crontab
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CRM.settings')
 
app = Celery('CRM')
app.config_from_object('django.conf:settings', namespace = 'CELERY')

app.autodiscover_tasks()

# Рассылка каждое утро в 9 в течении рабочей недели
app.conf.beat_schedule = {
    'print_every_5_seconds': {
        'task': 'notes.tasks.printer',
        # 'schedule': 5,
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
        'args': (5,),
    },
}