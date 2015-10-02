from django.core.cache import cache
from django.db.models import Count

from .models import Song


def get_popular_songs():
    songs = cache.get('most_popular_songs', None)
    if songs is not None:
        return songs

    # print("DB READ - most popular songs")
    songs = Song.objects.filter(published=True).annotate(
            popularity=Count('viewedBy') + 2 * Count('bookmarkedBy')
            ).order_by('-popularity')

    # cache the result for a day
    cache.set('most_popular_songs', songs, 86400)
    return songs

def get_recent_songs():
    songs = cache.get('most_recent_songs', None)
    if songs is not None:
        return songs

    # print("DB READ - most recent songs")
    songs = Song.objects.filter(published=True).order_by('-pub_date')
    cache.set('most_recent_songs', songs)
    return songs
