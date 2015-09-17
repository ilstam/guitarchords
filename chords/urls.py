from django.conf.urls import url

from . import views


song_path = r'^song/(?P<song_slug>[\w\-]+)'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(song_path + '/$', views.song, name='song'),
    url(song_path + '/.json/$', views.song_json, name='song_json'),
    url(r'^artist/(?P<artist_slug>[\w\-]+)/$', views.artist, name='artist'),
    url(r'^add_song/$', views.add_song, name='add_song'),
    url(r'^verify_song/$', views.verify_song, name='verify_song'),
    url(r'^song_submitted/$', views.song_submitted, name='song_submitted'),
    url(r'^user/(?P<username>[\w]+)/$', views.user, name='user'),
    url(r'^popular/$', views.popular, name='popular'),
    url(r'^search/$', views.search, name='search'),
    url(r'^bookmarks/$', views.bookmarks, name='bookmarks'),
    url(song_path + '/add_bookmark/$', views.add_bookmark, name='add_bookmark'),
    url(song_path + '/remove_bookmark/$', views.remove_bookmark, name='remove_bookmark'),
]
