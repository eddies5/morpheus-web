from django.conf.urls import patterns, include, url
from morpheus.views import job_submit, check_status
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^submit$', job_submit),
    url(r'^$', 'morpheus.views.home', name='home'),
    url(r'^status$', check_status)
    # url(r'^morpheusweb/', include('morpheusweb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
