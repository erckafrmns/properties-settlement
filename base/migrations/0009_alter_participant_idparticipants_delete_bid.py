# Generated by Django 4.2.2 on 2023-12-08 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_bid_items_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='IDParticipants',
            field=models.CharField(default='none', max_length=1000, unique=True),
        ),
        migrations.DeleteModel(
            name='Bid',
        ),
    ]
