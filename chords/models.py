from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models import Count

from .utils import generate_unique_slug, strip_whitespace_lines


class Artist(models.Model):
    # names are stored in the "Surname Name" format
    name = models.CharField(max_length=80)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if self.id is None:
            self.slug = generate_unique_slug(Artist, self.name, slug_max_length)
            MyCache.incr_value(MyCache.Keys.ARTISTS_COUNT)

        super(Artist, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        MyCache.decr_value(MyCache.Keys.ARTISTS_COUNT)
        super(Artist, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chords:artist', kwargs={'artist_slug' : self.slug})

    def __str__(self):
        return self.name


class Song(models.Model):
    BLUES = 'BLU'
    CLASSIC = 'CLA'
    CHANT = 'CHA'
    ENTEXNO = 'EDE'
    LAIKO = 'LAI'
    METAL = 'MET'
    POP = 'POP'
    PUNK = 'PUN'
    RAP = 'RAP'
    REGGAE = 'REG'
    ROCK = 'ROC'
    TRADITIONAL = 'TRA'
    OTHER = 'OTH'

    GENRE_CHOICES = (
        (BLUES, 'Blues'),
        (CLASSIC, 'Classic'),
        (CHANT, 'Chant'),
        (ENTEXNO, 'Entexno'),
        (LAIKO, 'Laiko'),
        (METAL, 'Metal'),
        (POP, 'Pop'),
        (PUNK, 'Punk'),
        (RAP, 'Rap'),
        (REGGAE, 'Reggae'),
        (ROCK, 'Rock'),
        (TRADITIONAL, 'Traditional'),
        (OTHER, 'Other'),
    )

    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True,
                               related_name='songs')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                               blank=True, related_name='songs')
    bookmarkedBy = models.ManyToManyField(User, related_name='bookmarks',
                                          verbose_name='Bookmarked by')
    viewedBy = models.ManyToManyField(User, related_name='viewed')
    content = models.TextField(default='')
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default=ENTEXNO)
    video = models.URLField(blank=True)
    tabs = models.BooleanField('Contain tabs', default=False)
    published = models.BooleanField(default=False)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    pub_date = models.DateTimeField('date published', null=True, blank=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if self.id is None:
            self.slug = generate_unique_slug(Song, self.title, slug_max_length)

        self.content = strip_whitespace_lines(self.content)
        if self.video:
            self.video = self.get_embed_video_url()

        super(Song, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.unpublish()
        super(Song, self).delete(*args, **kwargs)

    def publish(self):
        self.published = True
        self.pub_date = timezone.now()
        MyCache.incr_value(MyCache.Keys.PUBLISHED_SONGS_COUNT)
        MyCache.delete_recent_songs()
        self.save()

    def unpublish(self):
        self.published = False
        self.pub_date = None
        MyCache.decr_value(MyCache.Keys.PUBLISHED_SONGS_COUNT)
        MyCache.delete_recent_songs()
        self.save()

    def get_embed_video_url(self):
        if 'www.youtube.com' in self.video:
            if '/embed/' in self.video:
                return self.video

            video_id = self.video.split('watch?')[1].split('v=')[1].split('&')[0]
            return 'https://www.youtube.com/embed/{0}?feature=player_detailpage'\
                .format(video_id)

        if 'www.dailymotion.com' in self.video:
            if '/embed/' in self.video:
                return self.video

            video_id = self.video.split('video/')[1].split('_')[0]
            return 'http://www.dailymotion.com/embed/video/{0}'.format(video_id)

        if 'vimeo.com' in self.video:
            if 'player.vimeo.com' in self.video:
                return self.video

            video_id = self.video.split('vimeo.com/')[1].split('?')[0]
            return 'http://player.vimeo.com/video/{0}'.format(video_id)

        return self.video

    def genre_str(self):
        return self.get_genre_display()

    def full_title(self):
        full_title = '{0} - {1}'.format(self.artist, self.title)
        return full_title + ' (+t)' if self.tabs else full_title

    def tojson(self):
        artist = self.artist.name if self.artist else None
        sender = self.sender.username if self.sender else None
        return {
            'title'         : self.title,
            'artist'        : artist,
            'sender'        : sender,
            'content'       : self.content,
            'genre'         : self.genre_str(),
            'video'         : self.video,
            'tabs'          : self.tabs,
            'registered'    : self.reg_date,
            'published'     : self.pub_date,
            'last_modified' : self.mod_date,
            }

    def get_absolute_url(self):
        return reverse('chords:song', kwargs={'song_slug' : self.slug})

    def __str__(self):
        return self.title + ' (+t)' if self.tabs else self.title


class Comment(models.Model):
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                             related_name='comments')
    song = models.ForeignKey(Song, on_delete=models.CASCADE,
                             related_name='comments')

    def save(self, *args, **kwargs):
        self.content = strip_whitespace_lines(self.content)
        super(Comment, self).save(*args, **kwargs)


class MyCache:
    class Keys:
        PUBLISHED_SONGS_COUNT = 'published_songs_count'
        ARTISTS_COUNT = 'artists_count'
        USER_COUNT = 'users_count'
        MOST_POPULAR_SONGS = 'most_popular_songs'
        MOST_RECENT_SONGS = 'most_recent_songs'

    def popular_songs():
        key = MyCache.Keys.MOST_POPULAR_SONGS
        songs = cache.get(key, None)
        if songs is None:
            print("DB READ - most popular songs")
            songs = Song.objects.filter(published=True).annotate(
                    popularity=Count('viewedBy') + 2 * Count('bookmarkedBy')
                    ).order_by('-popularity')

            # cache the result for a day
            cache.set(key, songs, 86400)
        return songs

    def recent_songs():
        key = MyCache.Keys.MOST_RECENT_SONGS
        songs = cache.get(key, None)
        if songs is None:
            print("DB READ - most recent songs")
            songs = Song.objects.filter(published=True).order_by('-pub_date')
            cache.set(key, songs)
        return songs

    def delete_recent_songs():
        cache.delete(MyCache.Keys.MOST_RECENT_SONGS)

    def published_songs_count():
        key = MyCache.Keys.PUBLISHED_SONGS_COUNT
        count = cache.get(key, None)
        if count is None:
            print("DB READ - published songs count")
            count = Song.objects.filter(published=True).count()
            cache.set(key, count)
        return count

    def artists_count():
        key = MyCache.Keys.ARTISTS_COUNT
        count = cache.get(key, None)
        if count is None:
            print("DB READ - artists count")
            count = Artist.objects.count()
            cache.set(key, count)
        return count

    def users_count():
        key = MyCache.Keys.USER_COUNT
        count = cache.get(key, None)
        if count is None:
            print("DB READ - users count")
            count = User.objects.count()
            cache.set(key, count)
        return count

    def incr_value(key):
        try:
            cache.incr(key)
        except ValueError:
            pass

    def decr_value(key):
        try:
            cache.decr(key)
        except ValueError:
            pass
