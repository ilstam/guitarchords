from django.contrib import admin

from .models import Artist, Song


class ArtistAdmin(admin.ModelAdmin):
    exclude = ['slug']

class SongAdmin(admin.ModelAdmin):
    exclude = ['slug', 'pub_date']


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
