from django.db import models
from CRM.notes.models import Notes
from django.contrib.auth.models import User

class Scheduler(models.Model):
    # responsible = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    finished_at = models.DateTimeField(null = True)
    complete = models.BooleanField(default = False)
    # notes = models.ManyToManyField(Notes, )

# class NotesScheduler(models.Model):
#     notes = models.ForeignKey(Notes, on_delete = models.CASCADE)
#     scheduler = models.ForeignKey(Scheduler, on_delete = models.CASCADE)