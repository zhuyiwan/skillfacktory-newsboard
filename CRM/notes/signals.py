from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.console import EmailBackend
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notes, NoteStructureModel

@receiver(post_save, sender=Notes)
def note_created(instance, created, **kwargs):
    if not created:
        return
    
    try:
        note_structure = NoteStructureModel.objects.get(current_note=instance)
        root_note = note_structure.root_note
    except NoteStructureModel.DoesNotExist:
        return
    
    emails = User.objects.filter(
        subscriptions__topic_root=root_note
    ).values_list('email', flat=True)

    subject = f'Новый коментарый в ветке {root_note.title}'

    text_content = (
        f'Ветка: {root_note.title}\n'
        f'Коментарий: {instance.content}\n\n'
        f'Ссылка тему: http://127.0.0.1:8000{root_note.get_absolute_url()}'
    )
    html_content = (
        f'Ветка: {root_note.title}<br>'
        f'Коментарий: {instance.content}<br><br>'
        f'<a href="http://127.0.0.1{root_note.get_absolute_url()}">'
        f'Ссылка на тему</a>'
    )
    
    print(emails)
    for email in emails:
        msg = EmailBackend(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()