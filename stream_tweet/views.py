from django.shortcuts import render
from . import stream
from django.http import HttpResponseRedirect
from home.models import IsuTweet
import os

def online_stream(request):
    if request.method == 'POST':
        try:
            s = IsuTweet.objects.create(
                    judul       = request.POST['judul'],
                    deskripsi   = request.POST['deskripsi'],
                    keyword     = request.POST['keyword'])
            stream.onlinestream(id=str(s.id_ref))
            return HttpResponseRedirect('/home')
        except:
            return HttpResponseRedirect('/stream_tweet/online')
    else:
        return render(request,'stream_tweet/online.html')

def file_stream(request):
    if request.method == 'POST':
        try:
            s = IsuTweet.objects.create(
                    judul       = request.POST['judul'],
                    deskripsi   = request.POST['deskripsi'],
                    keyword     = 'stream offline (no keyword)')
            stream.filestream(namafile=request.POST['data'], id=str(s.id_ref))
            return HttpResponseRedirect('/home')
        except:
            return HttpResponseRedirect('/stream_tweet/file')

    else:
        return render(request,'stream_tweet/offline.html', {'file':os.listdir('data')})

def create_stream(request):
    if request.method == 'POST':
        form = UploadForm(request.POST)
        if request.POST['pilihan'] == 'fl':
            return HttpResponseRedirect('file')
        else:
            return HttpResponseRedirect('online')
    else:
        form = UploadForm()

    return render(request, 'stream_tweet/index.html', {'form':form})
