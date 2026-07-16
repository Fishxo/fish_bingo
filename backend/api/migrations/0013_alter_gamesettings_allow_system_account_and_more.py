from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_gamesettings_system_accounts_max_100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesettings',
            name='allow_system_account',
            field=models.BooleanField(
                default=True,
                help_text='Enable fake system accounts to join games',
            ),
        ),
    ]
