from django.db import migrations, models


def copy_bid_amount_to_registration_gift(apps, schema_editor):
    """Preserve current gift size: it used to equal bid_amount."""
    GameSettings = apps.get_model('api', 'GameSettings')
    for settings in GameSettings.objects.all():
        settings.registration_gift_amount = settings.bid_amount
        settings.save(update_fields=['registration_gift_amount'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0041_cardtemplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesettings',
            name='registration_gift_amount',
            field=models.DecimalField(
                decimal_places=2,
                default=10.00,
                help_text='Amount credited to unwithdrawable on first registration when give_register_reward is True. Independent of bid_amount.',
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name='gamesettings',
            name='give_register_reward',
            field=models.BooleanField(
                default=True,
                help_text='If True, new users get registration_gift_amount as registration bonus (unwithdrawable). If False, no bonus, balance stays 0.',
            ),
        ),
        migrations.RunPython(copy_bid_amount_to_registration_gift, migrations.RunPython.noop),
    ]
