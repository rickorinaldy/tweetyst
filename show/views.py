from django.shortcuts import render
from stream_tweet.models import TweetsModel, Hashtag
# Create your views here.
def show_data(request, id, nama, bulan1, bulan2, tahun):
    if nama!='all':
        if bulan1!=0:
            tweet_tag = TweetsModel.objects.filter(
                            id_isu=id,
                            tags__hashtag=nama,
                            waktu__year=tahun,
                            waktu__month__gte=bulan1,
                            waktu__month__lte=bulan2)
        else:
            tweet_tag = TweetsModel.objects.filter(id_isu=id,tags__hashtag=nama)

    else:
        tweet_tag = TweetsModel.objects.filter(id_isu=id)

    hashtag_list = [', '.join([j.hashtag for j in t.tags.all()]) for t in tweet_tag]
    return render(request, 'show.html', {'data':zip(tweet_tag,hashtag_list)})
