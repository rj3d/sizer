from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^treemap', views.render_treemap, name='treemap'),
    url(r'^my_treemap', views.render_treemap, name='my_treemap'),
    url(r'^zoomable_treemap', views.render_zoomable_treemap, name='zoomable_treemap'),
    url(r'^sunburst', views.render_sunburst, name='flare'),
    url(r'^json', views.render_filesystem_json, name='json')
)