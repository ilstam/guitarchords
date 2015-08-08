from django.db import models
from django.utils import timezone

from .utils import generate_unique_slug, greek_to_english_letters


class Artist(models.Model):
    # names are stored in the "Surname Name" format
    name = models.CharField(max_length=80)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        slug_text = greek_to_english_letters(self.name)
        self.slug = generate_unique_slug(Artist, slug_text, slug_max_length)

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
        ('', '---'),
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
    artist = models.ForeignKey(Artist)
    content = models.TextField(default='')
    genre = models.CharField(max_length=3,
                             choices=GENRE_CHOICES,
                             default='',
                             blank=True)
    video = models.URLField(blank=True)
    tabs = models.BooleanField('tablatures', default=False)
    #sender = models.ForeignKey(User)
    published = models.BooleanField(default=False)
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    pub_date = models.DateTimeField('date published', null=True, blank=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True)

    def __init__(self, *args, **kwargs):
        super(Song, self).__init__(*args, **kwargs)
        self.old_published = self.published

    def save(self, slug_max_length=-1, *args, **kwargs):
        self.content = self.content.strip('\n')

        slug_text = greek_to_english_letters(self.title)
        self.slug = generate_unique_slug(Song, slug_text, slug_max_length)

        if self.old_published != self.published and self.published:
            self.pub_date = timezone.now()
        if self.old_published != self.published and not self.published:
            self.pub_date = None
        self.old_published = self.published

        super(Song, self).save(*args, **kwargs)

    def full_title(self):
        return '{0} - {1}'.format(self.artist, self.title)

    def genre_str(self):
        return self.get_genre_display()

    def __str__(self):
        return self.title

    def create_song_from_json(data, save=False):
        if save:
            artist = Artist(name=data['artist_txt'])
        else:
            # NullArtist serves testing purposes
            artist = Artist.objects.get_or_create(name='NullArtist')[0]
        artist.save()

        song = Song(
            title=data['title'],
            artist=artist,
            video=data['video'],
            genre=data['genre'],
            tabs=data['tabs'],
            content=data['content'],
        )

        if save:
            song.save()

        return song
