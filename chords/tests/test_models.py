from django.test import TestCase
from django.utils import timezone

from chords.models import Artist, Song
from .helper_functions import create_artist, create_song


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
