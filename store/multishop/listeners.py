# encoding: utf-8
from satchmo_store.shop.models import Order, OrderItem


def postprocess_order(sender, order=None, **kwargs):
	"""
	Postprocesses an order after it has successfully been created. Here we
	can check if the order belongs to a virtual shop and then split the items
	in it accordingly into multiple related Orders, each containing all the
	items of one distinct "real" shop.
	"""
	print "Initial Order created: %s"%order
	order_item_groups = get_order_item_groups_from_order(order)
	for site, order_item_group in order_item_groups.iteritems():
		new_order = create_copied_order_with_item_group_for_site(
			order, order_item_group, site)
		print "Created a copied order: %s"%new_order


def create_copied_order_with_item_group_for_site(order, order_item_group, site):
	"""
	Expects an original order and a group of OrderItems (of that order).
	A new Order will created, attributes copied from the original order but
	only containing the OrderItems of the group.
	"""
	new_order = copy_order_for_site(order, site)
	new_order.save()
	for order_item in order_item_group:
		new_order.orderitem_set.add(order_item)
	
	return new_order


def get_order_item_groups_from_order(order):
	"""
	Receives an order, iterates over all OrderItems and groups them into
	disjunct list of OrderItems, one for each site (shop) they originally
	belong to.
	"""
	item_groups = {}
	for item in order.orderitem_set.all():
		# create a "bucket" for the current site if not yet created
		if not item.product.site in item_groups.keys():
			item_groups[item.product.site] = []
		
		# add the item to the correct bucket
		item_groups[item.product.site].append(item)
	
	return item_groups


def copy_order_for_site(order, site):
	"""Copies an order and returns the (unsaved) Order copy."""
	copied_order = Order(
		site = site,
		contact = order.contact,
		ship_addressee = order.ship_addressee,
		ship_street1 = order.ship_street1,
		ship_street2 = order.ship_street2,
		ship_city = order.ship_city,
		ship_state = order.ship_state,
		ship_postal_code = order.ship_postal_code,
		ship_country = order.ship_country,
		bill_addressee = order.bill_addressee,
		bill_street1 = order.bill_street1,
		bill_street2 = order.bill_street2,
		bill_city = order.bill_city,
		bill_state = order.bill_state,
		bill_postal_code = order.bill_postal_code,
		bill_country = order.bill_country,
		notes = order.notes,
		sub_total = order.sub_total,
		total = order.total,
		discount_code = order.discount_code,
		discount = order.discount,
		method = order.method,
		shipping_description = order.shipping_description,
		shipping_method = order.shipping_method,
		shipping_model = order.shipping_model,
		shipping_cost = order.shipping_cost,
		shipping_discount = order.shipping_discount,
		tax = order.tax,
		time_stamp = order.time_stamp,
		status = order.status)
	return copied_order