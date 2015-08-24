from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from .utils import generate_unique_slug, strip_whitespace_lines


class Artist(models.Model):
    # names are stored in the "Surname Name" format
    name = models.CharField(max_length=80)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if self.id is None:
            self.slug = generate_unique_slug(Artist, self.name, slug_max_length)

        super(Artist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Song(models.Model):
    BLUES = 'BLU'
    CLASSIC = 'CLA'
    CHANT = 'CHA'
    ENTEXNO = 'EDE'
    LAIKO = 'LAI'
    POP = 'POP'
    PUNK = 'PUN'
    RAP = 'RAP'
    REGGAE = 'REG'
    ROCK = 'ROC'
    TRADITIONAL = 'TRA'

    GENRE_CHOICES = (
        (BLUES, 'Blues'),
        (CLASSIC, 'Classic'),
        (CHANT, 'Chant'),
        (ENTEXNO, 'Entexno'),
        (LAIKO, 'Laiko'),
        (POP, 'Pop'),
        (PUNK, 'Punk'),
        (RAP, 'Rap'),
        (REGGAE, 'Reggae'),
        (ROCK, 'Rock'),
        (TRADITIONAL, 'Traditional'),
    )

    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(default='')
    genre = models.CharField(max_length=3, choices=GENRE_CHOICES, default=ENTEXNO)
    video = models.URLField(blank=True)
    tabs = models.BooleanField('tablatures', default=False)
    published = models.BooleanField(default=False)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    pub_date = models.DateTimeField('date published', null=True, blank=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if self.id is None:
            self.slug = generate_unique_slug(Song, self.title, slug_max_length)

        self.content = strip_whitespace_lines(self.content)

        if self.published and self.pub_date is None:
            self.pub_date = timezone.now()
        elif not self.published and self.pub_date is not None:
            self.pub_date = None

        super(Song, self).save(*args, **kwargs)

    def full_title(self):
        return '{0} - {1}'.format(self.artist, self.title)

    def genre_str(self):
        return self.get_genre_display()

    def __str__(self):
        return self.title

    def embed_video_url(self):
        return self.video.replace('watch?v=', 'embed/')


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} -> {1}'.format(self.user.username, self.song.full_title())
