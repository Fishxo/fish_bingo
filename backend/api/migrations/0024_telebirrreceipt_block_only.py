# TelebirrReceipt: allow user=null and amount=0 for block-only entries

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_cbereceipt_block_only'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telebirrreceipt',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telebirr_receipts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='telebirrreceipt',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[MinValueValidator(0)]),
        ),
    ]
