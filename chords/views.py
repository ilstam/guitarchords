from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Artist, Song, Bookmark
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
    artist = get_object_or_404(Artist, slug=artist_slug)
    songs = Song.objects.filter(artist=artist, published=True)
    context = {'artist' : artist, 'songs' : songs}
    return render(request, 'chords/artist.html', context)

@login_required
def add_song(request):
    if request.method == 'POST':
        form = AddSongForm(request.POST)
        if form.is_valid():
            request.session['song_data'] = form.cleaned_data
            return redirect('chords:verify_song')
    else:
        form = AddSongForm(initial=request.session.get('song_data', None))

    return render(request, 'chords/add_song.html', {'form' : form})

@login_required
def verify_song(request):
    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    song = Song(
        title=song_data['title'], artist=None, video=song_data['video'],
        genre=song_data['genre'], tabs=song_data['tabs'],
        content=song_data['content'])

    context = {'song' : song, 'artist_txt' : song_data['artist_txt']}
    return render(request, 'chords/verify_song.html', context)

@login_required
def song_submitted(request):
    if not request.user.is_authenticated():
        return redirect('chords:index')

    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    artist = Artist.objects.get_or_create(name=song_data['artist_txt'])[0]
    artist.save()
    song = Song(
        title=song_data['title'], artist=artist, user=request.user,
        video=song_data['video'], genre=song_data['genre'],
        tabs=song_data['tabs'], content=song_data['content'])
    song.save()

    del request.session['song_data']
    return render(request, 'chords/song_submitted.html', {})

@login_required
def user_bookmarks(request):
    if not request.user.is_authenticated():
        return redirect('chords:index')

    user = request.user
    bookmarks = Bookmark.objects.filter(user=user, song__published=True).order_by('song__artist__name', 'song__title')
    songs = [bookmark.song for bookmark in bookmarks]
    return render(request, 'chords/user_bookmarks.html', {'songs' : songs})

def about(request):
    return render(request, 'chords/about.html', {})
