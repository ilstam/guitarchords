from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Artist, Song
from .forms import AddSongForm
from .utils import slugify_greek


def index(request):
    if 'song_data' in request.session:
        del request.session['song_data']
    recent_songs = Song.objects.filter(published=True).order_by('-pub_date')[:5]
    return render(request, 'chords/index.html', {'songs' : recent_songs})

def song(request, song_slug):
    if request.user.is_authenticated():
        song = get_object_or_404(Song, Q(slug=song_slug),
            Q(published=True) | Q(sender=request.user))
    else:
        song = get_object_or_404(Song, slug=song_slug, published=True)

    return render(request, 'chords/song.html', {'song' : song})

def song_json(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug, published=True)
    return JsonResponse(song.tojson())

def artist(request, artist_slug):
    artist = get_object_or_404(Artist, slug=artist_slug)
    songs = artist.songs.filter(published=True).order_by('title')
    context = {'artist' : artist, 'songs' : songs}
    return render(request, 'chords/artist.html', context)

def user(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and request.user == user:
        songs = user.songs.all()
    else:
        songs = user.songs.filter(published=True)

    songs = songs.order_by('artist__name', 'title')
    context = {'theuser' : user, 'songs' : songs}
    return render(request, 'chords/user.html', context)

def search(request):
    query = request.GET.get('search', '')
    query_slug = slugify_greek(query)
    context = {}
    if query:
        results = Song.objects.filter(Q(published=True),
            Q(slug__contains=query_slug) | Q(artist__slug__contains=query_slug))
        context = {'query' : query, 'results' : results,
                   'results_count' : results.count()}
    return render(request, 'chords/search.html', context)

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
    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    artist = Artist.objects.get_or_create(
            slug=slugify_greek(song_data['artist_txt']))[0]
    artist.save()
    song = Song(
        title=song_data['title'], artist=artist, sender=request.user,
        video=song_data['video'], genre=song_data['genre'],
        tabs=song_data['tabs'], content=song_data['content'])
    song.save()

    del request.session['song_data']
    return render(request, 'chords/song_submitted.html', {})

@login_required
def bookmarks(request):
    songs = request.user.bookmarks.filter(published=True
            ).order_by('artist__name', 'title')
    return render(request, 'chords/bookmarks.html', {'songs' : songs})
