# Generated by Django 2.2.12 on 2020-11-03 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stream_tweet', '0011_hashtag_jumlah'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hashtag',
            name='jumlah',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
