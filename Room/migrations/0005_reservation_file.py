# Generated by Django 4.2.1 on 2023-05-17 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Room', '0004_alter_reservation_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='file',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
