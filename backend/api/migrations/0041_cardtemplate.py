from django.db import migrations, models


def seed_card_templates(apps, schema_editor):
    """Generate permanent layouts for card numbers 1..total_cards (once)."""
    CardTemplate = apps.get_model('api', 'CardTemplate')
    GameSettings = apps.get_model('api', 'GameSettings')

    total = 100
    try:
        settings = GameSettings.objects.first()
        if settings and getattr(settings, 'total_cards', None):
            total = int(settings.total_cards) or 100
    except Exception:
        total = 100

    import random

    def generate_layout():
        card = {
            'B': random.sample(range(1, 16), 5),
            'I': random.sample(range(16, 31), 5),
            'N': random.sample(range(31, 46), 4),
            'G': random.sample(range(46, 61), 5),
            'O': random.sample(range(61, 76), 5),
        }
        layout = []
        for row in range(5):
            layout_row = []
            for col_idx, letter in enumerate(['B', 'I', 'N', 'G', 'O']):
                if letter == 'N' and row == 2 and col_idx == 2:
                    layout_row.append({
                        'number': None,
                        'letter': 'FREE',
                        'marked': True,
                        'row': row,
                        'col': col_idx,
                    })
                else:
                    if letter == 'N':
                        num_idx = row if row < 2 else row - 1
                        number = card[letter][num_idx]
                    else:
                        number = card[letter][row]
                    layout_row.append({
                        'number': number,
                        'letter': letter,
                        'marked': False,
                        'row': row,
                        'col': col_idx,
                    })
            layout.append(layout_row)
        return layout

    existing = set(CardTemplate.objects.values_list('card_number', flat=True))
    to_create = []
    for n in range(1, total + 1):
        if n not in existing:
            to_create.append(CardTemplate(card_number=n, layout=generate_layout()))
    if to_create:
        CardTemplate.objects.bulk_create(to_create, batch_size=100)


def unseed_card_templates(apps, schema_editor):
    CardTemplate = apps.get_model('api', 'CardTemplate')
    CardTemplate.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_depositrequest_transaction_reference'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.PositiveIntegerField(db_index=True, unique=True)),
                ('layout', models.JSONField(help_text='5x5 grid layout with numbers (unmarked template)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'card_templates',
                'ordering': ['card_number'],
            },
        ),
        migrations.RunPython(seed_card_templates, unseed_card_templates),
    ]
