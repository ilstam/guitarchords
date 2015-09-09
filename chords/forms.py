from django import forms

from .models import Song
from .utils import strip_whitespace_lines


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
            'video' : 'Video',
            'tabs'  : 'This version contain tabs',
        }
        help_texts = {
            'genre' : 'Pick the closest, or Other.',
            'video' : 'Optional. Youtube etc.',
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
