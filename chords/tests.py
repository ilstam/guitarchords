from django.test import TestCase

from .models import Artist, Song


class SongModelTests(TestCase):
    def test_slug_line_creation(self):
        """
        make sure that when we add a song an appropriate slug line is created
        i.e. "Random Song" -> "random-song"
        """
        artist = Artist(name='Some Artist')
        artist.save()
        song = Song(title='Random Song', artist=artist)
        song.save()
        self.assertEqual(song.slug, 'random-song')

    def test_slug_line_creation_greek(self):
        """
        make sure that when we add a song with greek title an appropriate slug
        line in english is created
        i.e. "Τυχαίο όνομα από τραγούδι" -> "tyxaio-onoma-apo-tragoudi"
        """
        artist = Artist(name='Κάποιος Καλλιτέχνης')
        artist.save()
        song = Song(title='Τυχαίο όνομα από τραγούδι', artist=artist)
        song.save()
        self.assertEqual(song.slug, 'tyxaio-onoma-apo-tragoudi')

    def test_slugs_are_unique(self):
        """
        make sure that slugs are always unique, even with same title and artist
        """
        artist = Artist(name='Some Artist')
        artist.save()
        song1 = Song(title='Random Song', artist=artist)
        song1.save()
        song2 = Song(title=song1.title, artist=artist)
        song2.save()

        self.assertNotEqual(song1.slug, song2.slug)

    def test_slugs_are_of_appropriate_size(self):
        """
        make sure that slugs do not exceed the specified length
        """
        slug_length = 5

        artist = Artist(name='Some Artist')
        artist.save()
        song1 = Song(title='Random Song', artist=artist)
        song1.save(slug_max_length=slug_length)

        self.assertEqual(len(song1.slug), slug_length)
