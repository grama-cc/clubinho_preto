# Generated by Django 3.2.6 on 2021-12-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('box', '0005_auto_20211203_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='box',
            name='height',
            field=models.FloatField(default=5.0, verbose_name='Altura (cm)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='length',
            field=models.FloatField(default=35.0, verbose_name='Comprimento (cm)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='weight',
            field=models.FloatField(default=1.0, verbose_name='Peso (kg)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='width',
            field=models.FloatField(default=23.0, verbose_name='Largura (cm)'),
        ),
    ]