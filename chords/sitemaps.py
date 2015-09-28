from django.contrib.sitemaps import Sitemap

from .models import Song


class SongsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Song.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.mod_date
