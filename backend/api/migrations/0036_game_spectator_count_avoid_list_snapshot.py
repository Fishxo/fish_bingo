# Generated manually for spectator count and avoid-list snapshot

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_user_abuse_flags_and_settings_toggle'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='spectator_count',
            field=models.PositiveIntegerField(default=0, help_text='Current spectators (watching without a card); updated from live connections + periodic sync.'),
        ),
        migrations.AddField(
            model_name='game',
            name='avoid_list_numbers',
            field=models.JSONField(blank=True, default=list, help_text='Snapshot of anti-abuse avoid-list numbers for this game (when prepared).'),
        ),
    ]
