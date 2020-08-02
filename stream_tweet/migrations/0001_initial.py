# Generated by Django 2.2.12 on 2020-06-23 07:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hashtag', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TweetsModel',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('id_isu', models.CharField(max_length=50, null=True)),
                ('user', models.CharField(max_length=100)),
                ('user_id', models.CharField(max_length=100)),
                ('teks', models.TextField(max_length=280)),
                ('reply_count', models.IntegerField(blank=True, null=True)),
                ('retweet_count', models.IntegerField(blank=True, null=True)),
                ('like_count', models.IntegerField(blank=True, null=True)),
                ('waktu', models.DateTimeField(default=datetime.datetime.now)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('tags', models.ManyToManyField(to='stream_tweet.Hashtag')),
            ],
        ),
    ]
