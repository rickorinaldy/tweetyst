import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django_pandas.io import read_frame
from stream_tweet.models import TweetsModel, Hashtag


def download_data(request, id, nama, bulan1, bulan2, tahun):
    bulan_list = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
    'juli', 'agustus', 'september', 'oktober', 'november', 'desember']

    if nama!='all':
        tweet_tag = TweetsModel.objects.filter(
                        id_isu=id,
                        tags__hashtag=nama,
                        waktu__year=tahun,
                        waktu__month__gte=bulan1,
                        waktu__month__lte=bulan2)
        namafile = f'{nama} {bulan_list[bulan1-1]}-{bulan_list[bulan2-1]} {tahun}'

    else:
        tweet_tag = TweetsModel.objects.filter(id_isu=id)
        namafile = f'{id}'

    df = read_frame(tweet_tag.all())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={namafile}.csv'
    df.to_csv(path_or_buf=response, sep=';', index=False, decimal=".")

    return response


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
    return render(request, 'show.html', {'data':zip(tweet_tag,hashtag_list), 'r':[id,nama,bulan1,bulan2,tahun]})
