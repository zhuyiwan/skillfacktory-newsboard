from django import forms
from .models import Notes, NoteStructureModel, CategoryType

class NotesForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=CategoryType.choices,
        required=True,
        label='Категория',
        initial=CategoryType.TOPIC
    )

    class Meta:
        model = Notes
        fields = [
            'title',
            'content',
            'category',
        ]

class TopicTaskForm(forms.Form):
    category = forms.ChoiceField(
        choices=CategoryType.choices,
        required=True,
        label='',
        initial=CategoryType.TOPIC
    )