from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import FormView
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

import os

from .models import Artist, Song, Comment, User
from .forms import AddSongForm, AddCommentForm, ContactForm, SearchForm
from .utils import slugify_greek


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def index(request):
    if 'song_data' in request.session:
        del request.session['song_data']
    recent_songs = Song.get_recent_songs()[:5]
    popular_songs = Song.get_popular_songs()[:5]
    context = {'recent_songs' : recent_songs, 'popular_songs' : popular_songs}
    return render(request, 'chords/index.html', context)

def song(request, song_slug):
    context = {}
    if request.user.is_authenticated():
        song = get_object_or_404(Song, Q(slug=song_slug),
            Q(published=True) | Q(sender=request.user))
        song.viewedBy.add(request.user)

        context['bookmarked'] = bool(request.user.bookmarks.filter(slug=song.slug))
    else:
        song = get_object_or_404(Song, slug=song_slug, published=True)

    comments = song.comments.all().order_by('pub_date')
    comment_form = AddCommentForm(initial={
        'user' : request.user.id,
        'song' : song.id})
    context.update({'song' : song, 'preview' : False,
                    'comments' : comments, 'comment_form' : comment_form})
    return render(request, 'chords/song.html', context)

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

def popular(request):
    songs = Song.get_popular_songs()[:100]
    return render(request, 'chords/popular.html', {'songs' : songs})

def recently_added(request):
    songs = Song.get_recent_songs()[:100]
    return render(request, 'chords/recently_added.html', {'songs' : songs})

def search(request):
    searchBy = request.GET.get('searchBy', SearchForm.SEARCH_SONG)
    keywords = request.GET.get('keywords', '')
    genre = request.GET.get('genre', SearchForm.GENRE_ALL)
    tabs = request.GET.get('tabs', SearchForm.INCLUDE_TABS)
    orderBy = request.GET.get('orderBy', '')

    form = SearchForm(initial={'searchBy' : searchBy, 'keywords' : keywords,
                               'genre' : genre, 'tabs' : tabs})
    context = {'form' : form}

    if keywords:
        keyword_slug = slugify_greek(keywords)

        if searchBy == SearchForm.SEARCH_ARTIST:
            context['searchBy'] = 'artist'
            results = Artist.objects.filter(slug__contains=keyword_slug)
        elif searchBy == SearchForm.SEARCH_SONG:
            context['searchBy'] = 'song'
            results = Song.objects.filter(
                    slug__contains=keyword_slug, published=True)

            if genre != SearchForm.GENRE_ALL:
                results = results.filter(genre=genre)
            if tabs == SearchForm.CHORDS_ONLY:
                results = results.filter(tabs=False)
        else:
            context['searchBy'] = 'user'
            results = User.objects.filter(username__icontains=keywords)

        order_dict = {
                SearchForm.SEARCH_ARTIST :
                    {'nameAsc' : 'name', 'nameDesc' : '-name'},
                SearchForm.SEARCH_SONG :
                    {'nameAsc' : 'title', 'nameDesc' : '-title',
                     'artistAsc' : 'artist__name', 'artistDesc' : '-artist__name',
                     'genreAsc' : 'genre', 'genreDesc' : '-genre',
                     'tabsAsc' : '-tabs', 'tabsDesc' : 'tabs'},
                SearchForm.SEARCH_USER :
                    {'nameAsc' : 'username', 'nameDesc' : '-username'},
        }

        if orderBy:
            context['results'] = results.order_by(order_dict[searchBy][orderBy])
            html = render_to_string('chords/search_results_body.html', context)
            return HttpResponse(html)

        results = results.order_by(order_dict[searchBy]['nameAsc'])
        context.update({'results' : results, 'query' : keywords})

    return render(request, 'chords/search.html', context)

class ContactView(FormView):
    form_class = ContactForm
    template_name = 'chords/contact.html'
    success_url = reverse_lazy('chords:contact_done')

    def get_initial(self):
        if self.request.user.is_authenticated():
            return {'email' : self.request.user.email}
        return {}

    def form_valid(self, form):
        form.send_email()
        return super(ContactView, self).form_valid(form)

def contact_done(request):
    return render(request, 'chords/contact_done.html', {})

class AddCommentView(LoginRequiredMixin, FormView):
    form_class = AddCommentForm
    template_name = 'chords/display_comment.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get('testing', '') == 'True':
            os.environ['RECAPTCHA_TESTING'] = 'True'
            request.POST._mutable = True
            request.POST['g-recaptcha-response'] = 'PASSED'
            request.POST._mutable = False

        form = self.form_class(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            comment = Comment(user=data['user'], song=data['song'],
                              content=data['content'])
            comment.save()

            os.environ['RECAPTCHA_TESTING'] = 'False'
            return HttpResponse(render_to_string(self.template_name,
                                                 {'comment' : comment}))

        return HttpResponse(status=400) # Bad Request

@login_required
def add_bookmark(request, song_slug):
    song = get_object_or_404(Song, Q(slug=song_slug),
        Q(published=True) | Q(sender=request.user))
    request.user.bookmarks.add(song)
    return HttpResponse()

@login_required
def remove_bookmark(request, song_slug):
    song = get_object_or_404(Song, slug=song_slug)
    request.user.bookmarks.remove(song)
    return HttpResponse()

@login_required
def bookmarks(request):
    songs = request.user.bookmarks.filter(
            Q(published=True) | Q(sender=request.user)
            ).order_by('artist__name', 'title')
    return render(request, 'chords/bookmarks.html', {'songs' : songs})

class AddSongView(LoginRequiredMixin, FormView):
    form_class = AddSongForm
    template_name = 'chords/add_song.html'
    success_url = reverse_lazy('chords:verify_song')

    def get_initial(self):
        return self.request.session.get('song_data', None)

    def form_valid(self, form):
        self.request.session['song_data'] = form.cleaned_data
        self.request.session['song_data']['user_txt'] = self.request.user.get_username()
        return super(AddSongView, self).form_valid(form)

@login_required
def verify_song(request):
    song_data = request.session.get('song_data', None)
    if song_data is None:
        return redirect('chords:add_song')

    song = Song(
        title=song_data['title'], artist=None, video=song_data['video'],
        genre=song_data['genre'], tabs=song_data['tabs'],
        content=song_data['content'])
    if song.video:
        song.video = song.get_embed_video_url()

    context = {'song' : song, 'artist_txt' : song_data['artist_txt'],
               'user_txt' : song_data['user_txt'], 'preview' : True}
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
