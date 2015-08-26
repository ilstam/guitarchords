from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http.response import Http404

from chords.models import Song
from chords.views import user as user_view, song as song_view
from .helper_functions import (create_artist, create_song, create_user,
                               create_bookmark, valid_song_data)


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

    def test_index_view_with_an_unpublished_song(self):
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

        request = RequestFactory().get(reverse('chords:user',
                                       args=(user.username,)))
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

        request = RequestFactory().get(reverse('chords:user',
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

    def test_song_view_with_authenticated_user_looking_own_songs(self):
        """
        An authenticated user should be able to see both published and
        unpublished songs sent by him.
        """
        user = create_user()
        song_pub = create_song(title='Song_Published', published=True, user=user)
        song_unpub = create_song(title='Song_Unpublished', published=False,
                                 user=user)

        request = RequestFactory().get(reverse('chords:song',
                                       args=(song_pub.slug,)))
        request.user = user
        response = song_view(request, song_pub.slug)
        self.assertContains(response, song_pub.title, status_code=200)

        request = RequestFactory().get(reverse('chords:song',
                                       args=(song_unpub.slug,)))
        request.user = user
        response = song_view(request, song_unpub.slug)
        self.assertContains(response, song_unpub.title, status_code=200)

    def test_song_view_with_authenticated_user_looking_other_songs(self):
        """
        An authenticated user should be able to see only published songs from
        other users.
        """
        user_viewer = create_user(username='user_viewer')
        user_artist = create_user(username='user_artist')
        song_pub = create_song(title='Song Published', published=True,
                               user=user_artist)
        song_unpub = create_song(title='Song Unpublished', published=False,
                                 user=user_artist)

        request = RequestFactory().get(reverse('chords:song',
                                       args=(song_pub.slug,)))
        request.user = user_viewer
        response = song_view(request, song_pub.slug)
        self.assertContains(response, song_pub.title, status_code=200)

        request = RequestFactory().get(reverse('chords:song',
                                       args=(song_unpub.slug,)))
        request.user = user_viewer
        with self.assertRaises(Http404):
            song_view(request, song_unpub.slug)


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


class SearchViewTests(TestCase):
    def test_search_view_without_query(self):
        """
        Search view should display published songs.
        """
        response = self.client.get(reverse('chords:search'))
        self.assertContains(response, 'Search for a song title or artist')

    def test_search_view_with_a_published_song(self):
        """
        Search view should display published songs.
        """
        create_song(title='Random Song', published=True)
        response = self.client.get(reverse('chords:search') +
            '?search=Random Song')
        self.assertQuerysetEqual(response.context['results'],
                                 ['<Song: Random Song>'])
        self.assertContains(response, '1 relative result')

    def test_search_view_with_an_unpublished_song(self):
        """
        Search view should not display unpublished songs.
        """
        create_song(title='Random Song', published=False)
        response = self.client.get(reverse('chords:search') +
            '?search=Random Song')
        self.assertQuerysetEqual(response.context['results'], [])
        self.assertContains(response, 'No results found')

    def test_search_view_with_published_song_and_unpublished_song(self):
        """
        Search view should display only published songs.
        """
        create_song(title='Published Song1', published=True)
        create_song(title='Published Song2', published=True)
        create_song(title='Unpublished Song', published=False)
        response = self.client.get(reverse('chords:search') + '?search=Song')
        self.assertQuerysetEqual(response.context['results'].order_by('title'),
            ['<Song: Published Song1>', '<Song: Published Song2>'])
        self.assertContains(response, '2 relative results')

    def test_search_view_results_matching(self):
        """
        Search view should display songs that contain the query string in
        title or artist name. The match must be case insensitive and greek
        letters must be converted in english first.
        """
        create_song(title='Random Song', published=True)
        create_song(title='Tυχαίο Σόνγ', published=True)
        create_song(title='Some', artist=create_artist(name='Song Artist'),
            published=True)
        response = self.client.get(reverse('chords:search') +
            '?search=ΣόnG')
        self.assertQuerysetEqual(response.context['results'].order_by('title'),
            ['<Song: Random Song>', '<Song: Some>', '<Song: Tυχαίο Σόνγ>'])


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
        self.assertContains(response, 'Your bookmarks are empty.',
                            status_code=200)
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