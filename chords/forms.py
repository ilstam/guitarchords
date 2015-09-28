from django import forms
from django.conf import settings
from django.core.mail import send_mail

from .models import Song, Comment
from .utils import strip_whitespace_lines

from captcha.fields import ReCaptchaField


class AddSongForm(forms.ModelForm):
    artist_txt = forms.CharField(
            max_length=100,
            label='Artist',
            help_text='In Surname Name format.'
    )

    class Meta:
        model = Song
        fields = ['title', 'artist_txt', 'genre', 'video', 'content', 'tabs']

        widgets = {
            'content' : forms.Textarea(attrs={'cols': 70, 'rows': 35}),
        }
        labels = {
            'title' : 'Title',
            'genre' : 'Genre',
            'video' : 'Video (optional)',
            'tabs'  : 'This version contain tabs',
        }
        help_texts = {
            'genre' : 'Pick the closest, or Other.',
            'video' : 'Youtube, Vimeo, Dailymotion.',
        }
        error_messages = {
            'content' : {
                'required' : "Remember to include the song!"
            },
        }


    def clean(self):
        if 'content' in self.cleaned_data:
            self.cleaned_data['content'] = strip_whitespace_lines(
                    self.cleaned_data['content'])
        return self.cleaned_data


class AddCommentForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Comment
        exclude = ['pub_date']

        widgets = {
            'user' : forms.HiddenInput(),
            'song' : forms.HiddenInput(),
            'content' : forms.Textarea(attrs={'rows': 8}),
        }
        labels = {
            'content' : 'Leave a comment',
        }


class SearchForm(forms.Form):
    SEARCH_ARTIST = 'AR'
    SEARCH_SONG = 'SO'
    SEARCH_USER = 'US'

    SEARCHBY_CHOICES = (
        (SEARCH_ARTIST, 'Artist'),
        (SEARCH_SONG, 'Song'),
        (SEARCH_USER, 'User'),
    )

    GENRE_ALL = 'ALL'
    GENRE_CHOICES = ((GENRE_ALL, 'All'),) + Song.GENRE_CHOICES

    INCLUDE_TABS = 'IT'
    CHORDS_ONLY = 'CO'

    TABS_CHOICES = (
            (INCLUDE_TABS, 'Include Tabs'),
            (CHORDS_ONLY, 'Chords only'),
    )

    searchBy = forms.ChoiceField(label='Search by', choices=SEARCHBY_CHOICES)
    keywords = forms.CharField(label='Keywords', max_length=100, required=False)
    genre = forms.ChoiceField(label='Genre', choices=GENRE_CHOICES, required=False)
    tabs = forms.ChoiceField(label='Tabs', choices=TABS_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['keywords'].widget.attrs['placeholder'] = 'Search for...'

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    subject = forms.CharField(label='Subject', max_length=100)
    body = forms.CharField(label='Your message', widget=forms.Textarea())

    def send_email(self):
        to_email = getattr(settings, 'REGISTRATION_DEFAULT_FROM_EMAIL',
                           settings.DEFAULT_FROM_EMAIL)
        send_mail(
                subject=self.cleaned_data['subject'],
                message=self.cleaned_data['body'],
                from_email=self.cleaned_data['email'],
                recipient_list=[to_email],
                fail_silently=False
        )
