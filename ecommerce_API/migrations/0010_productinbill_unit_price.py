# Generated by Django 4.2.3 on 2024-11-12 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0009_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinbill',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
