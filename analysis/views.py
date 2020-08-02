from django.shortcuts import render
from stream_tweet.models import TweetsModel, Hashtag
from django.db.models import Count
from django.http import HttpResponseRedirect
import folium
from folium.plugins import MarkerCluster

def analyst(request, id, nama, **kwargs):
    bulan_list = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
    'juli', 'agustus', 'september', 'oktober', 'november', 'desember']

    if request.method == 'POST':
        bulan1 = bulan_list.index(request.POST['bulan1'].lower())+1
        bulan2 = bulan_list.index(request.POST['bulan2'].lower())+1
        tahun = request.POST['tahun']
        return HttpResponseRedirect(f'/analysis/{id}/%23{nama[1:]}/{bulan1}/{bulan2}/{tahun}')

    tweet_tag    = TweetsModel.objects.filter(id_isu=id, tags__hashtag=nama)

    b = tweet_tag.dates('waktu','month')
    if kwargs['bulan1']!=0:
        tahun = kwargs['tahun']
        bulan1 = kwargs['bulan1']
        if bulan1 <= kwargs['bulan2']:
            bulan2 = kwargs['bulan2']
            tweet_tag = tweet_tag.filter(waktu__year=tahun,waktu__month__gte=bulan1,waktu__month__lte=bulan2)
            tweet_date = TweetsModel.objects.filter(waktu__year=tahun,waktu__month__gte=bulan1,waktu__month__lte=bulan2)
        else:
            bulan2 = max(b).month
            tweet_tag = tweet_tag.filter(waktu__year=tahun,waktu__month__gte=bulan2)
            tweet_date = TweetsModel.objects.filter(waktu__year=tahun,waktu__month__gte=bulan2)
    else:
        bulan1, bulan2 = min(b).month, max(b).month
        tahun = max(tweet_tag.dates('waktu', 'year')).year
        tweet_tag = tweet_tag.filter(waktu__year=tahun)
        tweet_date = TweetsModel.objects.filter(waktu__year=tahun)

    with open('data\ISO_3166-2.txt') as d:
        dict_area = [i for i in d.read().split('\n')]
        dict_area = {k.split(':')[0]:k.split(':')[1] for k in dict_area[:-1]}

    # data_lokasi = [[t['lokasi'],t['lokasi__count']] for t in tweet_tag.exclude(lokasi=None).values('lokasi').annotate(Count('lokasi'))]
    print(tweet_tag.exclude(lokasi=None)[0].lokasi)

    date_dict = tweet_tag.values('waktu').annotate(Count('waktu'))
    date_dict_all = tweet_date.values('waktu').annotate(Count('waktu'))

    line_data = [[f"{d['waktu'].day}/{d['waktu'].month}", d['waktu__count'], da['waktu__count']] for d,da in zip(date_dict, date_dict_all)]
    line_data.insert(0,['tanggal', 'tweet dengan hashtag', 'semua tweet'])

    try:    nowhere = tweet_tag.filter(lokasi=None).count()
    except: nowhere = 0

    f = folium.Figure(width=1000, height=390)
    m = folium.Map(location=(-2,116.5), zoom_start=5, tiles="CartoDB positron")
    marker_cluster = MarkerCluster().add_to(m)
    data_lokasi = tweet_tag.exclude(lokasi=None)
    data.apply(folium.Marker([each[1]['lat'],each[1]['lon']],
                            tooltip=f"{each[1]['lat']}, {each[1]['lon']}",
                            icon=folium.Icon(color='blue')).add_to(marker_cluster), axis = 1)
    # for each in titik.iterrows():
    #     folium.Marker([each[1]['lat'],each[1]['lon']], tooltip=f"{each[1]['lat']}, {each[1]['lon']}",icon=folium.Icon(color='blue')).add_to(marker_cluster)

    m.add_to(f)

    konteks         = {
        'map'           : f._repr_html_(),
        'isu_id'        : id,
        'bulan1_current': bulan_list[bulan1-1].title(),
        'bulan2_current': bulan_list[bulan2-1].title(),
        'tahun_current' : tahun,
        'line_data'     : line_data,
        'bulan_list'    : [bulan_list[b.month-1].title() for b in TweetsModel.objects.filter(id_isu=id, tags__hashtag=nama).dates('waktu','month')],
        'tahun_list'    : [t.year for t in TweetsModel.objects.filter(id_isu=id, tags__hashtag=nama).dates('waktu','year')],
        'nama_hashtag'  : nama,
        # 'data_lokasi'   : data_lokasi,
        'porsi_posisi'  : [nowhere, tweet_tag.count()-nowhere],
        'tweet_list'    : tweet_tag
    }

    return render(request, 'analysis.html', konteks)
