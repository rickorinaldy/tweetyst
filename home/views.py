from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from stream_tweet.models import TweetsModel, Hashtag
from .models import IsuTweet
from stream_tweet import stream
from django.db.models import Count


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


def detail(request, id):
    tweet_id = TweetsModel.objects.filter(id_isu=id).exclude(tags=None)
    hashtag_list = [[h['tags__hashtag'], h['tags__hashtag__count']] for h in tweet_id.values('tags__hashtag').annotate(Count('tags__hashtag')).order_by('-tags__hashtag__count') if h['tags__hashtag']!=None]
    tweet_like = tweet_id.order_by('-like_count')
    tweet_retweet = tweet_id.order_by('-retweet_count')
    tweet_reply = tweet_id.order_by('-reply_count')
    konteks = { 'hashtag_list':hashtag_list,
                'tweet_list':list(zip(
                        zip(tweet_like[:5], tweet_like.values('tags__hashtag')[:5]),
                        zip(tweet_retweet[:5], tweet_retweet.values('tags__hashtag')[:5]),
                        zip(tweet_reply[:5], tweet_reply.values('tags__hashtag')[:5])
                        )),
                'isu':IsuTweet.objects.get(id_ref=id),
                'tweet':tweet_id.order_by('-waktu')}
    return render(request, 'home/detail.html', konteks)
