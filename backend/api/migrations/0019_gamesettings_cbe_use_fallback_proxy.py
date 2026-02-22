# CBE verification: use fallback proxy when server is outside Ethiopia (e.g. AWS)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_merge_0017_aggregate_and_failed_deposit'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesettings',
            name='cbe_use_fallback_proxy',
            field=models.BooleanField(
                default=False,
                help_text='If server is outside Ethiopia: ask verify API to use fallback proxy for CBE (skipPrimaryVerification)'
            ),
        ),
    ]
