# Generated by Django 2.2.12 on 2020-06-23 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20200623_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='isutweet',
            name='deskripsi',
            field=models.TextField(blank=True),
        ),
    ]
