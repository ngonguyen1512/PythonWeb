# Generated by Django 5.0.1 on 2024-02-18 04:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state'),
        ),
    ]
