# encoding: utf-8
from django import template
from satchmo_store.shop.models import Order

register = template.Library()

def shop_segmented_cart_display(cart, sale):
	"""
	Renders a list of products in the current Cart, grouped by their
	corresponding original shops. Used only for multishop Orders.
	"""
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
	}
register.inclusion_tag('multishop/_shop_segmented_cart_display.html')(shop_segmented_cart_display)
