# Generated by Django 4.0.5 on 2022-06-25 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0004_workout_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workout',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
