# Generated by Django 4.2.11 on 2024-05-02 07:00

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0002_notesreaction_notes_unique_note_profile_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notesreaction',
            options={'verbose_name': 'note reaction', 'verbose_name_plural': 'note reactions'},
        ),
        migrations.RemoveConstraint(
            model_name='notes',
            name='unique_note_profile',
        ),
        migrations.AddField(
            model_name='notesreaction',
            name='note_id',
            field=models.ForeignKey(default=datetime.datetime(2024, 5, 2, 7, 0, 17, 290515, tzinfo=datetime.timezone.utc), on_delete=django.db.models.deletion.DO_NOTHING, related_name='notereactions_to_note', to='notes.notes'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='notesreaction',
            name='profile_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='notereactions_to_profile', to='notes.profiles'),
        ),
        migrations.AddConstraint(
            model_name='notesreaction',
            constraint=models.UniqueConstraint(fields=('note', 'profile_id'), name='unique_note_profile'),
        ),
    ]
