# Generated by Django 4.2.3 on 2024-11-14 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_API', '0018_alter_buyingbill_fournisseur'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='fournisseur',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
