from django.contrib.auth.models import User

from chords.models import Artist, Song


def create_artist(name='Some Artist'):
    artist = Artist(name=name)
    artist.save()
    return artist

def create_song(title='Random Song', artist=None, sender=None, published=True,
                tabs=False, genre=None):
    song = Song(title=title, artist=artist, sender=sender, published=published,
                tabs=tabs)
    if genre is not None:
        song.genre = genre
    song.save()
    return song

def create_user(username='username', password='password'):
    user = User.objects.create_user(username=username, password=password)
    user.save()
    return user

def valid_song_data(title='Title', artist_txt='artist_txt', user_txt='user_txt',
                    genre=Song.POP, video='http://www.example.com', tabs=True,
                    content='content'):
    return {
        'title' : title, 'artist_txt' : artist_txt, 'user_txt' : user_txt,
        'genre' : genre, 'video' : video, 'tabs' : tabs, 'content' : content
    }

def valid_contact_data(name='Name', email='example@example.com',
                       subject='Subject', body='Message'):
    return {
        'name' : name, 'email' : email,
        'subject': subject, 'body' : body
    }
