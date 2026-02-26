# GameSettings: disable /transfer (transfer menu)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_user_two_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesettings',
            name='disable_bot_transfer',
            field=models.BooleanField(default=False, help_text='When enabled, the bot will not process transfer (button, /transfer, or cached menu).'),
        ),
    ]
