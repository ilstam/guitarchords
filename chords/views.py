from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import Artist, Song
from .forms import AddSongForm, SearchForm
from .utils import slugify_greek


def index(request):
    if 'song_data' in request.session:
        del request.session['song_data']
    recent_songs = Song.objects.filter(published=True).order_by('-pub_date')[:5]
    popular_songs = Song.objects.filter(published=True)\
            .annotate(popularity=Count('viewedBy') + 2 * Count('bookmarkedBy'))\
            .order_by('-popularity')[:5]
    context = {'recent_songs' : recent_songs, 'popular_songs' : popular_songs}
    return render(request, 'chords/index.html', context)

def song(request, song_slug):
    if request.user.is_authenticated():
        song = get_object_or_404(Song, Q(slug=song_slug),
            Q(published=True) | Q(sender=request.user))
        song.viewedBy.add(request.user)
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
    searchBy = request.GET.get('searchBy', SearchForm.SEARCH_SONG)
    keywords = request.GET.get('keywords', '')
    genre = request.GET.get('genre', SearchForm.GENRE_ALL)
    tabs = request.GET.get('tabs', SearchForm.INCLUDE_TABS)

    form = SearchForm(initial={'searchBy' : searchBy, 'keywords' : keywords,
                               'genre' : genre, 'tabs' : tabs})
    context = {'form' : form}

    if keywords:
        keyword_slug = slugify_greek(keywords)

        if searchBy == SearchForm.SEARCH_ARTIST:
            results = Artist.objects.filter(slug__contains=keyword_slug)

        elif searchBy == SearchForm.SEARCH_SONG:
            results = Song.objects.filter(slug__contains=keyword_slug, published=True)

            if genre != SearchForm.GENRE_ALL:
                results = results.filter(genre=genre)

            if tabs == SearchForm.CHORDS_ONLY:
                results = results.filter(tabs=False)
        # else:
            # results = User.objects.filter(slug__contains=keyword_slug, published=True)

        context['results'] = results

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

    try:
        artist = Artist.objects.get(slug=slugify_greek(song_data['artist_txt']))
    except Artist.DoesNotExist:
        artist = Artist(name=song_data['artist_txt'])
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
