# Generated by Django 4.2.3 on 2024-11-12 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0011_alter_buyingbill_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinbill',
            name='bill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='ecommerce_API.buyingbill'),
        ),
    ]
