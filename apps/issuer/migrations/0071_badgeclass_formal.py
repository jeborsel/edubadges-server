# Generated by Django 2.2.13 on 2020-07-28 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0070_auto_20200630_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgeclass',
            name='formal',
            field=models.BooleanField(default=None, null=True),
        ),
    ]