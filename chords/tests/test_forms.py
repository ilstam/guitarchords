from django.test import TestCase

import os

from chords.forms import AddCommentForm, AddSongForm, ContactForm, SearchForm
from .helper_functions import (create_user, create_song, valid_song_data,
                               valid_contact_data)


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
        self.assertFalse(AddSongForm().is_valid())
        # title required
        self.assertFalse(AddSongForm(valid_song_data(title='')).is_valid())
        # artist_txt required
        self.assertFalse(AddSongForm(valid_song_data(artist_txt='')).is_valid())
        # genre required
        self.assertFalse(AddSongForm(valid_song_data(genre=None)).is_valid())
        # invalid video url
        self.assertFalse(AddSongForm(valid_song_data(video='invalid_url')).is_valid())


class AddCommentFormTests(TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.valid_data = {
            'user' : create_user().id,
            'song' : create_song().id,
            'content': 'comment',
            'g-recaptcha-response' : 'PASSED'
        }

    def tearDown(self):
        os.environ['RECAPTCHA_TESTING'] = 'False'

    def test_form_with_valid_data(self):
        """
        Form must be valid with sensible data.
        """
        self.assertTrue(AddCommentForm(self.valid_data).is_valid())

    def test_form_with_invalid_data(self):
        """
        Test form with invalid data.
        """
        self.assertFalse(AddCommentForm().is_valid())

        # user required
        data = self.valid_data.copy()
        data['user'] = ''
        self.assertFalse(AddCommentForm(data).is_valid())

        # user must exist
        data = self.valid_data.copy()
        data['user'] = -1
        self.assertFalse(AddCommentForm(data).is_valid())

        # song required
        data = self.valid_data.copy()
        data['song'] = ''
        self.assertFalse(AddCommentForm(data).is_valid())

        # song must exist
        data = self.valid_data.copy()
        data['song'] = -1
        self.assertFalse(AddCommentForm(data).is_valid())

        # content required
        data = self.valid_data.copy()
        data['content'] = ''
        self.assertFalse(AddCommentForm(data).is_valid())

        # g-recaptcha-response required
        data = self.valid_data.copy()
        data['g-recaptcha-response'] = ''
        self.assertFalse(AddCommentForm(data).is_valid())


class ContactFormTests(TestCase):
    def test_form_with_valid_data(self):
        """
        Form must be valid with sensible data.
        """
        self.assertTrue(ContactForm(valid_contact_data()).is_valid())

    def test_form_with_invalid_data(self):
        """
        Test form with invalid data.
        """
        self.assertFalse(ContactForm().is_valid())

        # name required
        form = ContactForm(valid_contact_data(name=''))
        self.assertFalse(form.is_valid())
        # email required
        form = ContactForm(valid_contact_data(email=''))
        self.assertFalse(form.is_valid())
        # email must be valid
        form = ContactForm(valid_contact_data(email='junk string'))
        self.assertFalse(form.is_valid())
        # subject required
        form = ContactForm(valid_contact_data(subject=''))
        self.assertFalse(form.is_valid())
        # body required
        form = ContactForm(valid_contact_data(body=''))
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
        self.assertFalse(SearchForm().is_valid())
