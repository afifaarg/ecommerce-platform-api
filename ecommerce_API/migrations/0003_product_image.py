# Generated by Django 4.2.3 on 2024-10-13 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0002_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(default=1, upload_to='produit_images/'),
            preserve_default=False,
        ),
    ]