from django.db import models
import datetime


class TweetsModel(models.Model):
    id_tweet        = models.CharField(primary_key=True, max_length=50)
    id_isu          = models.CharField(max_length=50, null=True)
    user            = models.CharField(max_length=50)
    user_id         = models.CharField(max_length=50)
    teks            = models.TextField(max_length=280)
    reply_count     = models.IntegerField(blank=True, null=True)
    retweet_count   = models.IntegerField(blank=True, null=True)
    like_count      = models.IntegerField(blank=True, null=True)
    waktu           = models.DateTimeField(default=datetime.datetime.now)
    latitude        = models.FloatField(null=True, blank=True, default=None)
    longitude       = models.FloatField(null=True, blank=True, default=None)
    lokasi          = models.CharField(max_length=30, null=True)
    tags            = models.ManyToManyField('Hashtag')

    def __str__(self):
        return f"{self.user_id} at {self.waktu + datetime.timedelta(hours=7)}"


class Hashtag(models.Model):
    hashtag         = models.CharField(max_length=100, blank=True)
    jumlah          = models.IntegerField(null=True)

    def __str__(self):
        return self.hashtag
