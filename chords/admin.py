from django.contrib import admin

from .models import Artist, Song, Bookmark


class ArtistAdmin(admin.ModelAdmin):
    exclude = ['slug']

class SongAdmin(admin.ModelAdmin):
    exclude = ['slug']


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Bookmark)
