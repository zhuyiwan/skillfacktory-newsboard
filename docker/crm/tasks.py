from celery import shared_task
import time
import redis

@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")

@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)
    print("Finished!")

@shared_task
def send_ping():
    client = redis.Redis(host='redis', port=6379, db=0)
    response = client.ping()
    print("PING response:", response)