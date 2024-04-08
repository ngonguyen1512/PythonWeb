# Generated by Django 5.0.1 on 2024-01-25 08:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('phone', models.IntegerField(null=True)),
                ('email', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=255, null=True)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('phone', models.IntegerField(null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('ship', models.IntegerField(null=True)),
                ('total', models.IntegerField(null=True)),
                ('accept_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_accepted', to='app.account')),
                ('account_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_accounted', to='app.account')),
                ('ship_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders_shipped', to='app.account')),
                ('state_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='permission_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.permission'),
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('category_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.category')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('name', models.CharField(max_length=255, null=True)),
                ('discount', models.IntegerField(blank=True, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('infor', models.CharField(blank=True, max_length=255, null=True)),
                ('category_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.category')),
                ('sample_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.sample')),
                ('state_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state')),
            ],
        ),
        migrations.CreateModel(
            name='OrderDetail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('price', models.IntegerField(blank=True, null=True)),
                ('discount', models.IntegerField(blank=True, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('color_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.color')),
                ('order_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.order')),
                ('product_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product')),
                ('size_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.size')),
            ],
        ),
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=0, null=True)),
                ('color_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.color')),
                ('product_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product')),
                ('size_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.size')),
                ('state_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state')),
            ],
        ),
        migrations.AddField(
            model_name='permission',
            name='state_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state'),
        ),
        migrations.AddField(
            model_name='account',
            name='state_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.state'),
        ),
    ]