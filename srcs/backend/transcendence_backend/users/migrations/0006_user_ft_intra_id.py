# Generated by Django 5.0.3 on 2024-03-07 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_is_user_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ft_intra_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]