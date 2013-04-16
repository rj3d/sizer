from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.display_dropbox_user_info, name='index')
)