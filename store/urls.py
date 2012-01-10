from django.conf.urls.defaults import *
from satchmo_store.urls import urlpatterns

from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns += patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'cms/', include('cms.urls')),
)
