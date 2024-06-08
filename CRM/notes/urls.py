from django.urls import path
from .views import NotesListView, NoteDetailsView, NoteCreateView, NoteUpdateView, subscriptions

urlpatterns = [
    path('', NotesListView.as_view(), name='main_page'),
    path('note/create', NoteCreateView.as_view(), name='note_create'),
    path('note/<str:pk>', NoteDetailsView.as_view(), name='note_detals'),
    path('note/<str:pk>/edit', NoteUpdateView.as_view(), name='note_update'),
    path('subscriptions/', subscriptions, name='subscriptions'), 
]