from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_merge_20260716_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositrequest',
            name='transaction_reference',
            field=models.CharField(
                blank=True,
                help_text='CBE/Telebirr transaction id when manually approved (prevents reuse)',
                max_length=128,
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name='depositrequest',
            index=models.Index(fields=['transaction_reference'], name='deposit_req_transac_0a1b2c_idx'),
        ),
    ]
