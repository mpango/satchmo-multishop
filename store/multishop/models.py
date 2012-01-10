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