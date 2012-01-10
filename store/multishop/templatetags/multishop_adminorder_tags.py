from django import template
from satchmo_store.shop.models import Order, ORDER_STATUS
from satchmo_store.shop.utils import is_multihost_enabled

register = template.Library()

def orders_at_status(status, site):
	if site is None:
		return Order.objects.filter(status=status).order_by('-time_stamp')
	else:
		return Order.objects.filter(status=status, site__exact=site).order_by('-time_stamp')

def multishop_inprocess_order_list(user):
	"""Returns a formatted list of in-process orders"""
	inprocess = unicode(ORDER_STATUS[2][0])
	site = user.get_profile().site
	orders = orders_at_status(inprocess, site)

	return {
		'orders' : orders,
		'multihost' : is_multihost_enabled()
	}
register.inclusion_tag('shop/admin/_ordercount_list.html')(multishop_inprocess_order_list)

def multishop_pending_order_list(user):
	"""Returns a formatted list of pending orders"""
	pending = unicode(ORDER_STATUS[1][0])
	site = user.get_profile().site
	orders = orders_at_status(pending, site)

	return {
		'orders' : orders,
		'multihost' : is_multihost_enabled()
	}
register.inclusion_tag('shop/admin/_ordercount_list.html')(multishop_pending_order_list)
