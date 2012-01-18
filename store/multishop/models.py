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


SATCHMO_PRODUCT=True

def get_product_types():
	"""
	Returns a tuple of all product subtypes this app adds
	"""
	return ('MultishopProduct', )

class MultishopProduct(Product):
	parent_product = models.ForeignKey(Product, related_name='child_product')
	
	def save(self, force_insert=False, force_update=False):
		self.name = self.parent_product.name
		self.slug = self.parent_product.slug
		self.sku = self.parent_product.sku
		self.short_description = self.parent_product.short_description
		self.description = self.parent_product.description
		self.active = self.parent_product.active
		self.featured = self.parent_product.featured
		self.ordering = self.parent_product.ordering
		self.weight = self.parent_product.weight
		self.weight_units = self.parent_product.weight_units
		self.length = self.parent_product.length
		self.length_units = self.parent_product.length_units
		self.width = self.parent_product.width
		self.width_units = self.parent_product.width_units 
		self.height = self.parent_product.height
		self.height_units = self.parent_product.height_units
		self.total_sold = self.parent_product.total_sold
		self.taxable = self.parent_product.taxable
		self.taxClass = self.parent_product.taxClass
		self.date_added = datetime.date.today()
		super(MultishopProduct, self).save(force_insert=force_insert, force_update=force_update)
	
	
	def _get_subtype(self):
		"""
		Has to return the name of the product subtype
		"""
		return 'MultishopProduct'
	
	def __unicode__(self):
		return u"MultishopProduct: %s" % self.parent_product.name
	
	class Meta:
		verbose_name = _('Multishop Product')
		verbose_name_plural = _('Multishop Products')
	


class MultishopCategory(Category):
	parent_category = models.ForeignKey(Category, related_name='child_category')
	
	def save(self, force_insert=False, force_update=False):
		self.name = self.parent_category.name
		self.slug = self.parent_category.slug
		self.meta = self.parent_category.meta
		self.description = self.parent_category.description
		self.ordering = self.parent_category.ordering
		self.is_active = self.parent_category.is_active
		self.date_added = datetime.date.today()
		super(MultishopCategory, self).save(force_insert=force_insert, force_update=force_update)
	
	def _get_subtype(self):
		return 'Multishop'
	
	def __unicode__(self):
		return u"Multishop Category: %s" % self.name
	
	class Meta:
		verbose_name = _('Multishop Category')
		verbose_name_plural = _('Multishop Categories')
	


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