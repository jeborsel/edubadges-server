# Generated by Django 2.2.9 on 2020-03-26 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0015_auto_20200326_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
