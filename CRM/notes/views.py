from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Notes


class NotesListView(ListView):
    model = Notes
    ordering ='created_at'
    template_name = 'notes/notes_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        # queryset = Notes.objects.filter(category="Блок")
        queryset = Notes.objects.filter(note_structure_current__category="Проект")
        return queryset
    
class NoteDetailsView(DetailView):
    model = Notes
    template_name = 'notes/notes_details.html' 
    context_object_name = "note"
    
    # Нам нужно выводить только коментарии которые ссылаются непосредственно на эту статью.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'name' 
        return context
    