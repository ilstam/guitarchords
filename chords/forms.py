from django.forms import ModelForm, CharField, Textarea

from .models import Song
from .utils import strip_whitespace_lines


class AddSongForm(ModelForm):
    artist_txt = CharField(
            max_length=100,
            label='Artist',
            help_text='In Surname Name format.'
    )

    class Meta:
        model = Song
        fields = ['title', 'artist_txt', 'genre', 'video', 'content', 'tabs']

        widgets = {
            'content' : Textarea(attrs={'cols': 70, 'rows': 35}),
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
