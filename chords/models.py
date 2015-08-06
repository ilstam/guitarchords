from django.db import models
from django.utils import timezone

from .utils import generate_unique_slug, greek_to_english_letters


class Artist(models.Model):
    # names are stored in the "Surname Name" format
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if not self.id:
            # generate slug only when creating an object to avoid broken links
            slug_text = greek_to_english_letters(self.name)
            self.slug = generate_unique_slug(Artist, slug_text, slug_max_length)

        super(Artist, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    content = models.TextField(default='')
    #genre = models.ForeignKey(Genre)
    video = models.URLField(blank=True)
    tabs = models.BooleanField('tablatures', default=False)
    #sender = models.ForeignKey(User)
    published = models.BooleanField(default=False)
    # when the song initially submitted by a user for approval
    reg_date = models.DateTimeField('date registered', auto_now_add=True)
    # when the song actually published after approval
    pub_date = models.DateTimeField('date published', null=True, blank=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True, max_length=60)

    def __init__(self, *args, **kwargs):
        super(Song, self).__init__(*args, **kwargs)
        self.old_published = self.published

    def save(self, slug_max_length=-1, *args, **kwargs):
        if not self.id:
            # generate slug only when creating an object to avoid broken links
            slug_text = greek_to_english_letters(self.title)
            self.slug = generate_unique_slug(Song, slug_text, slug_max_length)

        self.content = self.content.strip('\n')

        if self.old_published != self.published and self.published:
            self.pub_date = timezone.now()
        self.old_published = self.published

        super(Song, self).save(*args, **kwargs)

    def full_title(self):
        return '{0} - {1}'.format(self.artist, self.title)

    def __str__(self):
        return self.title
