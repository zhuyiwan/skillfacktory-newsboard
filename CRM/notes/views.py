from typing import Any
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, CreateView, View, UpdateView
from django.urls import reverse_lazy

from .forms import NotesForm, TopicTaskForm
from .models import Notes, NoteStructureModel, Subscription


class NotesListView(LoginRequiredMixin, ListView):
    # permission_required = ()
    model = Notes
    ordering ='created_at'
    template_name = 'notes/notes_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        category = self.request.GET.get('category')
        if not category:
            category = "topic"
        queryset = Notes.objects.filter(note_structure_current__category=category)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TopicTaskForm(self.request.GET or None)
        return context

class NoteDetailsView(DetailView):
    model = Notes
    template_name = 'notes/notes_details.html'
    context_object_name = "note"

    # Нам нужно выводить только коментарии которые ссылаются непосредственно на эту статью.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = 'name'
        return context


class NoteCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('notes.add_note',)
    model = Notes
    form_class = NotesForm
    context_object_name = 'note'
    template_name = 'notes/notes_edit.html'

    def get_success_url(self):
        return reverse_lazy('note_detals', kwargs = {'pk': self.object.pk})
    
    def form_valid(self, form):
        with transaction.atomic():
            note = form.save(commit=False)
            note.created_by = self.request.user.profiles
            note.save()

            note_structure = NoteStructureModel(
                root_note=note,
                parent_note=note,
                current_note=note,
                category=form.cleaned_data['category']
            )
            note_structure.save()
        return redirect(note.get_absolute_url())


class NoteUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('notes.change_note',)
    model = Notes
    form_class = NotesForm
    context_object_name = 'note'
    template_name = 'notes/notes_edit.html'

    def get_initial(self):
        initial = super().get_initial()
        note = self.get_object()
        note_structure = NoteStructureModel.objects.get(current_note=note)
        initial['category'] = note_structure.category
        return initial

    def get_success_url(self):
        return reverse_lazy('note_detals', kwargs = {'pk': self.object.pk})
    
    def form_valid(self, form):
        with transaction.atomic():
            note = form.save()
            notes_structure = NoteStructureModel.objects.get(current_note=note)
            notes_structure.category = form.cleaned_data['category']
            notes_structure.save()
        return super().form_valid(form)
    

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        note = Notes.objects.get(id=topic_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, topic_root=topic_id)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                topic_root=topic_id,
            )

    notes_with_subscription = Notes.objects.annotate(
        user_subscribed = Exists(
            Subscription.objects.filter(urser=request.user, topic_root=OuterRef('pk'))
        )
    ).order_by('name')
    return render(request, 'subscription.html', {'notes': notes_with_subscription})