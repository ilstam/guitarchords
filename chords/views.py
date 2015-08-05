from django.shortcuts import render, get_object_or_404

from .models import Artist, Song


def index(request):
    recent_songs = Song.objects.order_by('-pub_date')[:5]
    return render(request, 'chords/index.html', {'songs' : recent_songs})

def song(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug)
    return render(request, 'chords/song.html', {'song' : song})

def about(request):
    return render(request, 'chords/about.html', {})
