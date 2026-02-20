# Merge migration: resolves conflict between 0013_alter_gamesettings_allow_system_account_and_more
# and 0013_telebirr_receipt_and_api_key (multiple leaf nodes).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_gamesettings_allow_system_account_and_more'),
        ('api', '0013_telebirr_receipt_and_api_key'),
    ]

    operations = []
