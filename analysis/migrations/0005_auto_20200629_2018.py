# Generated by Django 2.2.12 on 2020-06-29 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0004_auto_20200629_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysistweet',
            name='id_isu',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
