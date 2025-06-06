# Generated by Django 5.2.1 on 2025-05-26 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0004_offers_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='offers',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='offers',
            name='status',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offers',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
