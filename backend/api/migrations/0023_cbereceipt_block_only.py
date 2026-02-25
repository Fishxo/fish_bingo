# CbeReceipt: allow user=null and amount=0 for block-only entries (manually added refs)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_gamesettings_instruction_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbereceipt',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cbe_receipts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cbereceipt',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[MinValueValidator(0)]),
        ),
    ]
