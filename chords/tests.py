from django.test import TestCase

from .models import Artist, Song

class SongModelTests(TestCase):
    def test_slug_line_creation(self):
        """
        make sure that when we add a song an appropriate slug line is created
        i.e. "Random Song" from "Some Artist"-> "artist-random-song"
        """
        artist = Artist(name='Some', surname='Artist')
        artist.save()
        song = Song(title='Random Song', artist=artist)
        song.save()
        self.assertEqual(song.slug, 'artist-random-song')

    def test_slug_line_creation_greek(self):
        """
        make sure that when we add a song with greek title an appropriate slug
        line in english is created
        i.e. "Τυχαίο Τραγούδι" from "Κάποιος Καλλιτέχνης"-> "kallitexnis-tyxaio-tragoudi"
        """
        artist = Artist(name='Κάποιος', surname='Καλλιτέχνης')
        artist.save()
        song = Song(title='Τυχαίο Τραγούδι', artist=artist)
        song.save()
        self.assertEqual(song.slug, 'kallitexnhs-tyxaio-tragoudi')

    def test_slugs_are_unique_and_of_appropriate_size(self):
        """
        make sure that slugs do not exceed the specified length and are always
        unique (even with same title and artist)
        """
        slug_length = 8

        artist = Artist(name='Some', surname='Artist')
        artist.save()

        song1 = Song(title='Random Song', artist=artist)
        song1.save(slug_max_length=slug_length)
        song2 = Song(title=song1.title, artist=artist)
        song2.save(slug_max_length=slug_length)

        self.assertEqual(len(song1.slug), slug_length)
        self.assertEqual(len(song2.slug), slug_length)
        self.assertNotEqual(song1.slug, song2.slug)
