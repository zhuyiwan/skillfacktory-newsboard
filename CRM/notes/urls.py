from django.urls import path
from .views import NotesListView, NoteDetailsView

urlpatterns = [
    path('', NotesListView.as_view(), name='main_page'),
    path('note/<str:pk>', NoteDetailsView.as_view(), name='note_detals'),
]