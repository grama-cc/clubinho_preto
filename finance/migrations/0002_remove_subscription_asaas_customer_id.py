# Generated by Django 3.2.8 on 2021-10-29 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='asaas_customer_id',
        ),
    ]
