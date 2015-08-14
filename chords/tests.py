from django.test import TestCase, SimpleTestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Artist, Song, Bookmark
from .views import user as user_view
from .forms import AddSongForm
from . import utils


def create_artist(name='Some Artist'):
    artist = Artist(name=name)
    artist.save()
    return artist

def create_song(title='Random Song', artist=None, user=None, published=True):
    song = Song(title=title, artist=artist, user=user, published=published)
    song.save()
    return song

def create_user(username='username', password='password'):
    user = User.objects.create_user(username=username, password=password)
    user.save()
    return user

def create_bookmark(user, published_song=True):
    bookmark = Bookmark(user=user, song=create_song(published=published_song))
    bookmark.save()
    return bookmark

def valid_song_data(title='Title', artist_txt='artist_txt', genre=Song.POP,
                    video='http://www.example.com', tabs=True, content='content'):
    return {
        'title' : title, 'artist_txt' : artist_txt, 'genre' : genre,
        'video' : video, 'tabs' : tabs, 'content' : content
    }


class ArtistModelTests(TestCase):
    def test_slug_line_creation(self):
        """
        When we add an artist, an appropriate slug must be created.
        """
        artist = create_artist(name='Some Artist')
        self.assertEqual(artist.slug, 'some-artist')

    def test_slug_line_creation_greek(self):
        """
        When we add an artist with a greek name, an appropriate slug must be
        created in english.
        """
        artist = create_artist(name='Τυχαίο Όνομα Καλλιτέχνη')
        self.assertEqual(artist.slug, 'tyxaio-onoma-kallitexnh')

    def test_slugs_are_unique(self):
        """
        Artist slugs must be always unique, even when there are artists with
        the same name.
        """
        artist1 = create_artist()
        artist2 = Artist(name=artist1.name)
        artist2.save()
        self.assertNotEqual(artist1.slug, artist2.slug)

    def test_slugs_are_of_appropriate_size(self):
        """
        Artist slug must not exceed the specified length.
        """
        slug_length = 20
        artist = Artist(name='Some Artist')
        artist.save(slug_max_length=slug_length)
        self.assertLessEqual(len(artist.slug), slug_length)

    def test_slug_when_name_changes(self):
        """
        Once created slug must never change, even when we update the artist
        name, in order to avoid broken links.
        """
        artist = create_artist(name='Some Artist')
        orig_slug = artist.slug
        artist.name = 'Some Other Name'
        artist.save()
        self.assertEqual(artist.slug, orig_slug)


class SongModelTests(TestCase):
    def test_slug_line_creation(self):
        """
        When we add a song, an appropriate slug must be created.
        """
        song = create_song(title='Random Song')
        self.assertEqual(song.slug, 'random-song')

    def test_slug_line_creation_greek(self):
        """
        When we add a song with a greek title, an appropriate slug must be
        created in english.
        """
        song = create_song(title='Τυχαίο όνομα από τραγούδι')
        self.assertEqual(song.slug, 'tyxaio-onoma-apo-tragoudi')

    def test_slugs_are_unique(self):
        """
        Song slugs must be always unique, even when they have the same title.
        """
        song1 = create_song()
        song2 = Song(title=song1.title, artist=song1.artist)
        song2.save()
        self.assertNotEqual(song1.slug, song2.slug)

    def test_slugs_are_of_appropriate_size(self):
        """
        Song slug must not exceed the specified length.
        """
        slug_length = 5
        song = Song(title='Random Song', artist=create_artist())
        song.save(slug_max_length=slug_length)
        self.assertLessEqual(len(song.slug), slug_length)

    def test_slug_when_title_changes(self):
        """
        Once created, slug must never change, even when we update the song
        title, in order to avoid broken links.
        """
        song = create_song(title='Random Song')
        orig_slug = song.slug
        song.title = 'Some Other Name'
        song.save()
        self.assertEqual(song.slug, orig_slug)

    def test_pub_date_with_a_published_song(self):
        """
        Published songs must have a published day in past.
        """
        song = create_song(published=True)
        self.assertLessEqual(song.pub_date, timezone.now())

    def test_pub_date_with_an_unpublished_song(self):
        """
        Un-published songs should have no publish date, even if they published
        once.
        """
        song = create_song(published=False)
        self.assertEqual(song.pub_date, None)
        song.published = True
        song.save()
        song.published = False
        song.save()
        self.assertEqual(song.pub_date, None)


class IndexViewTests(TestCase):
    def test_index_view_with_no_songs(self):
        """
        If no songs exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('chords:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no songs present at the moment.')
        self.assertNotContains(response, 'Recently added songs')
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_index_view_with_a_published_song(self):
        """
        Recently published songs should be displayed on the index page.
        """
        create_song(title='Random Song', published=True)
        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_index_view_with_a_unpublished_song(self):
        """
        Recently un-published songs should not be displayed on the index page.
        """
        create_song(published=False)
        response = self.client.get(reverse('chords:index'))
        self.assertContains(response, 'There are no songs present at the moment.')
        self.assertNotContains(response, 'Recently added songs')
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_index_view_with_published_and_unpublished_song(self):
        """
        Even if both published and un-published songs exist, only published
        songs should be displayed on the index page.
        """
        create_song(title='Random Song', published=True)
        create_song(title='Another Random Song', published=False)
        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_erase_song_data(self):
        """
        Index view must remove song_data from the session.
        """
        session = self.client.session
        session['song_data'] = valid_song_data()
        session.save()
        self.assertTrue('song_data' in self.client.session)
        response = self.client.get(reverse('chords:index'))
        self.assertFalse('song_data' in self.client.session)


class ArtistViewTests(TestCase):
    def test_artist_view_with_an_invalid_slug(self):
        """
        The artist view should return a 404 not found for invalid slugs.
        """
        response = self.client.get(reverse('chords:artist', args=('slug',)))
        self.assertEqual(response.status_code, 404)

    def test_artist_view_with_a_valid_slug(self):
        """
        The artist view should display artist name for valid slugs.
        """
        artist = create_artist()
        response = self.client.get(reverse('chords:artist', args=(artist.slug,)))
        self.assertContains(response, artist.name, status_code=200)

    def test_artist_view_with_no_songs(self):
        """
        The artist view should display an appropriate message when there are
        no songs associated with the artist.
        """
        artist = create_artist()
        response = self.client.get(reverse('chords:artist', args=(artist.slug,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            'There are no registered songs for this artist.')
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_artist_view_with_a_published_song(self):
        """
        The artist view should display published songs.
        """
        song = create_song(published=True, artist=create_artist())
        response = self.client.get(reverse('chords:artist',
                                   args=(song.artist.slug,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_artist_view_with_an_unpublished_song(self):
        """
        The artist view should not display un-published songs.
        """
        song = create_song(published=False, artist=create_artist())
        response = self.client.get(reverse('chords:artist',
                                   args=(song.artist.slug,)))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_artist_view_with_published_and_unpublished_song(self):
        """
        Even if both published and un-published songs exist, only published
        songs should be displayed on the artist view.
        """
        artist = create_artist()
        song1 = create_song(title='Random Song', artist=artist, published=True)
        song2 = create_song(artist=artist, published=False)

        response = self.client.get(reverse('chords:artist', args=(artist.slug,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])


class UserViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_user_view_with_an_invalid_username(self):
        """
        The user view should return a 404 not found for invalid usernames.
        """
        response = self.client.get(reverse('chords:user', args=('username',)))
        self.assertEqual(response.status_code, 404)

    def test_user_view_with_a_valid_username(self):
        """
        The user view should dislay the username for valid usernames.
        """
        user = create_user()
        response = self.client.get(reverse('chords:user', args=(user.username,)))
        self.assertContains(response, user.username, status_code=200)

    def test_user_view_with_no_songs(self):
        """
        The user view should display an appropriate message when there are
        no songs associated with the user.
        """
        user = create_user()
        response = self.client.get(reverse('chords:user', args=(user.username,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "This user hasn't sent any songs yet.")
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_user_view_with_a_published_song(self):
        """
        The user view should display published songs.
        """
        song = create_song(published=True, user=create_user())
        response = self.client.get(reverse('chords:user',
                                   args=(song.user.username,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_user_view_with_an_unpublished_song(self):
        """
        The user view should not display un-published songs.
        """
        song = create_song(published=False, user=create_user())
        response = self.client.get(reverse('chords:user',
                                   args=(song.user.username,)))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_user_view_with_published_and_unpublished_song(self):
        """
        Even if both published and un-published songs exist, only published
        songs should be displayed on the user view.
        """
        user = create_user()
        create_song(published=True, user=user)
        create_song(published=False, user=user)
        response = self.client.get(reverse('chords:user', args=(user.username,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_user_view_with_authenticated_user_looking_own_page(self):
        """
        An authenticated user should be able to see both published and
        unpublished songs, on his own user page.
        """
        user = create_user()
        create_song(title='Song_Published', published=True, user=user)
        create_song(title='Song_Unpublished', published=False, user=user)

        request = self.factory.get(reverse('chords:user', args=(user.username,)))
        request.user = user
        response = user_view(request, user.username)
        self.assertContains(response, 'Song_Published')
        self.assertContains(response, 'Song_Unpublished')

    def test_user_view_with_authenticated_user_looking_other_user_page(self):
        """
        An authenticated user should be able to see only published songs,
        when looking on another's user page.
        """
        user_viewer = create_user(username='user_viewer')
        user_artist = create_user(username='user_artist')
        create_song(title='Song Published', published=True, user=user_artist)
        create_song(title='Song Unpublished', published=False, user=user_artist)

        request = self.factory.get(reverse('chords:user',
                                   args=(user_artist.username,)))
        request.user = user_viewer
        response = user_view(request, user_artist.username)
        self.assertContains(response, 'Song Published')
        self.assertNotContains(response, 'Song Unpublished')


class SongViewTests(TestCase):
    def test_song_view_with_an_invalid_slug(self):
        """
        The song view should return a 404 not found for invalid slugs.
        """
        response = self.client.get(reverse('chords:song', args=('slug',)))
        self.assertEqual(response.status_code, 404)

    def test_song_view_with_a_valid_slug(self):
        """
        The song view should display song title for valid slugs.
        """
        song = create_song(published=True)
        response = self.client.get(reverse('chords:song', args=(song.slug,)))
        self.assertContains(response, song.title, status_code=200)

    def test_song_view_with_a_published_song(self):
        """
        The song view should display song title for published songs.
        """
        song = create_song(published=True)
        response = self.client.get(reverse('chords:song', args=(song.slug,)))
        self.assertContains(response, song.title, status_code=200)

    def test_song_view_with_an_unpublished_song(self):
        """
        The song view should return a 404 not found for un-published songs.
        """
        song = create_song(published=False)
        response = self.client.get(reverse('chords:song', args=(song.slug,)))
        self.assertEqual(response.status_code, 404)


class AddSongViewTests(TestCase):
    def setUp(self):
        self.user = create_user(password='password')
        self.client.login(username=self.user.username, password='password')

    def test_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the add_song view must redirect to the
        login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:add_song'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:add_song'))

    def test_addsong_view_with_valid_input(self):
        """
        The add_song view with valid POST data should return a 302 Found.
        """
        response = self.client.post(reverse('chords:add_song'), valid_song_data())
        self.assertEqual(response.status_code, 302)

    def test_addsong_view_with_invalid_input(self):
        """
        The add_song view must return an appropriate message for each case of
        invalid POST data.
        """
        # missing title
        response = self.client.post(reverse('chords:add_song'),
                valid_song_data(title=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        # missing artist_txt
        response = self.client.post(reverse('chords:add_song'),
                valid_song_data(artist_txt=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        # missing genre
        response = self.client.post(reverse('chords:add_song'),
                valid_song_data(genre=None))
        self.assertEqual(response.status_code, 200)
        msg = 'Select a valid choice. None is not one of the available choices.'
        self.assertContains(response, msg)
        # invalid video url
        response = self.client.post(reverse('chords:add_song'),
                valid_song_data(video='invalid_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid URL.')


class VerifySongViewTests(TestCase):
    def setUp(self):
        self.user = create_user(password='password')
        self.client.login(username=self.user.username, password='password')

    def test_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the verify_song view must redirect to the
        login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:verify_song'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:verify_song'))

    def test_redirects_with_no_song_data(self):
        """
        When there are no song_data on the session the verify_song view must
        redirect to the add_song view.
        """
        response = self.client.get(reverse('chords:verify_song'))
        self.assertFalse('song_data' in self.client.session)
        self.assertRedirects(response, reverse('chords:add_song'))

    def test_with_song_data(self):
        """
        When there are valid song_data stored on the session the verify_song
        view must display the song.
        """
        session = self.client.session
        session['song_data'] = valid_song_data()
        session.save()
        response = self.client.get(reverse('chords:verify_song'))
        self.assertContains(response, session['song_data']['title'])


class SongSubmittedViewTests(TestCase):
    def setUp(self):
        self.user = create_user(password='password')
        self.client.login(username=self.user.username, password='password')

    def test_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the song_submitted view must redirect to
        the login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:song_submitted'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:song_submitted'))

    def test_redirects_with_no_song_data(self):
        """
        When there are no song_data on the session the song_submitted view
        must redirect to the add_song view.
        """
        response = self.client.get(reverse('chords:song_submitted'))
        self.assertFalse('song_data' in self.client.session)
        self.assertRedirects(response, reverse('chords:add_song'))

    def test_with_song_data(self):
        """
        When there are valid song_data stored on the session, one more
        _unpublished_ song must be added to the database.
        """
        session = self.client.session
        session['song_data'] = valid_song_data()
        session.save()
        pub_songs = Song.objects.filter(published=True).count()
        unpub_songs = Song.objects.filter(published=False).count()

        response = self.client.get(reverse('chords:song_submitted'))
        self.assertContains(response, 'Thank you for submitting a song!')
        self.assertEqual(pub_songs, Song.objects.filter(published=True).count())
        self.assertEqual(unpub_songs + 1,
                Song.objects.filter(published=False).count())
        self.assertFalse('song_data' in self.client.session)


class UserBookmarksViewTests(TestCase):
    def setUp(self):
        self.user = create_user(password='password')
        self.client.login(username=self.user.username, password='password')

    def test_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the user_bookmarks view must redirect to
        the login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:user_bookmarks'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:user_bookmarks'))

    def test_userbookmarks_view_with_no_songs(self):
        """
        The user bookmarks view should display an appropriate message if
        user has no bookmarks saved.
        """
        response = self.client.get(reverse('chords:user_bookmarks'))
        self.assertContains(response, 'Your bookmarks are empty.', status_code=200)
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_userbookmarks_view_with_a_published_song(self):
        """
        The user bookmarks view should display published songs.
        """
        create_bookmark(user=self.user, published_song=True)
        response = self.client.get(reverse('chords:user_bookmarks'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_userbookmarks_view_with_an_unpublished_song(self):
        """
        The user bookmarks view should not display un-published songs.
        """
        create_bookmark(user=self.user, published_song=False)
        response = self.client.get(reverse('chords:user_bookmarks'))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_userbookmarks_view_with_published_and_unpublished_song(self):
        """
        Even if user have published and un-published bookmarks, only published
        songs should be displayed on the user bookmark view.
        """
        create_bookmark(user=self.user, published_song=True)
        create_bookmark(user=self.user, published_song=False)
        response = self.client.get(reverse('chords:user_bookmarks'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])


class AddSongFormTests(TestCase):
    def test_form_with_valid_data(self):
        """
        Form must be valid with sensible data.
        """
        form = AddSongForm(data=valid_song_data())
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        """
        Form cannot be valid if any of title, artist_txt, genre or content
        is missing, or if we give an invalid url.
        """
        form = AddSongForm()
        self.assertFalse(form.is_valid())
        # title required
        form = AddSongForm(data=valid_song_data(title=''))
        self.assertFalse(form.is_valid())
        # artist_txt required
        form = AddSongForm(data=valid_song_data(artist_txt=''))
        self.assertFalse(form.is_valid())
        # genre required
        form = AddSongForm(data=valid_song_data(genre=None))
        self.assertFalse(form.is_valid())
        # invalid video url
        form = AddSongForm(data=valid_song_data(video='invalid_url'))
        self.assertFalse(form.is_valid())


class TestUtils(SimpleTestCase):
    def test_strip_whitespace_lines(self):
        """
        The strip_empty_lines() function should remove all empty lines from
        end and begging and any adjacent whitespace lines inside.
        """
        s1 = '  \t\n\n\t \tsome identation here\n\n\n\nlorem ipsum\n\n'
        s2 =         '\t \tsome identation here\n\nlorem ipsum'
        self.assertEqual(utils.strip_whitespace_lines(s1), s2)

    def test_song_parsing(self):
        """
        A song must have all its chords enclosed in span tags after parsing and
        all empty lines in the begging end the end must be stripped.
        """
        orig = """
      @Am@  @G#@
Lorem ipsum, lorem ipsum

"""
        result = """      <span class="chord">Am</span>  <span class="chord">G#</span>
Lorem ipsum, lorem ipsum"""
        self.assertEqual(utils.parse_song(orig), result)
