# Generated by Django 2.2.13 on 2020-08-20 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('badgeuser', '0069_auto_20200820_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='termsagreement',
            name='agreed_language',
        ),
    ]
