from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0033_alter_gamesettings_deposit_bonus_percent'),
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
