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
    # for i in range(N):
    #     time.sleep(1)
    #     print(i+1)

    users = User.objects.all()
    subscriptions = Subscription.objects.all()
    print(users)

    for user in users:
        user_subscription = subscriptions.filter(user = user)
        if user_subscription:
            print(user_subscription)

    # emails = User.objects.filter(subscriptions__topic_root=root_note).values_list('email', flat=True)
    # print(emails)
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
