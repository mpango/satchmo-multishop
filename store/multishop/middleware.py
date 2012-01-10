# encoding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from product.models import Product
from product.modules.configurable.models import ConfigurableProduct
from product.views import adminviews
from satchmo_utils.views import bad_or_missing
# from satchmo_ext.satchmo_toolbar import listeners
# from satchmo_store import get_version

class MultishopProductVariationManagerMiddleware(object):
	"""
	This middleware needs to be added to settings.MIDDLEWARE_CLASSES. It will
	monkey-patch satchmo's default product variation manager, so it restricts
	access for non-superusers to only the products / productvariations they
	own (i.e. those that belong to their own site).
	"""
	
	def __init__(self):
		"""Store the old variation manager and then monkey-patch them."""
		self.satchmo_variation_manager = adminviews.variation_manager
		adminviews.variation_list = self.variation_list
		adminviews.variation_manager = self.variation_manager
		# listeners.add_toolbar_context = self.add_my_toolbar_context#(listeners.add_toolbar_context)
	
	
	def variation_list(self, request):
		products = Product.objects.filter(configurableproduct__in=ConfigurableProduct.objects.all())
		# Simply filter for the current user's site if he's not a superuser.
		if not request.user.is_superuser:
			products = products.filter(site__exact=request.user.get_profile().site)
		ctx = RequestContext(request, {
			'products' : products,
		})
		
		return render_to_response('product/admin/variation_manager_list.html',
		                          context_instance=ctx)
	
	
	def variation_manager(self, request, product_id = ""):
		# Slightly more complicated here, but again, only filter for the
		# current user's site if he's not a superuser. Redirect the actual
		# work to satchmo's original method. In essence this method here is
		# merely an authorization wrapper for #adminviews.variation_manager.
		try:
			if not request.user.is_superuser:
				Product.objects.get(id=product_id, site__exact=request.user.get_profile().site)
			return self.satchmo_variation_manager(request, product_id)
		except Product.DoesNotExist:
				return bad_or_missing(request, _('The product you have requested does not exist.'))
	
	
	# # def add_toolbar_context(self, func):
	# def add_my_toolbar_context(self, sender, context={}, **kwargs):
	# 	print "addind toolbar monkeypatch..."
	# 	st = {}
	# 	st['st_satchmo_version'] = get_version()
	# 	st['st_new_order_total'] = 111
	# 	context.update(st)
	# 	# def decorated_add_toolbar_context(sender, context={}, **kwargs):
	# 	# 	print "addind toolbar monkeypatch 2"
	# 	# 	# do some stuff
	# 	# 	response = func(sender, context, **kwargs)
	# 	# 	# more stuff
	# 	# 	return {}
	# 	# return decorated_add_toolbar_context
	
