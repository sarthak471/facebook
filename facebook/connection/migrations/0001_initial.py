# Generated by Django 3.2.11 on 2024-01-02 22:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend_status', models.BooleanField(default=False)),
                ('request_status', models.BooleanField(default=True)),
                ('reject_status', models.BooleanField(default=False)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_sent', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendship_requests_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('from_user', 'to_user')},
            },
        ),
    ]
