# Generated by Django 3.2.6 on 2021-12-03 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('box', '0004_remove_shipping_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='box',
            name='height',
            field=models.FloatField(null=True, verbose_name='Altura (cm)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='length',
            field=models.FloatField(null=True, verbose_name='Comprimento (cm)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='weight',
            field=models.FloatField(null=True, verbose_name='Peso (kg)'),
        ),
        migrations.AlterField(
            model_name='box',
            name='width',
            field=models.FloatField(null=True, verbose_name='Largura (cm)'),
        ),
    ]