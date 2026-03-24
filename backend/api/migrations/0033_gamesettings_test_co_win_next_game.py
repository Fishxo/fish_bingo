from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0032_win_stats_and_game_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesettings',
            name='test_co_win_next_game',
            field=models.BooleanField(
                default=False,
                help_text='If True, the next game that starts will run in test co-win mode (admin QA: same last call, banner shows both, payout real-only).',
            ),
        ),
    ]
