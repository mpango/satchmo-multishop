# encoding: utf-8
from django import template
from satchmo_store.shop.models import Order
from multishop.listeners import multiorder_update_shipping

register = template.Library()


def order_details(context, order, default_view_tax=False):
	"""Output a formatted block giving order details."""
	multiorder_update_shipping(order)
	
	return {
		'multishop_orders' : order.childorder_set.all(),
		'order': order,
		'default_view_tax' : default_view_tax,
		'request' : context['request']
	}
register.inclusion_tag('shop/_multishop_order_details.html', takes_context=True)(order_details)

# def shop_segmented_cart_display(cart, sale):
#	"""
#	Renders a list of products in the current Cart, grouped by their
#	corresponding original shops. Used only for multishop Orders.
#	"""
#	
#	return {
#		'multicart' : [segment for segment in segmented_items.values()],
#		'sale': sale,
#	}
# register.inclusion_tag('multishop/_shop_segmented_cart_display.html')(shop_segmented_cart_display)
