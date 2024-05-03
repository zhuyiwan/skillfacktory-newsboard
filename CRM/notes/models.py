from django.contrib.auth.models import User
from django.db import models
import uuid

# Create your models here.
class BasicModelTemplate(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


COEFICIENT = {
    "Блок": 3,
    "К выполнению": 2,
    "Коментарий": 1,
}

class ProfilesRoles(models.TextChoices):
    admin = "Администратор"
    manager = "Руководитель"
    employee = "Работник"
    client = "Килент"
    operaton = "Оператор" 

# def get_raiting(queryset):
#         queryset = Notes.objects.all()
#         raiting = [-1, 1]
#         likes_topics = queryset.filter(category)
#         likes_tasks
#         likes_comments 


class Profiles(BasicModelTemplate):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ProfilesRoles.choices)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def renew_raiting(self):
        global COEFICIENT
        sum = 0
        queryset = NotesReaction.objects.all()
        for key, value in COEFICIENT.items(): 
            likes_topics = queryset.filter(note__created_by=self, reaction=True, note__category=key)
            sum += likes_topics.count() * value
        self.likes = sum

        dislikes_topics = queryset.filter(note__created_by=self, reaction=True)
        self.dislikes = dislikes_topics.count()

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"



class CategoryType(models.TextChoices):
    topic = "Блок"
    task = "К выполнению"
    comment = "Коментарий"

class Notes(BasicModelTemplate):
    created_by = models.ForeignKey(Profiles, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100)
    content = models.TextField()
    notes_relations = models.ForeignKey('Notes', on_delete=models.CASCADE, related_name='note_parent', null=True, blank=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    category = models.CharField(max_length=16, choices=CategoryType.choices)

    def renew_raiting(self):
        queryset = NotesReaction.objects.all()
        likes_topics = queryset.filter(note=self, reaction=True)
        dislikes_topics = queryset.filter(note=self, reaction=False)
        self.likes = likes_topics.count()
        self.dislikes = dislikes_topics.count()

    def clean(self):
        if self.notes_relations and self.notes_relations == self:
            raise ValidationError("Заметка не может ссылаться сама на себя.")
                
    def _add_reaction(self, profile, reaction_value):
        # Проверяем существует ли уже реакция для данного профайла.
        # Если нет, то создаём новую и корректирую карму создателя статьи.
        # Если да, то меняем карму на противоположную
        global COEFICIENT
        try:
            reaction = NotesReaction.objects.get(note=self, profile=profile)
            if reaction.reaction != reaction_value:
                if reaction_value:
                    self.created_by.likes += COEFICIENT[self.category]
                    self.created_by.dislikes -= 1
                else:
                    self.created_by.likes -= COEFICIENT[self.category]
                    self.created_by.dislikes += 1
           
            reaction.reaction = reaction_value
            reaction.save()

        except NotesReaction.DoesNotExist:
            NotesReaction.objects.create(
                note=self,
                profile=profile,
                reaction=reaction_value
            )
            if reaction_value:
                self.created_by.likes += COEFICIENT[self.category]
            else:
                self.created_by.dislikes += 1


    def like(self, profile):
        self._add_reaction(profile, 1)
        self.likes += 1

    def dislike(self, profile):
        self._add_reaction(profile, 0)
        self.dislikes += 1
        self.created_by.dislikes += 1
            
    class Meta:
        verbose_name = ('note')
        verbose_name_plural = ('notes')

    def __str__(self):
        return self.title

class NotesReaction(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=True, primary_key=True)
    note = models.ForeignKey(Notes, on_delete=models.DO_NOTHING, related_name="notereactions_to_note")
    profile = models.ForeignKey(Profiles, on_delete=models.DO_NOTHING, related_name="notereactions_to_profile")
    reaction = models.BooleanField(default=True)

    class Meta:
        verbose_name = ('note reaction')
        verbose_name_plural = ('note reactions')
      
        constraints = [
                models.UniqueConstraint(fields=['note', 'profile'], name="unique_note_profile")
            ]
        
    def __str__(self) :
        reaction = "Like" if self.reaction else "Dislike"
        return f"{self.note.title} - {self.profile.user.username} : {reaction}"


'''
Откладываем на будущее
class TagsConnection(BasicModelTemplate):
    note_id = models.ForeignKey(Notes, on_delete=models.CASCADE)
    tag_shcema = models.CharField(max_length=20)
    tag_table = models.CharField(max_length=20)
    tag_key = models.CharField(max_length=16)

    class Meta:
        verbose_name = "tags connection"
        verbose_name_plural = "tags connections"
'''


class NotesRole(models.TextChoices):
    owner = "Отвественный"
    executor = "Исполнитель"
    spectator = "Наблюдаель"
    assignor = "Постановщик"

class NotesToProfiles(BasicModelTemplate):
    note_id = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="notes_profiles")
    profile_id = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="profiles_notes")
    role = models.CharField(max_length=20, choices=NotesRole.choices)  # Ссылка на роли из NotesRole

    class Meta:
        verbose_name = "Notes Profile Relation"
        verbose_name_plural = "Notes Profile Relations"
        unique_together = ("note_id", "profile_id")  # Уникальное сочетание note и profile для исключения дубликатов

    def __str__(self):
        return f"{self.profile_id.user.username} - {self.note_id.title} ({self.role})"