from celery import shared_task
import time
import redis
from django.contrib.auth.models import User

from .models import Subscription


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")

@shared_task
def printer(N):
    users = User.objects.all()
    subscriptions = Subscription.objects.all()

    # Проверяем всех подписки которые ещё есть у пользователей
    for user in users:
        user_subscription = subscriptions.filter(user = user)
        if user_subscription:
            # Извините, скорее всего оповещение буду прикручивать к телеграмму
            # Не вижу смысла дублировать инфомрацию в почту. 
            # Расслку при необходимости можно сделать по полному аналогу с сигналами
            print(user_subscription)

    print("Finished!")

@shared_task
def send_ping():
    client = redis.Redis(host='localhost', port=6379, db=0)
    response = client.ping()
    print("PING response:", response)

@shared_task
def note_created():
    print('Note just was created')
    # Нужно поднять список подписанных на заметку.
