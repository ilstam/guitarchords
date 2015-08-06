from django.contrib import admin

from .models import Artist, Song


class ArtistAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

class SongAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
