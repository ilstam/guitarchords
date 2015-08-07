from django.shortcuts import render, get_object_or_404

from .models import Artist, Song
from .forms import AddSongForm


def index(request):
    recent_songs = Song.objects.filter(published=True).order_by('-pub_date')[:5]
    return render(request, 'chords/index.html', {'songs' : recent_songs})

def song(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug, published=True)
    return render(request, 'chords/song.html', {'song' : song})

def artist(request, artist_slug):
    artist = get_object_or_404(Artist, slug=artist_slug)
    songs = Song.objects.filter(artist=artist, published=True)
    context = {'artist' : artist, 'songs' : songs}
    return render(request, 'chords/artist.html', context)

def add_song(request):
    if request.method == 'POST':
        form = AddSongForm(request.POST)
        if form.is_valid():
            pass
            #return HttpResponseRedirect('somewhere')

    else:
        form = AddSongForm()

    return render(request, 'chords/add_song.html', {'form' : form})

def about(request):
    return render(request, 'chords/about.html', {})
