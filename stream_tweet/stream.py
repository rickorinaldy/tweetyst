from pytz import timezone
from home.models import IsuTweet
from geopy.geocoders import Nominatim
from background_task import background
from geopy.exc import GeocoderTimedOut
from datetime import datetime, timedelta
from .models import TweetsModel, Hashtag
import tweepy, sys, time, re, pandas as pd
from collections import Counter


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, batch_time):
        self.start_time = time.time()
        self.limit = float(batch_time)
        self.non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        self.data = {'id':[], 'user':[], 'user_id':[], 'reply':[], 'retweet':[],
                    'like':[], 'waktu':[], 'teks':[], 'lokasi':[]}
        super(MyStreamListener, self).__init__()

    def on_status(self, status):
        if (time.time() - self.start_time) < self.limit:
            self.data['id'].append(status.id_str)
            self.data['user'].append(status.user.name)
            self.data['user_id'].append(status.user.screen_name)
            self.data['reply'].append(status.reply_count)
            self.data['retweet'].append(status.retweet_count)
            self.data['like'].append(status.favorite_count)

            ts = timezone('UTC').localize(status.created_at)
            self.data['waktu'].append(ts.astimezone(timezone('Asia/Jakarta')))

            try:
                self.data['teks'].append(status.extended_tweet['full_text'].translate(self.non_bmp_map))
            except:
                self.data['teks'].append(status.text.translate(self.non_bmp_map))

            try:
                self.data['lokasi'].append(status.place.bounding_box.coordinates[0][0])
            except:
                self.data['lokasi'].append(None)

            return True

        else:
            return False

    def on_error(self, status_code):
        if status_code == 420:
            return False


def geocoding(koordinat):
    locator = Nominatim(user_agent="myGeocoder")
    try:
        try:
            return locator.reverse(koordinat).raw['address']['state']
        except:
            return locator.reverse(koordinat).raw['address']['city']
    except GeocoderTimedOut:
        return geocoding(koordinat)


def simpan_data(data, id):
    hashtags = []
    for i in range(len(data['id'])):
        try:
            loc = geocoding(f"{data['lokasi'][i][1]}, {data['lokasi'][i][0]}")
            lat, lon = data['lokasi'][i][1], data['lokasi'][i][0]

        except:
            lat = lon = loc = None

        s = TweetsModel(
                id_tweet      = data['id'][i],
                id_isu        = id,
                user          = data['user'][i],
                user_id       = data['user_id'][i],
                reply_count   = data['reply'][i],
                retweet_count = data['retweet'][i],
                like_count    = data['like'][i],
                waktu         = data['waktu'][i],
                teks          = data['teks'][i],
                latitude      = lat,
                longitude     = lon,
                lokasi        = loc)

        s.save()
        hashtag_list = re.findall(r"(#[\w\d]+)", s.teks)
        hashtags += hashtag_list
        if len(hashtag_list)>0:
            for tag in hashtag_list:
                try:
                    h = Hashtag.objects.get(hashtag=tag)
                except:
                    h = Hashtag.objects.create(hashtag=tag)
                s.tags.add(h)

    akumulasi = Counter(hashtags)
    if len(akumulasi.values())>0:
        Hashtag.objects.all().update(jumlah=0)
        for tag in akumulasi.keys():
            h = Hashtag.objects.get(hashtag=tag)
            h.jumlah = akumulasi[tag]
            h.save()



@background()
def onlinestream(id):
    print('Sedang berjalan..')

    access_token        = "378898712-alwN8aEvT6j84qqx3ti4AW0xjSxfJe6IDWlGsa3S"
    access_token_secret =      "qTRi2JF1AI5GTgOizH3PSjBxg6PVNInUCaXB24j30Ykm5"
    consumer_key        =                          "d2pJN0kQUgpFFMWOPKS4VBGhr"
    consumer_secret     = "BhBOHMxLhM0vqqXTse4v0FtmmMmxP67JcVUolBZi3A2kf5JaQk"

    while len(IsuTweet.objects.filter(id_ref=id))!=0:
        myStreamListener    = MyStreamListener(batch_time=5)

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)
        myStream = tweepy.Stream(api.auth, myStreamListener)

        myStream.filter(track=IsuTweet.objects.get(id_ref=id).keyword.split(' OR '), languages=['in'])
        simpan_data(myStreamListener.data, id)

    print('Stream berhenti')


@background()
def filestream(namafile, id):
    data = pd.read_excel(f'data\{namafile}', index_col=0)
    mulai = time.time()
    hashtags = []

    print('Menyimpan data..')
    for i in range(len(data)):
        if len(IsuTweet.objects.filter(id_ref=id))==0:break

        try:
            TweetsModel.objects.get(id_tweet=data['tweetID'][i])
            mulai = time.time()

        except:
            try: loc = geocoding(f"{data['lat'][i]}, {data['lon'][i]}")
            except: loc = None

            t = str(data['tweet'][i]).translate(dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd))
            t = re.sub(r'\\n', ' ', t)
            t = re.sub(r'\\"', "'", t)

            s = TweetsModel(
                    id_tweet      = data['tweetID'][i],
                    id_isu        = id,
                    user          = data['name'][i],
                    user_id       = data['screen_name'][i],
                    reply_count   = data['nreplies'][i],
                    retweet_count = data['nretweets'][i],
                    like_count    = data['nlikes'][i],
                    waktu         = timezone('UTC').localize(data['created_at'][i]).astimezone(timezone('Asia/Jakarta')),
                    teks          = t,
                    latitude      = data['lat'][i],
                    longitude     = data['lon'][i],
                    lokasi        = loc)

            try:
                s.save()
                hashtag_list = re.findall(r"(#[\w\d]+)", s.teks)
                hashtags += hashtag_list
                if len(hashtag_list)>0:
                    for tag in hashtag_list:
                        try: h = Hashtag.objects.get(hashtag=tag)
                        except: h = Hashtag.objects.create(hashtag=tag)
                        s.tags.add(h)

                if (time.time()-mulai)>60:
                    akumulasi = Counter(hashtags)
                    if len(akumulasi.values())>0:
                        Hashtag.objects.all().update(jumlah=0)
                        for tag in akumulasi.keys():
                            h = Hashtag.objects.get(hashtag=tag)
                            h.jumlah = akumulasi[tag]
                            h.save()
                        hashtags = []

                    mulai = time.time()

            except:continue

    print('Berhasil disimpan')
