# Generated by Django 4.2.8 on 2023-12-16 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CreditApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]