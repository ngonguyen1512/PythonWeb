# Generated by Django 5.0.1 on 2024-02-20 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_sample_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='complete',
        ),
    ]
