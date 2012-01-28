# encoding: utf-8
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from product.models import Product, Category, TaxClass, AttributeOption, \
                           Option
from tax.modules.area.models import TaxRate
from satchmo_store.contact.models import ContactInteractionType, \
                                         ContactOrganizationRole, \
                                         ContactRole, Interaction, Contact, \
                                         ContactOrganization, Organization
from django.utils.translation import get_language, ugettext, ugettext_lazy as _
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


def is_virtual_shop_owner(self):
	"""Returns True when the User is in the 'virtual_shop_owner' group."""
	return self.groups.filter(name='virtual_shop_owner').count() == 1
User.add_to_class('is_virtual_shop_owner', is_virtual_shop_owner)


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