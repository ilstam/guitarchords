from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.http.response import Http404

import os

from chords.models import Song
from chords.forms import SearchForm
from chords.views import user as user_view, song as song_view, search as search_view
from .helper_functions import (create_artist, create_song, create_user,
                               valid_song_data, valid_contact_data)


class LoginedTestCase(TestCase):
    """
    All test cases that requires user authentication should inherit from
    this class.
    """
    def setUp(self):
        self.user = create_user(password='password')
        self.client.login(username=self.user.username, password='password')


class IndexViewTests(TestCase):
    def test_index_view_with_no_songs(self):
        """
        If no songs exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('chords:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no songs present at the moment.')
        self.assertNotContains(response, 'Recently added songs')
        self.assertNotContains(response, 'Most popular songs')
        self.assertQuerysetEqual(response.context['recent_songs'], [])
        self.assertQuerysetEqual(response.context['popular_songs'], [])

    def test_index_view_with_a_published_song(self):
        """
        Recently published songs should be displayed on the index page.
        """
        create_song(title='Random Song', published=True)
        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['recent_songs'],
                                 ['<Song: Random Song>'])

    def test_index_view_with_an_unpublished_song(self):
        """
        Recently unpublished songs should not be displayed on the index page.
        """
        create_song(published=False)
        response = self.client.get(reverse('chords:index'))
        self.assertContains(response, 'There are no songs present at the moment.')
        self.assertNotContains(response, 'Recently added songs')
        self.assertQuerysetEqual(response.context['recent_songs'], [])

    def test_index_view_with_published_and_unpublished_song(self):
        """
        Even if both published and unpublished songs exist, only published
        songs should be displayed on the index page.
        """
        create_song(title='Random Song', published=True)
        create_song(title='Another Random Song', published=False)
        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['recent_songs'],
                                 ['<Song: Random Song>'])

    def test_index_view_display_more_popular_songs_first(self):
        """
        More popular songs should be displayed first in the index view.
        """
        song1 = create_song(title='Song1', published=True)
        song2 = create_song(title='Song2', published=True)
        song1.viewedBy.add(create_user(username='user1'))

        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['popular_songs'],
                                 ['<Song: Song1>', '<Song: Song2>'])

        song2.viewedBy.add(create_user(username='user2'))
        song2.viewedBy.add(create_user(username='user3'))

        response = self.client.get(reverse('chords:index'))
        self.assertQuerysetEqual(response.context['popular_songs'],
                                 ['<Song: Song2>', '<Song: Song1>'])

    def test_index_view_erase_song_data(self):
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
        The artist view should not display unpublished songs.
        """
        song = create_song(published=False, artist=create_artist())
        response = self.client.get(reverse('chords:artist',
                                   args=(song.artist.slug,)))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_artist_view_with_published_and_unpublished_song(self):
        """
        Even if both published and unpublished songs exist, only published
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
        song = create_song(published=True, sender=create_user())
        response = self.client.get(reverse('chords:user',
                                   args=(song.sender.username,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_user_view_with_an_unpublished_song(self):
        """
        The user view should not display unpublished songs.
        """
        song = create_song(published=False, sender=create_user())
        response = self.client.get(reverse('chords:user',
                                   args=(song.sender.username,)))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_user_view_with_published_and_unpublished_song(self):
        """
        Even if both published and unpublished songs exist, only published
        songs should be displayed on the user view.
        """
        user = create_user()
        create_song(published=True, sender=user)
        create_song(published=False, sender=user)
        response = self.client.get(reverse('chords:user', args=(user.username,)))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_user_view_with_authenticated_user_looking_own_page(self):
        """
        An authenticated user should be able to see both published and
        unpublished songs, on his own user page.
        """
        user = create_user()
        create_song(title='Song_Published', published=True, sender=user)
        create_song(title='Song_Unpublished', published=False, sender=user)

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
        create_song(title='Song Published', published=True, sender=user_artist)
        create_song(title='Song Unpublished',published=False,sender=user_artist)

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

    def test_song_view_with_a_published_song(self):
        """
        The song view should display song title for published songs.
        """
        song = create_song(published=True)
        response = self.client.get(reverse('chords:song', args=(song.slug,)))
        self.assertContains(response, song.title, status_code=200)

    def test_song_view_with_an_unpublished_song(self):
        """
        The song view should return a 404 not found for unpublished songs.
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
        song_pub = create_song(title='Song_Published',published=True,sender=user)
        song_unpub = create_song(title='Song_Unpublished', published=False,
                                 sender=user)

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
                               sender=user_artist)
        song_unpub = create_song(title='Song Unpublished', published=False,
                                 sender=user_artist)

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


class SongJsonViewTests(TestCase):
    def test_songjson_view_with_an_invalid_slug(self):
        """
        The song_json view should return a 404 not found for invalid slugs.
        """
        response = self.client.get(reverse('chords:song_json', args=('slug',)))
        self.assertEqual(response.status_code, 404)

    def test_songjson_view_with_a_published_song(self):
        """
        The song json view should display song title for published songs.
        """
        song = create_song(published=True)
        response = self.client.get(reverse('chords:song_json', args=(song.slug,)))
        self.assertContains(response, JsonResponse(song.tojson()).content,
                status_code=200)

    def test_songjson_view_with_an_unpublished_song(self):
        """
        The song json view should return a 404 not found for unpublished songs.
        """
        song = create_song(published=False)
        response = self.client.get(reverse('chords:song_json', args=(song.slug,)))
        self.assertEqual(response.status_code, 404)


class AddSongViewTests(LoginedTestCase):
    def test_addsong_view_redirects_when_not_logged_in(self):
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


class AddCommentViewTests(LoginedTestCase):
    def test_with_valid_data(self):
        """
        After posting to the add_comment view with valid data, one more comment
        should be assigned to the corresponding user and song.
        """
        os.environ['RECAPTCHA_TESTING'] = 'True'

        song = create_song()
        user_comments = self.user.comments.count()
        song_comments = song.comments.count()

        data = {'user' : self.user.id, 'song' : song.id,
                'content' : 'comment', 'testing' : 'True'}
        response = self.client.post(reverse('chords:add_comment'), data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.user.comments.count(), user_comments + 1)
        self.assertEqual(song.comments.count(), song_comments + 1)

    def test_with_invalid_data(self):
        """
        Add_comment view should return responses with appropriate status codes
        when we submit invalid data to it.
        """
        os.environ['RECAPTCHA_TESTING'] = 'True'

        song = create_song()
        user_comments = self.user.comments.count()
        song_comments = song.comments.count()

        # user doesn't exist
        data = {'user' : 'u', 'song' : song.id, 'content' : 'comment',
                'testing' : 'True'}
        response = self.client.post(reverse('chords:add_comment'), data)
        self.assertEqual(response.status_code, 400)

        # song doesn't exist
        data = {'user' : self.user.id, 'song' : 'slug', 'content' : 'comment',
                'testing' : 'True'}
        response = self.client.post(reverse('chords:add_comment'), data)
        self.assertEqual(response.status_code, 400)

        # comment is missing
        data = {'user' : self.user.id, 'song' : song.slug, 'comment' : '',
                'testing' : 'True'}
        response = self.client.post(reverse('chords:add_comment'), data)
        self.assertEqual(response.status_code, 400)

        self.assertEqual(self.user.comments.count(), user_comments)
        self.assertEqual(song.comments.count(), song_comments)


class VerifySongViewTests(LoginedTestCase):
    def test_verifysong_view_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the verify_song view must redirect to the
        login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:verify_song'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:verify_song'))

    def test_verifysong_view_redirects_with_no_song_data(self):
        """
        When there are no song_data on the session the verify_song view must
        redirect to the add_song view.
        """
        response = self.client.get(reverse('chords:verify_song'))
        self.assertFalse('song_data' in self.client.session)
        self.assertRedirects(response, reverse('chords:add_song'))

    def test_verifysong_view_with_song_data(self):
        """
        When there are valid song_data stored on the session the verify_song
        view must display the song.
        """
        session = self.client.session
        session['song_data'] = valid_song_data()
        session.save()
        response = self.client.get(reverse('chords:verify_song'))
        self.assertContains(response, session['song_data']['title'])


class SongSubmittedViewTests(LoginedTestCase):
    def test_songsubmitted_view_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the song_submitted view must redirect to
        the login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:song_submitted'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:song_submitted'))

    def test_songsubmitted_view_redirects_with_no_song_data(self):
        """
        When there are no song_data on the session the song_submitted view
        must redirect to the add_song view.
        """
        response = self.client.get(reverse('chords:song_submitted'))
        self.assertFalse('song_data' in self.client.session)
        self.assertRedirects(response, reverse('chords:add_song'))

    def test_songsubmitted_view_with_song_data(self):
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


class BookmarksViewTests(LoginedTestCase):
    def test_userbookmarks_view_redirects_when_not_logged_in(self):
        """
        When no user is logged in, the bookmarks view must redirect to
        the login page.
        """
        self.client.logout()
        response = self.client.get(reverse('chords:bookmarks'))
        self.assertRedirects(response,
            reverse('auth_login') + '?next=' + reverse('chords:bookmarks'))

    def test_userbookmarks_view_with_no_songs(self):
        """
        The bookmarks view should display an appropriate message if user has
        no bookmarks saved.
        """
        response = self.client.get(reverse('chords:bookmarks'))
        self.assertContains(response, 'Your bookmarks are empty.',
                            status_code=200)
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_userbookmarks_view_with_a_published_song(self):
        """
        The bookmarks view should display published songs.
        """
        self.user.bookmarks.add(create_song(published=True))
        response = self.client.get(reverse('chords:bookmarks'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])

    def test_userbookmarks_view_with_an_unpublished_song(self):
        """
        The bookmarks view should not display unpublished songs.
        """
        self.user.bookmarks.add(create_song(published=False))
        response = self.client.get(reverse('chords:bookmarks'))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_userbookmarks_view_with_published_and_unpublished_song(self):
        """
        Even if user have published and unpublished bookmarks, only published
        songs should be displayed on the bookmarks view.
        """
        self.user.bookmarks.add(create_song(published=True))
        self.user.bookmarks.add(create_song(published=False))
        response = self.client.get(reverse('chords:bookmarks'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Random Song>'])


class AddBookmarkViewTests(LoginedTestCase):
    def test_add_bookmark_view_with_an_invalid_slug(self):
        """
        The add_bookmark view should return a 404 not found for invalid slugs.
        """
        response = self.client.get(reverse('chords:add_bookmark', args=('slug',)))
        self.assertEqual(response.status_code, 404)

    def test_add_bookmark_view_with_a_valid_slug(self):
        """
        After calling add_bookmark view, the user must have one bookmark more.
        """
        num_bookmarks = self.user.bookmarks.count()
        self.user.bookmarks.add(create_song(published=True))
        self.assertTrue(self.user.bookmarks.count(), num_bookmarks + 1)


class RemoveBookmarkViewTests(LoginedTestCase):
    def test_remove_bookmark_view_with_an_invalid_slug(self):
        """
        The add_bookmark view should return a 404 not found for invalid slugs.
        """
        response = self.client.get(reverse('chords:remove_bookmark', args=('slug',)))
        self.assertEqual(response.status_code, 404)

    def test_remove_bookmark_view_with_a_valid_slug(self):
        """
        After calling remove_bookmark view, the user must have one bookmark less.
        """
        song = create_song(published=True)
        self.user.bookmarks.add(create_song())
        num_bookmarks = self.user.bookmarks.count()

        self.user.bookmarks.remove(song)
        self.assertTrue(self.user.bookmarks.count(), num_bookmarks - 1)


class SearchViewTests(TestCase):
    def test_without_query(self):
        """
        Search view should display published songs.
        """
        response = self.client.get(reverse('chords:search'))
        self.assertContains(response, 'Search for songs, users and artists')

    def test_search_user(self):
        """
        Search view should search for users when requested.
        """
        create_user(username='User')
        create_song(title='User', published=True)

        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=User'.format(SearchForm.SEARCH_USER))
        self.assertQuerysetEqual(response.context['results'], ['<User: User>'])

    def test_search_artist(self):
        """
        Search view should search for artists when requested.
        """
        create_artist(name='Artist')
        create_user(username='Artist')

        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=Artist'.format(SearchForm.SEARCH_ARTIST))
        self.assertQuerysetEqual(response.context['results'], ['<Artist: Artist>'])

    def test_search_song_with_an_unpublished_song(self):
        """
        Search view should not display unpublished songs.
        """
        create_song(title='Random Song', published=False)
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=Random Song'.format(SearchForm.SEARCH_SONG))
        self.assertQuerysetEqual(response.context['results'], [])
        self.assertContains(response, 'No results')

    def test_search_song_with_no_exact_title(self):
        """
        Search view should match a song even when only a part of the title is
        given and by ingoring case.
        """
        create_song(title='Song', published=True)

        for k in ['song', 'SONG', 'sOnG', 'σονγ', ' song ', 'on', 's']:
            response = self.client.get(reverse('chords:search') +
                '?searchBy={0}&keywords={1}'.format(SearchForm.SEARCH_SONG, k))
            self.assertQuerysetEqual(response.context['results'], ['<Song: Song>'])

    def test_search_song_results_are_sorted_by_name_ascending(self):
        """
        The resuls must be sorted by name in ascending order.
        """
        create_song(title='Beta Song', published=True)
        create_song(title='Gamma Song', published=True)
        create_song(title='Alpha Song', published=True)
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=Song'.format(SearchForm.SEARCH_SONG))

        self.assertQuerysetEqual(response.context['results'],
            ['<Song: Alpha Song>', '<Song: Beta Song>', '<Song: Gamma Song>'])

    def test_search_song_genre_all_or_specific(self):
        """
        Searh view must return only songs of the requested genre.
        """
        s1 = create_song(title='Song Rock', genre=Song.ROCK, published=True)
        s2 = create_song(title='Song Blues', genre=Song.BLUES, published=True)

        # by default all genres are included
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=Song'.format(SearchForm.SEARCH_SONG))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Blues>', '<Song: Song Rock>'])

        # test GENRE_ALL option
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&genre={1}&keywords=Song'.format(
                SearchForm.SEARCH_SONG, SearchForm.GENRE_ALL))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Blues>', '<Song: Song Rock>'])

        # test that we get only rock songs
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&genre={1}&keywords=Song'.format(
                SearchForm.SEARCH_SONG, Song.ROCK))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Rock>'])

    def test_search_song_include_tabs(self):
        """
        Searh view must not return songs with tabs when not requested.
        """
        s1 = create_song(title='Song Tabs', tabs=True, published=True)
        s2 = create_song(title='Song Chords', tabs=False, published=True)

        # by default include tabs
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&keywords=Song'.format(SearchForm.SEARCH_SONG))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Chords>', '<Song: Song Tabs (+t)>'])

        # test INCLUDE_TABS option
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&tabs={1}&keywords=Song'.format(
                SearchForm.SEARCH_SONG, SearchForm.INCLUDE_TABS))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Chords>', '<Song: Song Tabs (+t)>'])

        # test CHORDS_ONLY option
        response = self.client.get(reverse('chords:search') +
            '?searchBy={0}&tabs={1}&keywords=Song'.format(
                SearchForm.SEARCH_SONG, SearchForm.CHORDS_ONLY))
        self.assertQuerysetEqual(response.context['results'],
                ['<Song: Song Chords>'])


class RecentlyAddedViewTests(TestCase):
    def test_with_unpublished_song(self):
        """
        Recently_added view should not display unpublished songs.
        """
        create_song(title='Unpublished', published=False)
        response = self.client.get(reverse('chords:recently_added'))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_most_recent_comes_first(self):
        """
        More recent songs must be displayed first in the recently_added view.
        """
        create_song(title='Published First', published=True)
        create_song(title='Published Second', published=True)
        response = self.client.get(reverse('chords:recently_added'))
        self.assertQuerysetEqual(response.context['songs'],
                ['<Song: Published Second>', '<Song: Published First>'])


class PopularViewTests(TestCase):
    def test_with_unpublished_song(self):
        """
        Popular view should not display unpublished songs.
        """
        create_song(title='Unpublished', published=False)
        response = self.client.get(reverse('chords:popular'))
        self.assertQuerysetEqual(response.context['songs'], [])

    def test_most_popular_comes_first(self):
        """
        More popular songs must be displayed first in the popular view.
        """
        song1 = create_song(title='Song1', published=True)
        song2 = create_song(title='Song2', published=True)
        song1.viewedBy.add(create_user(username='user1'))

        response = self.client.get(reverse('chords:popular'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Song1>', '<Song: Song2>'])

        song2.viewedBy.add(create_user(username='user2'))
        song2.viewedBy.add(create_user(username='user3'))

        response = self.client.get(reverse('chords:popular'))
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Song2>', '<Song: Song1>'])


class ContactViewTests(LoginedTestCase):
    def test_with_valid_data(self):
        """
        Contact view should redirect to contact_done view, after posting to it
        valid data.
        """
        response = self.client.post(reverse('chords:contact'), valid_contact_data())
        self.assertRedirects(response, reverse('chords:contact_done'))

    def test_addsong_view_with_invalid_input(self):
        """
        The contact view must return an appropriate message for each case of
        invalid POST data.
        """
        # missing name
        response = self.client.post(reverse('chords:contact'),
                valid_contact_data(name=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        # missing email
        response = self.client.post(reverse('chords:contact'),
                valid_contact_data(email=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        # email must be valid
        response = self.client.post(reverse('chords:contact'),
                valid_contact_data(email='junk data'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid email address.')
        # missing subject
        response = self.client.post(reverse('chords:contact'),
                valid_contact_data(subject=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        # missing body
        response = self.client.post(reverse('chords:contact'),
                valid_contact_data(body=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
