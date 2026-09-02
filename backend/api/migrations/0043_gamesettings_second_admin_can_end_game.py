from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_gamesettings_registration_gift_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesettings',
            name='second_admin_can_end_game',
            field=models.BooleanField(
                default=False,
                help_text='When enabled, second admin dashboard shows End / Force end for active stuck games.',
            ),
        ),
    ]
