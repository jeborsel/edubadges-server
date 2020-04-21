# Generated by Django 2.2.9 on 2020-04-21 09:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issuer', '0067_badgeclass_expiration_period'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgeinstance',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
