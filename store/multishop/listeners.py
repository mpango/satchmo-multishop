# encoding: utf-8
from decimal import Decimal
from satchmo_store.shop.models import Order, OrderItem
from shipping.config import shipping_method_by_key
from shipping.utils import update_shipping


# entry point triggered from satchmo_store.shop.signals.order_success
def postprocess_order(sender, order=None, **kwargs):
	"""
	Postprocesses an order after it has successfully been created. Here we
	can check if the order belongs to a multishop and then finally update
	the shipping costs of it's child Orders accordingly.
	"""
	if order.is_multishoporder:
		for child_order in order.childorder_set.all():
			update_shipping_cost_for_order(child_order)
			child_order.recalculate_total()
			child_order.save()


# entry point triggered from satchmo_store.shop.signals.satchmo_post_copy_item_to_order
def postprocess_order_item_add(cart=None, cartitem=None, order=None, orderitem=None, **kwargs):
	"""docstring for postprocess_order_item_add"""
	print "adding orderitem: %s to order: %s"%(orderitem, order)
	if order.is_multishoporder:
		site = orderitem.product.site
		
		# See if we already have a related order for this multishop order.
		# If we don't, create a new one.
		try:
			copied_order = Order.objects.get(multishop_order=order,
			                                 site=site)
		except Order.DoesNotExist:
			copied_order = copy_order_for_site(order, site)
			copied_order.save()
		
		copy_orderitem_to_order(orderitem, copied_order)
		# update_shipping_cost_for_order(new_order)
		copied_order.recalculate_total()
		copied_order.save()


# entry point triggered from satchmo_store.shop.signals.order_cancelled
def cancel_order(sender, order=None, **kwargs):
	"""Invoked when an Order is cancelled."""
	if order.is_multishoporder:
		print "cancelling order %s"%order


# entry point triggered from satchmo_store.shop.signals.satchmo_cart_changed
def remove_orders_on_cart_change(request=None, cart=None, **kwargs):
	"""Satchmo already listens for this event and deletes any orders."""
	pass


# entry point triggered from satchmo_store.shop.signals.satchmo_order_status_changed
def status_changed_order(sender, oldstatus="", newstatus="", order=None, **kwargs):
	"""
	Triggered by signals.satchmo_order_status_changed. If called with a
	multishop Order, updates all it's child Order's statuses according to the
	new Status.
	"""
	print "changed status of order %s"%order
	if order.is_multishoporder:
		for child_order in order.childorder_set.all():
			child_order.status = newstatus
			child_order.save()



class DummyCart(object):
	"""
	The shipping modules mostly require the instance of a Cart. As we do
	not have this anymore sometimes, we simply 'fake' it, as all that's
	needed by the Shipping modules is access to the CardItem (which they ask
	for it's product to see if that's shippable).
	Here we define the a DummyCart mock as a replacement for the Cart which
	can be filled with the current Order's OrderItem set.
	"""
	def __init__(self, items): self.cartitem_set = items
	def all(): return self.cartitem_set


def update_shipping_cost_for_order(order):
	"""
	Updates the Order's shipping cost (if needed).
	"""
	dummy_cart = DummyCart(order.orderitem_set.all())
	
	# Let Satchmo's default shipping calculation method do the heavy work.
	update_shipping(order, order.shipping_model, order.contact, dummy_cart)


def multiorder_update_shipping(order):
	"""Set the shipping for this order"""
	# raise an exception when called with a non-multishop order
	if not order.is_multishoporder:
		raise Exception("called multiorder_update_shipping with normal order")
	
	# Set a default for when no shipping module is used
	order.shipping_cost = Decimal("0.00")
	shipping = order.shipping_model
	contact = order.contact
	
	# iterate over all child orders
	for child_order in order.childorder_set.all():
		# create a DummyCart
		cart = DummyCart(child_order.orderitem_set.all())
		
		# Save the shipping info
		shipper = shipping_method_by_key(shipping)
		shipper.calculate(cart, contact)
		child_order.shipping_description = shipper.description().encode("utf-8")
		child_order.shipping_method = shipper.method()
		child_order.shipping_cost = shipper.cost()
		child_order.shipping_model = shipping
		child_order.save()
		
		# update the parent's shipping cost
		order.shipping_cost = Decimal(order.shipping_cost + child_order.shipping_cost)
	
	order.shipping_description = shipper.description().encode("utf-8")
	order.shipping_method = shipper.method()
	order.shipping_model = shipping
	order.save()


def copy_orderitem_to_order(order_item, new_order):
	"""
	Expects an OrderItem and an Order. Adds a copy of the given OrderItem to
	the Order if the Order does not already have an OrderItem with the same
	Product attached to it.
	"""
	# First, see if we haven't already added this OrderItem.
	try:
		new_order.orderitem_set.get(product=order_item.product)
		# When #get doesn't raise an Exception, we already have an OrderItem
		# with the same product, so we need to exit this method and not do
		# anything else. Simply return.
		return
	except OrderItem.DoesNotExist:
		pass # If it doesn't exist, proceed without doing anything.
	
	# Quickly get and cache the original OrderItemDetails.
	old_order_item_details = list(order_item.orderitemdetail_set.all())
	
	# Set the OrderItem's PK to None, so it gets copied and then add it
	# to our new Order.
	order_item.pk = None
	new_order.orderitem_set.add(order_item)
	
	# Re-add a copied version of the original (old) OrderItemDetails.
	for new_order_item_detail in old_order_item_details:
		new_order_item_detail.pk = None
		order_item.orderitemdetail_set.add(new_order_item_detail)


def create_copied_order_with_item_group_for_site(order, item_group, site):
	"""
	Expects an original order and a group of OrderItems (of that order).
	A new Order will created, attributes copied from the original order but
	only containing the OrderItems of the group.
	"""
	new_order = copy_order_for_site(order, site)
	new_order.save()
	
	for order_item in item_group:
		copy_orderitem_to_order(order_item, new_order)
	
	# Recalculate the Order's prices and persist the updated values.
	update_shipping_cost_for_order(new_order)
	new_order.recalculate_total()
	new_order.save()
	
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
	"""
	Copies an order and returns the (unsaved) Order copy.
	The copied order does not include any OrderItem relations.
	"""
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
		sub_total = Decimal('0.00'),
		total = Decimal('0.00'),
		discount_code = order.discount_code,
		# TODO: update
		discount = order.discount,
		method = order.method,
		shipping_description = order.shipping_description,
		shipping_method = order.shipping_method,
		shipping_model = order.shipping_model,
		shipping_cost = Decimal('0.00'),
		# TODO: update
		shipping_discount = Decimal('0.00'),
		tax = order.tax,
		time_stamp = order.time_stamp,
		status = order.status,
		multishop_order = order)
	return copied_order
