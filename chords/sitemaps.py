from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from .models import Artist, Song, User


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ['index', 'popular', 'recently_added', 'search', 'contact']

    def location(self, item):
        return reverse('chords:' + item)


class SongSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Song.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.mod_date


class ArtistSitemap(sitemaps.Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Artist.objects.all()


class UserSitemap(sitemaps.Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return User.objects.all()

    def location(self, user):
        return reverse('chords:user', args=(user.get_username(),))
