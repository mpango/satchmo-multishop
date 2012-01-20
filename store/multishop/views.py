# encoding: utf-8
from django import forms
from django import http
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from product.models import Product, Category
import logging
import os
import urllib

log = logging.getLogger('satchmo_store.shop.views')


#
# TODO: perform a proper auth check here! (maybe using django-rulez?)
@login_required
def selection_index(request):
	"""docstring for multishop_selection_index"""
	productlist_url = reverse('multishop.views.productlist')
	return render_to_response('multishop/selection_index.html', {
		'productlist_url': productlist_url
	}, context_instance=RequestContext(request))



#
# TODO: perform a proper auth check here! (maybe using django-rulez?)
@login_required
def categorylist(request):
	r = ['<ul class="jqueryFileTree">']
	try:
		r = ['<ul class="jqueryFileTree">']
		shop_id = urllib.unquote(request.POST.get('dir', ''))
		if shop_id == '':
			for site in Site.objects.all():
				r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' %(site.id, site.name))
		else:
			try:
				shop_id = shop_id[:-1]
				site = Site.objects.get(id__exact=int(shop_id))
				for site in Category.objects.by_site(site):
					r.append('<li class="file"><a href="#" rel="%s">%s</a></li>' %(site.id, site.name))
			except Exception, e:
				r.append('Could not load shop: %s' % str(e))
		# r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
		# r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
		r.append('</ul>')
	except Exception, e:
		r.append('Could not load index: %s' % str(e))
	r.append('</ul>')
	return HttpResponse(''.join(r))



#
# TODO: perform a proper auth check here! (maybe using django-rulez?)
@login_required
def productlist(request):
	r = ['<ul class="productList">']
	try:
		r = ['<ul class="productList">']
		shop_id = urllib.unquote(request.POST.get('dir', ''))
		if shop_id == '':
			for site in Site.objects.all():
				r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' %(site.id, site.name))
		else:
			try:
				shop_id = shop_id[:-1]
				site = Site.objects.get(id__exact=int(shop_id))
				for site in Category.objects.by_site(site):
					r.append('<li class="file"><a href="#" rel="%s/">%s</a></li>' %(site.id, site.name))
			except Exception, e:
				r.append('Could not load shop: %s' % str(e))
		# r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
		# r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e,ff,f))
		r.append('</ul>')
	except Exception, e:
		r.append('Could not load index: %s' % str(e))
	r.append('</ul>')
	return HttpResponse(''.join(r))



