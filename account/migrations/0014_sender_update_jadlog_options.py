# Generated by Django 3.2.6 on 2022-02-18 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20220215_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='sender',
            name='update_jadlog_options',
            field=models.BooleanField(default=False, verbose_name='Atualizar opções Jadlog?'),
        ),
    ]