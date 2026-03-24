# Sync deposit_bonus_percent help_text with GameSettings model (%% escaping in help text)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_win_stats_and_game_snapshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesettings',
            name='deposit_bonus_percent',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Percent of deposit to add to unwithdrawable (e.g. 10 = 10%% of deposit also added as bonus). 0 = no bonus.',
            ),
        ),
    ]
