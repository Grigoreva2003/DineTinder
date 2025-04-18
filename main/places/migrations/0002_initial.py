# Generated by Django 5.1.7 on 2025-04-04 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('places', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiningPlace',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('photo_link', models.URLField(blank=True)),
                ('address', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=255)),
                ('rating', models.FloatField(default=0.0)),
            ],
            options={
                'db_table': 'dining_places',
                'managed': False,
            },
        ),
    ]
