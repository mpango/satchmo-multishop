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
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
from multishop.listeners import postprocess_order
from rulez import registry
import datetime


SATCHMO_PRODUCT = True

def get_product_types():
	"""
	Returns a tuple of all product subtypes this app adds
	"""
	return ('MultishopProduct', )


class MultishopProduct(models.Model):
	product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
	virtual_sites = models.ManyToManyField(Site, blank=True, verbose_name=_("Virtual Sites"))
	# site = models.ForeignKey(Site, verbose_name=_('Site'))
	# category = models.ManyToManyField(Category, blank=True, verbose_name=_("Category"))
	# name = models.CharField(_("Full Name"), max_length=255, blank=False, help_text=_("This is what the product will be called in the default site language.  To add non-default translations, use the Product Translation section below."))
	# slug = models.SlugField(_("Slug Name"), blank=True, help_text=_("Used for URLs, auto-generated from name if blank"), max_length=255)
	# sku = models.CharField(_("SKU"), max_length=255, blank=True, null=True, help_text=_("Defaults to slug if left blank"))
	
	def __init__(self, *args, **kwargs):
		super(MultishopProduct, self).__init__(*args, **kwargs)

	def _get_subtype(self):
		"""
		Has to return the name of the product subtype
		"""
		return 'MultishopProduct'
	
	def __unicode__(self):
		return u"MultishopProduct: %s" % self.product.name
	
	# def save(self, force_insert=False, force_update=False):
	# 	self.name = self.product.name
	# 	self.slug = self.product.slug
	# 	self.sku  = self.product.sku
	# 	super(MultishopProduct, self).save(force_insert=force_insert, force_update=force_update)
	
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


def belongs_to_multishop(self):
	"""Returns True when the order belongs to a multishop."""
	return self.site.is_multishop
Order.add_to_class('belongs_to_multishop', belongs_to_multishop)


"""Perform custom actions when an Order has been created successfully."""
signals.order_success.connect(postprocess_order, sender=None)



"""
Add a relationship with 'site' to existing (satchmo) models where required.
This allows us to use site / shop specific behaviour for all aspects needed.
"""
#
# product
#
TaxClass.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

AttributeOption.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

#
#
#
TaxRate.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

#
# satchmo_store.contact
#
ContactInteractionType.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

ContactOrganizationRole.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

ContactRole.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

Interaction.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

Contact.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

Organization.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))

ContactOrganization.add_to_class('site', models.ForeignKey(Site, blank=True, null=True))