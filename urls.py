from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

grid_patterns = patterns('',
    url(r'^$', 'grid.views.index'),
    url(r'scores/$', 'grid.views.scores')
)

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^grid/', include(grid_patterns)),
)
