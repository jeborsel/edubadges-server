# Generated by Django 2.2.9 on 2020-03-13 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backpack', '0012_remove_backpackcollection_entity_version'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backpackcollection',
            name='slug',
        ),
    ]
