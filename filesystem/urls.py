from django.conf.urls import patterns, url

from filesystem import views

urlpatterns = patterns('',
    url(r'^json', views.display_filesystem_json, name='json')
)