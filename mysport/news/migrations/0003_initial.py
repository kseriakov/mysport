# Generated by Django 4.0.5 on 2022-06-26 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('news', '0002_delete_news'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Контент')),
                ('url', models.URLField(unique=True, verbose_name='URL')),
                ('time_add', models.DateTimeField(auto_now_add=True, verbose_name='Время публикации')),
            ],
            options={
                'verbose_name': 'Новости',
                'verbose_name_plural': 'Новости',
                'ordering': ['-time_add'],
            },
        ),
    ]
