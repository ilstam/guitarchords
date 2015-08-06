from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Artist, Song


def dummy_artist(name='Some Artist'):
    artist = Artist(name=name)
    artist.save()
    return artist

def dummy_song(title='Random Song', artist_name='Some Artist'):
    song = Song(title=title, artist=dummy_artist(name=artist_name))
    song.save()
    return song


class SongModelTests(TestCase):
    def test_slug_line_creation(self):
        """
        When we add a song, an appropriate slug must be created.
        """
        song = dummy_song(title='Random Song')
        self.assertEqual(song.slug, 'random-song')

    def test_slug_line_creation_greek(self):
        """
        When we add a song with a greek title, an appropriate slug must be
        created in english.
        """
        song = dummy_song(title='Τυχαίο όνομα από τραγούδι')
        self.assertEqual(song.slug, 'tyxaio-onoma-apo-tragoudi')

    def test_slugs_are_unique(self):
        """
        Song slugs must be always unique, even when they have the same title.
        """
        song1 = dummy_song()
        song2 = Song(title=song1.title, artist=song1.artist)
        song2.save()
        self.assertNotEqual(song1.slug, song2.slug)

    def test_slugs_are_of_appropriate_size(self):
        """
        Song slug must not exceed the specified length.
        """
        slug_length = 5
        song1 = Song(title='Random Song', artist=dummy_artist())
        song1.save(slug_max_length=slug_length)
        self.assertEqual(len(song1.slug), slug_length)


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

    def test_index_view_with_songs(self):
        """
        The most recently added songs should be displayed on the index page.
        """
        song = dummy_song('Random Song', 'Some Artist')
        response = self.client.get(reverse('chords:index'))
        self.assertContains(response, "Recently added songs", status_code=200)
        self.assertQuerysetEqual(response.context['songs'],
                                 ['<Song: Some Artist - Random Song>'])


class SongViewTests(TestCase):
    def test_song_view_with_an_invalid_slug(self):
        """
        The song view should return a 404 not found for invalid slugs.
        """
        song = dummy_song()
        response = self.client.get(reverse('chords:song',
                                   args=(song.slug+"invalid",)))
        self.assertEqual(response.status_code, 404)

    def test_song_view_with_a_valid_slug(self):
        """
        The song view should display song title for valid slugs.
        """
        song = dummy_song()
        response = self.client.get(reverse('chords:song', args=(song.slug,)))
        self.assertContains(response, song.title, status_code=200)
