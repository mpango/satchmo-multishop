# encoding: utf-8
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from satchmo_store.shop import signals
from satchmo_store.shop.models import Order
from product.models import Product, Category, TaxClass, AttributeOption, \
                           Option
from tax.modules.area.models import TaxRate
from satchmo_store.contact.models import ContactInteractionType, \
                                         ContactOrganizationRole, \
                                         ContactRole, Interaction, Contact, \
                                         ContactOrganization, Organization
from django.utils.translation import get_language, ugettext, \
                                     ugettext_lazy as _
from multishop.listeners import postprocess_order, cancel_order, \
                                remove_orders_on_cart_change, \
                                status_changed_order, \
                                postprocess_order_item_add
from rulez import registry
import datetime


#
# Tell Satchmo we're configuring a custom Product here (MultishopProduct).
#
SATCHMO_PRODUCT = True

def get_product_types():
	"""
	Returns a tuple of all product subtypes this app adds.
	"""
	return ('MultishopProduct', )


class MultishopProduct(models.Model):
	"""
	A MultishopProduct links the original products to Multishops. A Multishop
	is the new shop class, that does not contain it's own products, but only
	products from other, real shops. One Product can thus belong to multiple
	Multishops. These shops are also referred to as 'virtual shops'.
	"""
	product = models.OneToOneField(Product, verbose_name=_('Product'),
		primary_key=True)
	virtual_sites = models.ManyToManyField(Site, blank=True,
		verbose_name=_("Virtual Sites"))
	
	def __init__(self, *args, **kwargs):
		super(MultishopProduct, self).__init__(*args, **kwargs)

	def _get_subtype(self):
		"""
		Has to return the name of the product subtype
		"""
		return 'MultishopProduct'
	
	def __unicode__(self):
		return u"MultishopProduct: %s" % self.product.name
	
	class Meta:
		verbose_name = _('Multishop Product')
		verbose_name_plural = _('Multishop Products')
	


@receiver(pre_save, sender=Contact)
def add_site(sender, instance, **kwargs):
	"""Adds the current page's site to the contact if it hasn't been set."""
	if not instance.site:
		instance.site = Site.objects.get_current()


def user_can_edit(self, user_obj):
	'''
	This function will be hooked up to the User model as a method.
	The rule says that a user can only be modified by the same user
	'''
	user_site = user_obj.get_profile().site
	if user_site is not None and self.site == user_site:
		return True
	return False
Product.add_to_class('can_edit', user_can_edit)
registry.register('can_edit', Product)


def is_shop_owner(self):
	"""Returns True when the User is in the 'shop_owner' group."""
	return self.groups.filter(name='shop_owner').count() == 1
User.add_to_class('is_shop_owner', is_shop_owner)


def is_multishop_owner(self):
	"""Returns True when the User is in the 'virtual_shop_owner' group."""
	# TODO: Maybe asking the user's site is a better approach to determine if
	#       the user is running a multishop or a normal shop. This would at
	#       least eliminate the need for the group 'multishop_owner' to have
	#       a hardcoded name.
	#       ATTENTION: Following line would need to get a try-catch for
	#       superusers, which may not have a site set.
	# return self.get_profile().site.is_multishop
	return self.groups.filter(name='multishop_owner').count() == 1
User.add_to_class('is_multishop_owner', is_multishop_owner)


class UserProfile(models.Model):
	# The required link to the django.contrib.auth.User model.
	user = models.OneToOneField(User)
	
	# The site_id the user belongs to (becomes relevant for staff-users).
	site = models.ForeignKey(Site, blank=True, null=True)
	
	def __unicode__(self):
		return "%s - %s"%(self.user, self.site)
	
	class Meta:
		app_label = 'auth'
		verbose_name = _('Benutzer Profil')
		verbose_name_plural = _('Benutzer Profile')


def create_user_profile(sender, instance, created, **kwargs):
	"""
	Automatically creates a default user profile for newly created users.
	We don't set the site here, as we cannot know which would be appropriate.
	"""
	if created:
		UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)



"""
Add a new field to the django.contrib.sites.Site which indicates whether the
respective site represents a normal shop (is_multishop = False) or a new
'multishop' (is_multishop = True). Default is False.
"""
Site.add_to_class('is_multishop', models.BooleanField(default=False))


#
# Order changes and additions.
#


def belongs_to_multishop(self):
	"""Returns True when the order belongs to a multishop."""
	return self.site.is_multishop
Order.add_to_class('belongs_to_multishop', belongs_to_multishop)

@property
def is_multishoporder(self):
	"""Property alias for belongs_to_multishop"""
	return self.belongs_to_multishop()
Order.add_to_class('is_multishoporder', is_multishoporder)

"""
Add a reference from normal orders to their parent multishoporder (if
present).
"""
Order.add_to_class('multishop_order', models.ForeignKey("self",
	verbose_name=_('Multishop Order'), blank=True, null=True,
	related_name='childorder_set'))


"""Perform custom actions when an Order has been created successfully."""
# signals.order_success.connect(postprocess_order, sender=None)

"""Perform custom actions when an Item has been copied over to an Order."""
signals.satchmo_post_copy_item_to_order.connect(postprocess_order_item_add,
	sender=None)

"""Perform custom actions when an Order has been cancelled."""
signals.order_cancelled.connect(cancel_order, sender=None)

"""Perform custom actions when a Cart has been changed."""
signals.satchmo_cart_changed.connect(remove_orders_on_cart_change, sender=None)

"""Perform custom actions when a Order's status has been changed."""
signals.satchmo_order_status_changed.connect(status_changed_order, sender=None)



"""
Add a relationship with 'site' to existing (satchmo) models where required.
This allows us to use site / shop specific behaviour for all aspects needed.
"""
#
# product
#
TaxClass.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

AttributeOption.add_to_class('site', models.ForeignKey(Site, blank=True,
	null=True))

#
#
#
TaxRate.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

#
# satchmo_store.contact
#
ContactInteractionType.add_to_class('site', models.ForeignKey(Site,
	blank=True, null=True))

ContactOrganizationRole.add_to_class('site', models.ForeignKey(Site,
	blank=True, null=True))

ContactRole.add_to_class('site', models.ForeignKey(Site, blank=True,
	null=True))

Interaction.add_to_class('site', models.ForeignKey(Site, blank=True,
	null=True))

Contact.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

Organization.add_to_class('site', models.ForeignKey(Site, blank=True,
	null=True))

ContactOrganization.add_to_class('site', models.ForeignKey(Site, blank=True,
	null=True))

