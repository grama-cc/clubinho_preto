# Generated by Django 3.2.8 on 2022-02-15 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_auto_20211210_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='kids_gender',
            field=models.CharField(blank=True, choices=[('MA', 'Masculino'), ('FE', 'Feminino'), ('NO', 'Prefiro não responder')], default='NO', max_length=2, null=True, verbose_name='sexo da criança'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='kids_race',
            field=models.CharField(blank=True, choices=[('WH', 'Branca'), ('PA', 'Parda'), ('BL', 'Preta'), ('YE', 'Amarela'), ('NA', 'Indígena'), ('BN', 'Preta e Indígena')], default='BL', max_length=2, null=True, verbose_name='Cor da criança'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='relatedness',
            field=models.CharField(blank=True, choices=[('PA', 'Mãe/Pai'), ('GR', 'Avôou Avó'), ('ST', 'Madrasta ou Padrasto'), ('AU', 'Tia ou Tio'), ('BR', 'Irmão ou Irmã'), ('TE', 'Professor(a)'), ('OT', 'Outro')], default='PA', max_length=2, null=True, verbose_name='parentesco'),
        ),
        migrations.AlterField(
            model_name='subscriber',
            name='subscribing_date',
            field=models.DateTimeField(null=True, verbose_name='Data de inscrição'),
        ),
    ]
