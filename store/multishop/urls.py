# encoding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('multishop.views',
	(r'index/categorylist/(?P<shop_id>\d)/$', 'categorylist'),
	(r'index/categorylist/$',                 'categorylist'),
	(r'index/productlist/$',                  'productlist'),
	(r'index/$',                              'selection_index'),
	# (r'^articles/(\d{4})/$', 'news.views.year_archive'),
	# (r'^articles/(\d{4})/(\d{2})/$', 'news.views.month_archive'),
	# (r'^articles/(\d{4})/(\d{2})/(\d+)/$', 'news.views.article_detail'),
)