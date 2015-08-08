from django.forms import ModelForm, CharField, Textarea

from .models import Song


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
