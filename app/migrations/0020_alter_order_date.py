# Generated by Django 5.0.1 on 2024-02-20 06:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_remove_order_accept_remove_order_ship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]