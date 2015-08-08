from django.test import TestCase, SimpleTestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import Artist, Song
from .forms import AddSongForm
from . import utils


def create_artist(name='Some Artist'):
    artist = Artist(name=name)
    artist.save()
    return artist

def create_song(title='Random Song', artist_name='Some Artist', artist=None,
                published=True):
    if artist is None:
        song = Song(title=title, artist=create_artist(name=artist_name))
    else:
        song = Song(title=title, artist=artist)
    song.published = published
    song.save()
    return song


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
        artist.name = "Some Other Name"
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
        song.title = "Some Other Name"
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
        self.assertContains(response, "There are no songs present at the moment.")
        self.assertNotContains(response, "Recently added songs")
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
        self.assertContains(response, "There are no songs present at the moment.")
        self.assertNotContains(response, "Recently added songs")
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


class ArtistViewTests(TestCase):
    def test_artist_view_with_an_invalid_slug(self):
        """
        The artist view should return a 404 not found for invalid slugs.
        """
        artist = create_artist()
        response = self.client.get(reverse('chords:artist',
                                   args=(artist.slug+"invalid",)))
        self.assertEqual(response.status_code, 404)

    def test_artist_view_with_a_valid_slug(self):
        """
        The artist view should display artist name for valid slugs.
        """
        artist = create_artist()
        response = self.client.get(reverse('chords:artist', args=(artist.slug,)))
        self.assertContains(response, artist.name, status_code=200)

    def test_artist_view_with_a_published_song(self):
        """
        The artist view should display song title for published songs.
        """
        song = create_song(published=True)
        response = self.client.get(reverse('chords:artist',
                                   args=(song.artist.slug,)))
        self.assertContains(response, song.title, status_code=200)

    def test_artist_view_with_a_unpublished_song(self):
        """
        The artist view should not display song title for un-published songs.
        """
        song = create_song(published=False)
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

    def test_nullartist_is_visible(self):
        """
        The Null Artist must not be visible and the artist view must return a
        404 not found.
        """
        artist = Artist.objects.get_or_create(name='NullArtist')[0]
        response = self.client.get(reverse('chords:artist', args=(artist.slug,)))
        self.assertEqual(response.status_code, 404)

class SongViewTests(TestCase):
    def test_song_view_with_an_invalid_slug(self):
        """
        The song view should return a 404 not found for invalid slugs.
        """
        song = create_song()
        response = self.client.get(reverse('chords:song',
                                   args=(song.slug+"invalid",)))
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


class AddSongFormTests(TestCase):
    def test_form_with_valid_data(self):
        """
        Form must be valid with sensible data.
        """
        data = {'title' : 'Title', 'artist_txt' : 'Artist', 'genre' : Song.POP,
                'video' : 'https://www.example.com', 'tabs' : True,
                'content' : 'content'
                }
        form = AddSongForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        """
        Form cannot be valid if any of title, artist_txt, genre or content
        is missing, or if we give an invalid url.
        """
        form = AddSongForm()
        self.assertFalse(form.is_valid())

        # title required
        data = {'title' : '', 'artist_txt' : 'Artist', 'genre' : Song.POP,
                'video' : 'https://www.example.com', 'tabs' : True,
                'content' : 'content'
                }
        form = AddSongForm(data=data)
        self.assertFalse(form.is_valid())

        # artist_txt required
        data = {'title' : 'Title', 'artist_txt' : '', 'genre' : Song.POP,
                'video' : 'https://www.example.com', 'tabs' : True,
                'content' : 'content'
                }
        form = AddSongForm(data=data)
        self.assertFalse(form.is_valid())

        # genre required
        data = {'title' : 'Title', 'artist_txt' : 'Artist', 'genre' : None,
                'video' : 'https://www.example.com', 'tabs' : True,
                'content' : 'content'
                }
        form = AddSongForm(data=data)
        self.assertFalse(form.is_valid())

        # invalid url
        data = {'title' : 'Title', 'artist_txt' : 'Artist', 'genre' : Song.POP,
                'video' : 'invalid_url', 'tabs' : True,
                'content' : 'content'
                }
        form = AddSongForm(data=data)
        self.assertFalse(form.is_valid())


class TestUtils(SimpleTestCase):
    def test_strip_whitespace_lines(self):
        """
        The strip_empty_lines() function should remove all empty lines from
        end and begging and any adjacent whitespace lines inside.
        """
        s1 = """


        some identation here


lorem ipsum

"""
        s2 = """        some identation here

lorem ipsum"""
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
