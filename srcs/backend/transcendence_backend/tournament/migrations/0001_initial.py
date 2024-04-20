# Generated by Django 5.0.3 on 2024-04-20 16:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pong', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(default='let the games begin')),
                ('max_players', models.IntegerField(default=20)),
                ('max_points', models.IntegerField(default=10)),
                ('status', models.CharField(default='open', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('games', models.ManyToManyField(related_name='games', to='pong.pong')),
                ('players', models.ManyToManyField(related_name='players', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
