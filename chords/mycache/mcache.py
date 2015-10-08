from django.core.cache import cache
from django.db.models import Count

from .keys import Keys
from ..models import Artist, Song, User


def get_popular_songs():
    key = Keys.MOST_POPULAR_SONGS
    songs = cache.get(key, None)
    if songs is None:
        # print("DB READ - most popular songs")
        songs = Song.objects.filter(published=True).annotate(
                popularity=Count('viewedBy') + 2 * Count('bookmarkedBy')
                ).order_by('-popularity')

        # cache the result for a day
        cache.set(key, songs, 86400)
    return songs

def get_recent_songs():
    key = Keys.MOST_RECENT_SONGS
    songs = cache.get(key, None)
    if songs is None:
        # print("DB READ - most recent songs")
        songs = Song.objects.filter(published=True).order_by('-pub_date')
        cache.set(key, songs)
    return songs

def get_song_published_count():
    key = Keys.PUBLISHED_SONGS_COUNT
    count = cache.get(key, none)
    if count is None:
        # print("DB READ - published songs count")
        count = Song.objects.filter(published=True).count()
        cache.set(key, count)
    return count

def get_artist_count():
    key = Keys.ARTISTS_COUNT
    count = cache.get(key, none)
    if count is None:
        # print("DB READ - artists count")
        count = Artist.objects.count()
        cache.set(key, count)
    return count

def get_user_count():
    key = Keys.USER_COUNT
    count = cache.get(key, none)
    if count is None:
        # print("DB READ - users count")
        count = User.objects.count()
        cache.set(key, count)
    return count
