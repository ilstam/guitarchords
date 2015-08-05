from django.db import models

from .utils import generate_unique_slug, greek_to_english_letters

class Artist(models.Model):
    # names are stored in the "Surname Name" format
    name = models.CharField(max_length=80)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist)
    content = models.TextField(default='')
    #genre = models.ForeignKey(Genre)
    video = models.URLField(default='')
    tabs = models.BooleanField('tablatures', default=False)
    #sender = models.ForeignKey(User)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True, max_length=60)

    def save(self, slug_max_length=-1, *args, **kwargs):
        if not self.id:
            # generate slug only when creating an object to avoid broken links
            slug_text = greek_to_english_letters(self.title)
            self.slug = generate_unique_slug(Song, slug_text, slug_max_length)

        super(Song, self).save(*args, **kwargs)

    def __str__(self):
        return '{0} - {1}'.format(self.artist, self.title)
