# Generated by Django 4.2.3 on 2024-11-14 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0015_productinorder_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinorder',
            name='unit_price',
            field=models.DecimalField(blank=True, decimal_places=2, default='0.00', max_digits=10, null=True),
        ),
    ]
