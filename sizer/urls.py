from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^db/', include('db.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    # Examples:
    # url(r'^$', 'sizer.views.home', name='home'),
    # url(r'^sizer/', include('sizer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
