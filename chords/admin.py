from django.contrib import admin

from .models import Artist, Song


admin.AdminSite.site_title = 'Chords administration'
admin.AdminSite.site_header = 'Chords Administration'

class ArtistAdmin(admin.ModelAdmin):
    exclude = ['slug']


class SongAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General',               {'fields': ['title', 'artist', 'genre']}),
        ('User information', {'fields': ['sender'], 'classes': ['collapse']}),
        ('Content',               {'fields': ['content', 'tabs', 'video']}),
        ('Published', {'fields': ['published']}),
    ]

    list_display = ['full_title', 'reg_date', 'pub_date', 'published']
    list_filter = ['pub_date', 'reg_date', 'genre', 'tabs']
    search_fields = ['sender__username', 'artist__name']
    actions = ['publish_songs', 'unpublish_songs']

    def publish_songs(self, request, queryset):
        queryset.update(published=True)
    publish_songs.short_description = 'Publish all selected songs'

    def unpublish_songs(self, request, queryset):
        queryset.update(published=False)
    unpublish_songs.short_description = 'Unpublish all selected songs'


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
