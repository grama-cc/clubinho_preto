# Generated by Django 3.2.6 on 2021-10-07 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20211007_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='asaas_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
