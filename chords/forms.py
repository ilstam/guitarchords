from django.forms import ModelForm, Textarea

from .models import Song


class AddSongForm(ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'genre', 'video', 'tabs', 'content']
        widgets = {
            'content' : Textarea(attrs={'cols': 70, 'rows': 35}),
        }
