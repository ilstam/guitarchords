from django.contrib import admin

from .models import Artist, Song


admin.AdminSite.site_title = 'Chords administration'
admin.AdminSite.site_header = 'Chords Administration'

class ArtistAdmin(admin.ModelAdmin):
    exclude = ['slug']
    actions = ['delete_selected']
    search_fields = ['name']

    def delete_selected(self, request, queryset):
        for artist in queryset:
            artist.delete()

    delete_selected.short_description = 'Delete selected artists (custom)'

class SongAdmin(admin.ModelAdmin):
    fieldsets = [
        ('General',          {'fields': ['title', 'artist', 'genre']}),
        ('User information', {'fields': ['sender'], 'classes': ['collapse']}),
        ('Content',          {'fields': ['content', 'tabs', 'video']}),
        ('Published',        {'fields': ['published']}),
    ]

    list_display = ['full_title', 'reg_date', 'pub_date', 'published']
    list_filter = ['pub_date', 'reg_date', 'genre', 'tabs']
    search_fields = ['title', 'artist__name']
    actions = ['delete_selected', 'publish_songs', 'unpublish_songs']

    def publish_songs(self, request, queryset):
        for song in queryset:
            if not song.published:
                song.publish()

    publish_songs.short_description = 'Publish all selected songs'

    def unpublish_songs(self, request, queryset):
        for song in queryset:
            if song.published:
                song.unpublish()

    unpublish_songs.short_description = 'Unpublish all selected songs'

    def delete_selected(self, request, queryset):
        for artist in queryset:
            artist.delete()

    delete_selected.short_description = 'Delete selected songs (custom)'


admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
