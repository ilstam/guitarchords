from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^song/(?P<song_slug>[\w\-]+)/$', views.song, name='song'),
    url(r'^artist/(?P<artist_slug>[\w\-]+)/$', views.artist, name='artist'),
    url(r'^add_song/$', views.add_song, name='add_song'),
    url(r'^verify_song/$', views.verify_song, name='verify_song'),
    url(r'^song_submitted/$', views.song_submitted, name='song_submitted'),
    url(r'^user/(?P<username>[\w]+)/$', views.user, name='user'),
    url(r'^search/$', views.search, name='search'),
    url(r'^bookmarks/$', views.bookmarks, name='bookmarks'),
]
