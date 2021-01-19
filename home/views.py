from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from stream_tweet.models import TweetsModel, Hashtag
from .models import IsuTweet
from stream_tweet import stream
from django.db.models import Count
from sklearn.ensemble import IsolationForest
import numpy as np

class HomeView(ListView):
    model = IsuTweet
    template_name = "home/home.html"
    context_object_name = "isu_list"
    ordering = ['-tanggal_buat']
    paginate_by = 5


def manage(request):
    return render(request, 'home/manage.html', {'isu_list':IsuTweet.objects.all()})


def update(request, id):
    if request.method == 'POST':
        IsuTweet.objects.filter(id_ref=id).update(
            judul       = request.POST["judul"],
            deskripsi   = request.POST["deskripsi"],
            keyword     = request.POST["keyword"]
            )
        return HttpResponseRedirect('/home/manage')
    else:
        return render(request, 'home/update.html', {'isu':IsuTweet.objects.get(id_ref=id)})


def delete(request, id):
    if request.method == 'POST':
        if id in request.POST:
            IsuTweet.objects.get(id_ref=id).delete()
            TweetsModel.objects.filter(id_isu=id).delete()
        return HttpResponseRedirect('/home/manage')
    else:
        return render(request, 'home/delete_confirmation.html', {'isu':IsuTweet.objects.get(id_ref=id)})

def std_outlier(data, threshold=2):
    mean = np.mean(data)
    std = np.std(data)
    return mean+(threshold*std), mean-(threshold*std)

def detail(request, id):
    tweet_id = TweetsModel.objects.filter(id_isu=id).exclude(tags=None)
    hashtag_list = [[h['tags__hashtag'], Hashtag.objects.get(hashtag=h['tags__hashtag']).jumlah, h['tags__hashtag__count']] for h in tweet_id.values('tags__hashtag').annotate(Count('tags__hashtag')).order_by('-tags__hashtag__count') if h['tags__hashtag']!=None]
    zipHashList = list(zip(*hashtag_list))
    appearance = np.array(zipHashList[1])
    batas = std_outlier(appearance[appearance>0])
    print(batas)
    hashtag_list = list(zip(zipHashList[0], zipHashList[1], zipHashList[2], [1 if (i>batas[0] or i<batas[1] and i!=0) else 0 for i in zipHashList[1]]))
    tweet_like = tweet_id.order_by('-like_count')
    tweet_retweet = tweet_id.order_by('-retweet_count')
    tweet_reply = tweet_id.order_by('-reply_count')
    mul = [[i.like_count, i.retweet_count] for i in tweet_id]
    iso = IsolationForest(random_state=27).fit_predict(mul)
    outlierId = [tweet_id[i].id_tweet for i in range(len(tweet_id)) if iso[i]==1]

    konteks = { 'hashtag_list':hashtag_list,
                'tweet_list':list(zip(
                        zip(tweet_like[:5], tweet_like.values('tags__hashtag')[:5]),
                        zip(tweet_retweet[:5], tweet_retweet.values('tags__hashtag')[:5]),
                        zip(tweet_reply[:5], tweet_reply.values('tags__hashtag')[:5])
                        )),
                'outlier':outlierId,
                'isu':IsuTweet.objects.get(id_ref=id),
                'tweet':tweet_id.order_by('-waktu')}

    return render(request, 'home/detail.html', konteks)
