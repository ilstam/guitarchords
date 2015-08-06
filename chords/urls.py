from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^song/(?P<song_slug>[\w\-]+)/$', views.song, name='song'),
    url(r'^artist/(?P<artist_slug>[\w\-]+)/$', views.artist, name='artist'),
    url(r'^about/$', views.about, name='about'),
]
