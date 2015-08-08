from django.forms import ModelForm, Textarea, TextInput

from .models import Song


class AddSongForm(ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'genre', 'video', 'tabs', 'content']

        widgets = {
            'artist' : TextInput,
            'content' : Textarea(attrs={'cols': 70, 'rows': 35}),
        }

        labels = {
            'title' : 'Title',
            'artist' : 'Artist',
            'genre' : 'Genre',
            'video' : 'Video',
            'tabs' : 'Tabs',
            'content' : '',
        }

        help_texts = {
            'title' : 'required',
            'artist' : 'Surname Name format, required',
            'video' : 'Youtube etc.',
            'tabs' : 'does this version contain tabs?',
        }

        error_messages = {
            'content' : {
                'required' : "Remember to include the song!"
            },
        }
