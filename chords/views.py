from django.shortcuts import render, get_object_or_404

from .models import Artist, Song


def index(request):
    context = {'hello_msg' : 'This is the index page'}
    return render(request, 'chords/index.html', context)

def song(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug)
    return render(request, 'chords/song.html', {'song' : song})

def about(request):
    return render(request, 'chords/about.html', {})
