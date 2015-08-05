from django.db import models

class Singer(models.Model):
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)

    def __str__(self):
        return "{0} {1}".format(self.name, self.surname) if self.name else self.surname

class Song(models.Model):
    title = models.CharField(max_length=100)
    singer = models.ForeignKey(Singer)
    content = models.TextField()
    #genre = models.ForeignKey(Genre)
    video = models.URLField(default="")
    tabs = models.BooleanField('tablatures')
    #sender = models.ForeignKey(User)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    mod_date = models.DateTimeField('last modified', auto_now=True)
    slug = models.SlugField(unique=True, max_length=60)

    def __str__(self):
        return "{0}: {1}".format(self.singer, self.title)
