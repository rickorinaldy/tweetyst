# Generated by Django 2.2.12 on 2020-06-23 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stream_tweet', '0002_auto_20200623_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweetsmodel',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tweetsmodel',
            name='user',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='tweetsmodel',
            name='user_id',
            field=models.CharField(max_length=50),
        ),
    ]
