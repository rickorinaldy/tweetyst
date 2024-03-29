from io import BytesIO
from collections import Counter
from wordcloud import WordCloud
from django.shortcuts import render
from django.db.models import Count, Max
from django_pandas.io import read_frame
from folium.plugins import MarkerCluster
from django.http import HttpResponseRedirect
from stream_tweet.models import TweetsModel, Hashtag
import folium, matplotlib.pyplot as plt, base64, json, numpy as np

def std_outlier(data, out_sign, no_out_sign, threshold=2):
    mean = np.mean(data)
    std = np.std(data)
    return [out_sign if (i>(mean+threshold*std) or i<(mean-threshold*std)) else no_out_sign for i in data]

def marking(data):
    folium.Marker(
        [data.latitude,data.longitude],
        tooltip=f"@{data.user_id} || {data.waktu.strftime('%d/%m/%Y')}",
        icon=folium.Icon(color='blue'),
        popup=data.teks
    ).add_to(marker_cluster)


def analyst(request, id, nama, **kwargs):
    bulan_list = ['januari', 'februari', 'maret', 'april', 'mei', 'juni',
    'juli', 'agustus', 'september', 'oktober', 'november', 'desember']

    if request.method == 'POST':
        bulan1 = bulan_list.index(request.POST['bulan1'].lower())+1
        bulan2 = bulan_list.index(request.POST['bulan2'].lower())+1
        tahun  = request.POST['tahun']
        return HttpResponseRedirect(f'/analysis/{id}/%23{nama[1:]}/{bulan1}/{bulan2}/{tahun}')

    tweet_tag = tweet_tag_unf = TweetsModel.objects.filter(id_isu=id, tags__hashtag=nama)

    b = tweet_tag.dates('waktu','month')
    if kwargs['bulan1']!=0:
        tahun = kwargs['tahun']
        bulan1 = kwargs['bulan1']
        if bulan1 <= kwargs['bulan2']:
            bulan2 = kwargs['bulan2']
            tweet_tag  = tweet_tag.filter(waktu__year=tahun,waktu__month__gte=bulan1,waktu__month__lte=bulan2)
            tweet_date = TweetsModel.objects.filter(waktu__year=tahun,waktu__month__gte=bulan1,waktu__month__lte=bulan2)
        else:
            bulan2 = max(b).month
            tweet_tag  = tweet_tag.filter(waktu__year=tahun,waktu__month__gte=bulan2)
            tweet_date = TweetsModel.objects.filter(waktu__year=tahun,waktu__month__gte=bulan2)
    else:
        bulan1, bulan2 = min(b).month, max(b).month
        tahun = max(tweet_tag.dates('waktu', 'year')).year
        tweet_tag  = tweet_tag.filter(waktu__year=tahun)
        tweet_date = TweetsModel.objects.filter(waktu__year=tahun,waktu__month__gte=bulan1,waktu__month__lte=bulan2)

    date_dict     = tweet_tag.values('waktu').annotate(Count('waktu'))
    date_dict_all = tweet_date.values('waktu').annotate(Count('waktu'))

    out_sign = 'point { size: 7; shape-type: star; fill-color: #a52714; dataOpacity: 0.3; visible: true }'
    no_out_sign = 'point'

    line_data = [[f"{d['waktu'].strftime('%d/%m')}", d['waktu__count'], da['waktu__count']] for d,da in zip(date_dict, date_dict_all)]
    zipHashList = list(zip(*line_data))
    out1,out2 = std_outlier(zipHashList[1], out_sign, no_out_sign), std_outlier(zipHashList[2], out_sign, no_out_sign)
    line_data = list(zip(zipHashList[0], zipHashList[1], zipHashList[2], out1, out2))
    line_data = [list(i) for i in line_data]
    line_data.insert(0,['tanggal', 'tweet dengan hashtag', 'semua tweet', {'type': 'string', 'role': 'style'}, {'type': 'string', 'role': 'style'}])

    f = folium.Figure(width=1000, height=390)
    m = folium.Map(location=(-2,116.5), zoom_start=5, tiles="CartoDB positron")
    global marker_cluster
    marker_cluster = MarkerCluster().add_to(m)

    tweet_lokasi = tweet_tag.exclude(lokasi=None)

    try:    nowhere = tweet_lokasi.count()
    except: nowhere = 0

    data_lokasi = {t['lokasi']:t['lokasi__count'] for t in tweet_lokasi.values('lokasi').annotate(Count('lokasi'))}

    for i in map(marking, list(tweet_lokasi)):pass

    with open('data\indonesia.geojson') as ig:
        json_loc = json.load(ig)

    data_provinsi = {}
    for i,j in enumerate(json_loc['features']):
        if j['properties']['state'] in data_lokasi.keys():
            data_provinsi[j['properties']['state']] = json_loc['features'][i]['properties']['jumlah'] = data_lokasi[j['properties']['state']]
        else:
            json_loc['features'][i]['properties']['jumlah'] = 0

    pmap = folium.Choropleth(
                geo_data=json_loc,
                data=data_lokasi,
                key_on='properties.state',
                fill_color='YlOrRd'
            ).add_to(m)

    folium.features.GeoJsonTooltip(
            fields=['state','jumlah'],
            aliases=['Provinsi','Jumlah'],
            labels=True,
            sticky=True,
            toLocaleString=True).add_to(pmap.geojson)

    folium.plugins.Search(layer=pmap,
                     geom_type='Polygon',
                     placeholder='Cari Provinsi',
                     collapsed=True,
                     search_label='state',
                     weight=3
                    ).add_to(m)

    m.add_to(f)

    with open('data\stopword.txt') as stop:
        stopword = set(stop.read().split('\n'))

    teks_tweet = ' '.join([t.teks for t in tweet_tag])

    wordcloud = WordCloud(random_state=27,
                    height=205,
                    background_color='black',
                    colormap='Set2',
                    collocations=False,
                    stopwords=stopword).generate(teks_tweet)

    fig = plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")

    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png', bbox_inches='tight')
    graphic = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    tmpfile.close()

    user = [[t['user_id'],t['user_id__count'],list(tweet_tag.filter(user_id=t['user_id']).aggregate(Max('like_count'),Max('retweet_count'),Max('reply_count')).values())] for t in tweet_tag.values('user_id').annotate(Count('user_id'))]

    konteks         = {
        'isu_id'        : id,
        'user'          : user,
        'nama_hashtag'  : nama,
        'wordcloud'     : graphic,
        'data_lokasi'   : data_provinsi,
        'tweet_list'    : tweet_tag,
        'map'           : f._repr_html_(),
        'porsi_posisi'  : [nowhere, tweet_tag.count()-nowhere],
        'bulan_list'    : [bulan_list[b.month-1].title() for b in tweet_tag_unf.dates('waktu','month')],
        'bulan1_current': bulan_list[bulan1-1].title(),
        'bulan2_current': bulan_list[bulan2-1].title(),
        'bulan1'        : bulan1,
        'bulan2'        : bulan2,
        'tahun_list'    : [t.year for t in tweet_tag_unf.dates('waktu','year')],
        'tahun_current' : tahun,
        'line_data'     : line_data
    }

    return render(request, 'analysis.html', konteks)
