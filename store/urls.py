from django.conf.urls.defaults import *
from satchmo_store.urls import urlpatterns
from satchmo_utils.urlhelper import replace_urlpattern

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

# replacement = url(r'^cart/$', 'multishop.display', {}, 'satchmo_cart')
# replace_urlpattern(urlpatterns, replacement)

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'cms/', include('cms.urls')),
    url(r'^multishop/', include('multishop.urls')),
)
