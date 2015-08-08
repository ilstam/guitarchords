from django.forms import ModelForm, CharField, Textarea

from .models import Song
from .utils import strip_whitespace_lines


class AddSongForm(ModelForm):
    artist_txt = CharField(
            max_length=100,
            label='Artist',
            help_text='Surname Name format, required'
    )

    class Meta:
        model = Song
        fields = ['title', 'artist_txt', 'genre', 'video', 'tabs', 'content']

        widgets = {
            'content' : Textarea(attrs={'cols': 70, 'rows': 35}),
        }

        labels = {
            'title' : 'Title',
            'genre' : 'Genre',
            'video' : 'Video',
            'tabs' : 'Tabs',
            'content' : '',
        }

        help_texts = {
            'title' : 'required',
            'video' : 'Youtube etc.',
            'tabs' : 'does this version contain tabs?',
        }

        error_messages = {
            'content' : {
                'required' : "Remember to include the song!"
            },
        }

    def clean(self):
        self.cleaned_data['content'] = strip_whitespace_lines(
                self.cleaned_data['content'])

        video_url = self.cleaned_data['video']
        if video_url and not (video_url.startswith('http://')
        or video_url.startswith('https://')):
            self.cleaned_data['video'] = 'http://' + video_url

        return self.cleaned_data
