from django.contrib.auth.models import User
from django.db import models
import uuid
from django.urls import reverse

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
    TOPIC = "topic", "Проект" # Задумка
    TASK = "task", "Задача" # Воплощение
    INSTRUCTION = "instruction", "Руководство" # Регламент
    COMMENT = "comment", "Коментарий" # Пиздёжь 
    KEY_COMMENT = "key_comment", "Фокус" # Пиздёжь по делу
    SCHEDULER = "scheduler", "Планировщик" # Ситуация на момнет дедлайна

class Notes(BasicModelTemplate):
    created_by = models.ForeignKey(Profiles, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("note_detals", kwargs={"pk": self.pk})
    

    def renew_raiting(self):
        queryset = NotesReaction.objects.all()
        likes_topics = queryset.filter(note=self, reaction=True)
        dislikes_topics = queryset.filter(note=self, reaction=False)
        self.likes = likes_topics.count()
        self.dislikes = dislikes_topics.count()

    # def clean(self):
    #     if self.notes_relations and self.notes_relations == self:
    #         raise ValidationError("Заметка не может ссылаться сама на себя.")
                
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
        if self.title:
            return self.title
        else:
            try:
                note_structure = self.note_structure_current.get()
                root_note_title = note_structure.root_note.title if note_structure.root_note.title else "No Title"
                return f'comment to: {root_note_title}'
            except NoteStructureModel.DoesNotExist:
                return f'Note ID: {self.id}'

class NoteStructureModel(BasicModelTemplate):
    '''
    Разводим по двум разным таблицам объект CRM системы
    И его места в структуре CRM системы.
    Начнём с малого. 
    Задаём дерево "проекта" к которому можно отнести заметку и в котором будем её искать.
    Задаём позицию в данном дереве (где эта заметка будет находиться)
    В дальнейшем превести на Postgres и добавить ltree
    '''
    root_note = models.ForeignKey(Notes, on_delete=models.DO_NOTHING, related_name="note_structure_root")
    parent_note =  models.ForeignKey(Notes, on_delete=models.DO_NOTHING, related_name="note_structure_parent") 
    current_note =  models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="note_structure_current")
    category = models.CharField(max_length=16, choices=CategoryType.choices)

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



class NotesRole(models.TextChoices):
    owner = "Отвественный"
    executor = "Исполнитель"
    spectator = "Наблюдаель"
    assignor = "Постановщик"

class NotesToProfiles(BasicModelTemplate):
    '''
    Ориентируемся на будущее, когда для каждого задания нужно будет права доступа и действия
    '''
    note_id = models.ForeignKey(Notes, on_delete=models.CASCADE, related_name="notes_profiles")
    profile_id = models.ForeignKey(Profiles, on_delete=models.CASCADE, related_name="profiles_notes")
    role = models.CharField(max_length=20, choices=NotesRole.choices)  # Ссылка на роли из NotesRole

    class Meta:
        verbose_name = "Notes Profile Relation"
        verbose_name_plural = "Notes Profile Relations"
        unique_together = ("note_id", "profile_id")  # Уникальное сочетание note и profile для исключения дубликатов

    def __str__(self):
        return f"{self.profile_id.user.username} - {self.note_id.title} ({self.role})"
    
class Subscription(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='subscriptions')
    topic_root = models.ForeignKey(to=Notes, on_delete=models.CASCADE, related_name='subscriptions')


'''
Теги должны быть раз. 
Задаём тип тега, и в поле значения информацию о схеме, таблице, и ключе.
(Например, когда нам нужно подключить таблицу. Нам нужно задать комбинацию: схема, таблица, id записи в таблице) 
Дальше возможно пары вариантов:
* мы собираем нуные теги по типу в нужном типе ищем нужную таблицу.
* можно сделать тег адрес, который будет содержать все три значения через разделитель
В обоих случаях мы заранее знаем что у нас должно быть несколько чётко определенное количество информации,
Иначе данная запись бессмыслена. 

Обкатать это можно на тегах к ключевым заметкам.
Мы создаём ключ, который привязывает данные к заметке её ключу. 
Один ключ к тегу, другой к заметке. 
Таблица тегов содрежит с называния тегов и их типы. 
'''

'''
class TagsCategory(models.TextChoices):
    tech = "Техническая" # Ссылка на документы из бугалтерского оборота.
    priority = "Приоритеты" # Технические элементы для CRM
    other = "Теги" # Теги в смысле тегов

class Tags(BasicModelTemplate):
    tag = models.CharField(unique=True)
    category = models.CharField(choices=TagsCategory.choices, default='Теги')

class NotesTagsConnection(BasicModelTemplate):
    note = models.ForeignKey(Notes, on_delete=models.CASCADE) # К какой заметке относятся тэги
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)


    class Meta:
        verbose_name = "tags connection"
        verbose_name_plural = "tags connections"

'''
