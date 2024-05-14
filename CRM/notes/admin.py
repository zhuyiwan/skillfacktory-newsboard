from django.contrib import admin
from .models import Notes, NoteStructureModel
# Register your models here.

class NoteStructureModelInLine(admin.TabularInline):
    model = NoteStructureModel
    fk_name = 'current_note' 
    extra = 0

@admin.register(Notes)
class NotesAdmin(admin.ModelAdmin):
    # list_display = ('')
    inlines = [
        NoteStructureModelInLine,
    ]