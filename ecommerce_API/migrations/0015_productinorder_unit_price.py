# Generated by Django 4.2.3 on 2024-11-14 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0014_alter_contact_etat'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinorder',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
    ]
