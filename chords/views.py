from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .models import Artist, Song
from .forms import AddSongForm


def index(request):
    if 'song_data' in request.session:
        del request.session['song_data']
    recent_songs = Song.objects.filter(published=True).order_by('-pub_date')[:5]
    return render(request, 'chords/index.html', {'songs' : recent_songs})

def song(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug, published=True)
    return render(request, 'chords/song.html', {'song' : song})

def artist(request, artist_slug):
    artist = get_object_or_404(Artist, ~Q(name='NullArtist'), slug=artist_slug)
    songs = Song.objects.filter(artist=artist, published=True)
    context = {'artist' : artist, 'songs' : songs}
    return render(request, 'chords/artist.html', context)

def add_song(request):
    if request.method == 'POST':
        form = AddSongForm(request.POST)
        if form.is_valid():
            request.session['song_data'] = form.cleaned_data
            return redirect('chords:verify_song')
    else:
        form = AddSongForm(initial=request.session.get('song_data', None))

    return render(request, 'chords/add_song.html', {'form' : form})

def verify_song(request):
    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    song = Song.create_song_from_json(data=song_data, save=False)
    context = {'song' : song, 'pseudo_artist' : song_data['artist_txt']}
    return render(request, 'chords/verify_song.html', context)

def song_submitted(request):
    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    Song.create_song_from_json(data=song_data, save=True)
    del request.session['song_data']
    return render(request, 'chords/song_submitted.html', {})

def about(request):
    return render(request, 'chords/about.html', {})
