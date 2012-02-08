from django import template
from satchmo_store.shop.models import Order, ORDER_STATUS
from satchmo_store.shop.utils import is_multihost_enabled

register = template.Library()

def shop_segmented_cart_display(cart, sale):
	"""Returns a formatted list of in-process orders"""
	segmented_items = {}
	for cart_item in cart.cartitem_set.all():
		site = cart_item.product.site
		if not segmented_items.get(site):
			segmented_items[site] = {
				'site': site,
				'cartitems': [] }
		segmented_items[site]['cartitems'].append(cart_item)
	
	return {
		'multicart' : [segment for segment in segmented_items.values()],
		'sale': sale,
		'multihost' : is_multihost_enabled()
	}
register.inclusion_tag('multishop/_shop_segmented_cart_display.html')(shop_segmented_cart_display)
