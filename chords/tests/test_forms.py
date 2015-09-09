from django.test import TestCase

from chords.forms import AddSongForm, SearchForm
from .helper_functions import valid_song_data


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


class SearchFormTests(TestCase):
    def test_form_with_valid_data(self):
        """
        Form must be valid with sensible data.
        """
        form = SearchForm(data={'searchBy': SearchForm.SEARCH_SONG})
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        """
        Form cannot be valid if searchBy field is missing.
        """
        form = SearchForm()
        self.assertFalse(form.is_valid())
