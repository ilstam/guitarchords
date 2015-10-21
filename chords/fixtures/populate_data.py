# Include this module into a population script.
# Remember to setup the django environment before calling populate().

import os
import xml.etree.ElementTree as etree

from chords.models import Artist, Song, User


DATA_PATH = os.path.join(os.path.dirname(__file__), 'data.xml')


def add_user(username='username', password='password'):
    try:
        user = User.objects.filter(username=username)[0]
    except IndexError:
        user = User.objects.create_user(username=username, password=password)
        user.save()

    return user

def add_artist(name):
    a = Artist.objects.get_or_create(name=name)[0]
    a.save()
    return a

def add_song(title, artist, sender=None, content='', genre='', video='',
             tabs=False, published=False):
    artist = Artist.objects.get(name=artist)
    s = Song.objects.get_or_create(title=title, artist=artist)[0]
    s.sender = User.objects.get(username=sender)
    s.content = content
    s.genre = genre
    s.video = video
    s.tabs = tabs
    s.published = published
    if published:
        s.publish()
    s.save()
    return s

def populate():
    tree = etree.parse(DATA_PATH)
    root = tree.getroot()

    for user in root.findall('user'):
        add_user(**user.attrib)

    for artist in root.findall('artist'):
        add_artist(**artist.attrib)

    for song in root.findall('song'):
        data = song.attrib
        data['content'] = song.text
        add_song(**data)
