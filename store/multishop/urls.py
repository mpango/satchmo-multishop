# encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('multishop.views',
	(r'index/categorylist/(?P<shop_id>\d)/$', 'categorylist'),
	(r'index/categorylist/$',                 'categorylist'),
	(r'productlist/(?P<cat_id>\d)/$',         'productlist'),
	(r'index/$',                              'selection_index'),
)