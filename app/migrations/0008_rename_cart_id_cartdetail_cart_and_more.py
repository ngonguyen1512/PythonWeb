# Generated by Django 5.0.1 on 2024-02-03 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_cartdetail_order_id_cartdetail_cart_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartdetail',
            old_name='cart_id',
            new_name='cart',
        ),
        migrations.RenameField(
            model_name='cartdetail',
            old_name='product_id',
            new_name='product',
        ),
    ]