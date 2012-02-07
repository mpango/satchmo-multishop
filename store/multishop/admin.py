# encoding: utf-8
from django.forms import ValidationError
from django import forms
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin
from django.core.urlresolvers import reverse
from django.contrib.comments       import Comment
from django.contrib.comments.admin import CommentsAdmin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from skins.models import Skin
from multishop.models import UserProfile, MultishopProduct
from multishop.forms import MultishopProductAdminForm
from product.models import Product, Category, AttributeOption, OptionGroup, \
                           Option, Discount, TaxClass
from product.admin  import ProductOptions, CategoryOptions, \
                           AttributeOptionAdmin, OptionGroupOptions, \
                           CategoryAttributeInline, CategoryImage_Inline, \
                           ProductAttribute_Inline, Price_Inline, \
                           ProductImage_Inline, OptionOptions, \
                           DiscountOptions
from product.modules.configurable.models import ConfigurableProduct, \
                                                ProductVariation
from product.modules.configurable.admin  import ConfigurableProductAdmin, \
                                                ProductVariationOptions
from registration.models import RegistrationProfile
from tax.modules.area.models import TaxRate
from tax.modules.area.admin  import TaxRateOptions
from satchmo_store.contact.models import ContactInteractionType, \
                                         ContactOrganizationRole, \
                                         ContactRole, Interaction, Contact, \
                                         Organization, ContactOrganization
from satchmo_store.contact.admin  import ContactInteractionTypeOptions, \
                                         ContactOrganizationRoleOptions, \
                                         ContactRoleOptions, \
                                         InteractionOptions, \
                                         ContactOptions, \
                                         OrganizationOptions, \
                                         ContactOrganizationOptions
from satchmo_store.shop.models import Order, OrderItem, Cart, Config, \
                                      OrderPayment, CartItem, \
                                      OrderAuthorization
from satchmo_store.shop.admin  import OrderOptions, OrderItemOptions, \
                                      CartOptions, ConfigOptions, \
                                      OrderPaymentOptions, CartItemOptions, \
                                      OrderAuthorizationOptions, \
                                      OrderItem_Inline, OrderStatus_Inline, \
                                      OrderVariable_Inline, CartItem_Inline,\
                                      OrderTaxDetail_Inline, \
                                      OrderAuthorizationDetail_Inline, \
                                      OrderPaymentDetail_Inline, \
                                      OrderPaymentFailureDetail_Inline


class MultishopLimitedFieldMixin(object):
	"""
	In many admin change pages there are foreign key relationships to other
	models. Many of these also need to be restricted to the current user's
	site. By default they simply show all available instances there. This
	mixin allows one to specify a tuple of field names which shall be
	restricted to the same site as their parent model.
	See method docs for more detailed instructions.
	"""
	
	def _filter_field(self, field, db_field, request):
		"""
		Helper method for performing the actual filtering of the given
		field's queryset. Used by #formfield_for_foreignkey and
		#formfield_for_manytomany.
		"""
		user_site = request.user.get_profile().site
		if db_field.name in self.site_limited_fields:
			field.queryset = field.queryset.filter(site__exact=user_site)
		return field
	
	
	def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
		"""
		Returns the formfield (and most importantly it's displayed choices)
		for ForeignKey fields. In many cases these need to be limited to the
		current user's site as well. Define these fields that need to be
		limited by defining a `site_limited_fields` property tuple like
		so::
			
			site_limited_fields = ('limited_field_a', 'limited_field_b', )
		"""
		field = super(MultishopLimitedFieldMixin, self).formfield_for_foreignkey(db_field, request, **kwargs)
		if not request.user.is_superuser:
			field = self._filter_field(field, db_field, request)
		return field
	
	
	def formfield_for_manytomany(self, db_field, request=None, **kwargs):
		"""
		See explanation for #formfield_for_manytomany.
		"""
		field = super(MultishopLimitedFieldMixin, self).formfield_for_manytomany(db_field, request, **kwargs)
		if not request.user.is_superuser:
			field = self._filter_field(field, db_field, request)
		return field


class MultishopMixinAdmin(MultishopLimitedFieldMixin, admin.ModelAdmin):
	"""
	Customized satchmo.ProductOptions admin class, responsible for handling
	the more fine-grained permission system.
	"""
	site_limited_fields = ()
	#
	# Because of this class being used as a mixin, 'fields' isn't necessarily
	# declared already, hence we cannot manipulate it as needed. Find another
	# solution to hide the 'site' field from the admin list. (Adding it to
	# the list of 'exclude' fields doesn't work either.)
	#
	# def __init__(self, *args, **kwargs):
	# 	"""
	# 	Overwrite to remove the 'site' field from the admin and make it use a
	# 	default value instead. That default value is the current user's own
	# 	site_id.
	# 	"""
	# 	super(MultishopMixinAdmin, self).__init__(*args, **kwargs)
	# 	self.fieldsets = super(MultishopMixinAdmin, self).fieldsets
	# 	
	# 	# Remove the 'site' entry from tuple, which is the first one in the
	# 	# 'fields' tuple.
	# 	# TODO: Verify by testing that this hardcoded structure remains
	# 	#       untouched (satchmo changing the order shall break that test).
	# 	fields = self.fieldsets[0][1]['fields']
	# 	self.fieldsets[0][1]['fields'] = fields[1:]
	
	
	def _obj_site(self, obj):
		"""
		Returns the site associated with the given obj, assuming there either
		is a property or a callable method with the name `site` for it.
		"""
		if(callable(obj.site)):
			return obj.site()
		else:
			return obj.site
	
	
	def get_readonly_fields(self, request, obj=None):
		"""
		Adds the site attribute to the readonly fields for all non-superusers
		so they don't get confused about that one so much (as it's
		automatically set to the user's site anyway).
		"""
		readonly_fields = super(MultishopMixinAdmin, self).get_readonly_fields(request, obj)
		if not request.user.is_superuser:
			readonly_fields += ('site', )
		return readonly_fields
	
	
	def save_model(self, request, obj, form, change):
		"""
		We need to set the object's site to the current user's site unless
		the request is made by a superuser, who may set the site setting to
		any arbitrary site.
		"""
		if not request.user.is_superuser:
			# TODO: references #2: currently this method may be called from a
			#       user who doesn't have a site yet, which would lead to an
			#       IntegrityError being thrown that isn't handled nicely.
			#       Instead, it would simply result in a 500 response. FIX IT
			obj.site = request.user.get_profile().site
		obj.save()
	
	
	def has_change_permission(self, request, obj=None):
		if not obj:
			# So they can see the change list page
			return True
		if request.user.is_superuser or self._obj_site(obj) == request.user.get_profile().site:
			# Superusers may see all objects. Normal users may only see their
			# own objects, i.e. objects belonging to the user's site setting.
			return True
		else:
			# In all other cases don't grant permission.
			return False
	# Treat delete and change permissions identical.
	has_delete_permission = has_change_permission
	
	
	def _filter(self, user_site, queryset):
		"""
		By default the filtering assumes that the object passed to #queryset
		does have it's own site field and uses this for filtering. In some
		cases however, this may not be the case. E.g. when a model is always
		linked to a parent model and that parent already has a site field. We
		can then overwrite / implement this method to take that into account
		and change the default filtering.
		"""
		raise NotImplementedError
	
	
	def queryset(self, request):
		"""
		Overwrite to filter out objects the current user of that request does
		not have any kind of access to. That is all products that are not
		linked to the same site. Superusers have access to all objects.
		"""
		queryset = super(MultishopMixinAdmin, self).queryset(request)
		user_site = request.user.get_profile().site
		
		# Limit the query by adding a filter for the site when the request is
		# not originating from a superuser.
		# If the user does not yet have a site set, he won't see anything!
		if not request.user.is_superuser:
			try:
				queryset = self._filter(user_site, queryset)
			except NotImplementedError:
				queryset = queryset.filter(site=user_site)
		
		return queryset



"""
Extend the default (or rather already extended by django-site-skins) Sites
Admin class. Add a field for our custom 'is_multishop' flag.
"""
new_list_display = list(SiteAdmin.list_display)
new_list_display.extend(['is_multishop',])
SiteAdmin.list_display = tuple(new_list_display)
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)



"""
Our own completely custom multishop admin classes.
"""
#
# Register the UserProfile so we can manage it in the admin panel as well.
# 
admin.site.register(UserProfile)

#
# Register our custom MultishopProduct
#
class MultishopProductAdmin(admin.ModelAdmin):
	list_display = ('product', 'slug', )
	# list_filter = ['product__site', ]
	search_fields = ['product__slug', 'product__sku', 'product__name', ]
	form = MultishopProductAdminForm
	actions = ['remove_selected', ]
	change_form_template = 'admin/multishop/multishopproduct_change_form.html'
	add_form_template = 'admin/multishop/multishopproduct_add_form.html'
	
	def __init__(self, model, admin_site):
		self.form.admin_site = admin_site 
		super(MultishopProductAdmin, self).__init__(model, admin_site)
	
	
	def slug(self, obj):
		return obj.product.slug
	
	
	def add_view(self, request, form_url='', extra_context=None):
		user_site = request.user.get_profile().site
		
		if request.method == 'POST':
			customform = MultishopProductAdminForm(request.POST)
		else:
			customform = MultishopProductAdminForm()
		
		if not request.user.is_superuser:
			customform.fields.get('virtual_sites').widget = forms.HiddenInput()
			customform.fields.get('categories').queryset = Category.objects.filter(site__id=user_site.id)
		
		my_context = {
			'customform': customform,
		}
		return super(MultishopProductAdmin, self).add_view(request,
			form_url, extra_context=my_context)
	
	
	def change_view(self, request, object_id, extra_context=None):
		instance = None
		user_site = request.user.get_profile().site
		
		if request.method == 'POST':
			customform = MultishopProductAdminForm(request.POST)
		else:
			instance = get_object_or_404(MultishopProduct, product__id=object_id)
			customform = MultishopProductAdminForm(instance=instance)
			customform.fields.get('categories').initial = instance.product.category.all()
		
		if not request.user.is_superuser:
			customform.fields.get('virtual_sites').widget = forms.HiddenInput()
			customform.fields.get('categories').queryset = Category.objects.filter(site__id=user_site.id)
		
		my_context = {
			'adminform': None,
			'customform': customform,
		}
		return super(MultishopProductAdmin, self).change_view(request,
			object_id, extra_context=my_context)
	
	
	def get_readonly_fields(self, request, obj=None):
		"""
		Adds the virtual_sites attribute to the readonly fields for all
		non-superusers so they don't get confused about that one so much (as
		it's automatically set to the user's site anyway).
		However, in this case we may completely remove it from the field?
		"""
		readonly_fields = super(MultishopProductAdmin, self).get_readonly_fields(request, obj)
		if not request.user.is_superuser:
			readonly_fields += ('virtual_sites', )
		return readonly_fields
	
	
	# def get_form(self, request, obj=None, **kwargs):
	# 	"""
	# 	TODO: setting the queryset and the initial value here doesn't work as
	# 	it should because it caches the result. We'd need to move all that
	# 	stuff into a different method. See #15.
	# 	"""
	# 	form = super(MultishopProductAdmin, self).get_form(request, obj, **kwargs)
	# 	if obj is not None:
	# 		form.declared_fields['categories'].initial = obj.product.category.all()
	# 	if not request.user.is_superuser:
	# 		user_site = request.user.get_profile().site
	# 		form.declared_fields['categories'].queryset = Category.objects.filter(site__id=user_site.id)
	# 		if obj is not None:
	# 			form.declared_fields['categories'].initial = obj.product.category.filter(site__id=user_site.id)
	# 	return form
	
	
	def save_model(self, request, obj, form, change):
		"""
		Purpose of overwriting this method here is to handle the categories
		of the original product. When a non-superuser submits the form, only
		categories from his own site can be selected and hence stored. But we
		do have to keep all other categories, belonging to different sites as
		well here. Assuring this relationship doesn't break is done here.
		"""
		new_cats = set(form.cleaned_data['categories'])
		if not request.user.is_superuser:
			user_site = request.user.get_profile().site
			# current categories of the linked product
			old_cats = obj.product.category.all()
			# the ones we definitely keep (all but from this site)
			keep_cats = set(old_cats.exclude(site=user_site))
			# the (new) ones to add; same site
			new_cats = keep_cats.union(new_cats)
			# store the site (first saving the object for the m2m stuff)
			obj.save()
			obj.virtual_sites.add(request.user.get_profile().site)
			form.cleaned_data['categories'] = list(new_cats)
		obj.product.category = new_cats
		obj.save()
		obj.product.save()
	
	
	def queryset(self, request):
		"""
		Overwrite to filter out objects the current user of that request does
		not have any kind of access to. That is all products that are not
		linked to the same site. Superusers have access to all objects.
		"""
		queryset = super(MultishopProductAdmin, self).queryset(request)
		user_site = request.user.get_profile().site
		
		# Limit the query by adding a filter for the site when the request is
		# not originating from a superuser.
		# If the user does not yet have a site set, he won't see anything!
		if not request.user.is_superuser:
			queryset = queryset.filter(virtual_sites__in=[user_site])
		
		return queryset
	
	
	def get_actions(self, request):
		"""
		Disable the delete action for non-superuser and disable the remove
		action for superusers. So each group does only have one of these two
		options available. (Removing doesn't really make sense for
		superusers, as they can manipulate the MultishopProduct's
		virtual_sites attribute directly anyway).
		"""
		actions = super(MultishopProductAdmin, self).get_actions(request)
		if not request.user.is_superuser and 'delete_selected' in actions:
			del actions['delete_selected']
		if request.user.is_superuser and 'remove_selected' in actions:
			del actions['remove_selected']
		return actions
	
	
	def remove_selected(self, request, queryset):
		"""
		Loop through all objects the user has selected and call our custom
		remove function. This is basically a delete but with the difference
		that only the site references get removed from the model. The actual
		model's #delete method only gets called when no other sites are left
		after the site has been removed. Thsi prevents accidental removal of
		a product from other shops. Superuser may still call delete directly
		causing the product to be removed from all virtual shops.
		"""
		user_site = request.user.get_profile().site
		for obj in queryset:
			# remove the current user's site
			obj.virtual_sites.remove(user_site)
			# remove all the object's categories for that site
			for cat_to_remove in Category.objects.by_site(user_site).all():
				obj.product.category.remove(cat_to_remove)
			if obj.virtual_sites.count() == 0:
				# delete when there are no sites left now
				obj.delete()
		self.message_user(request, "%s Multishop Products were successfully removed" % len(queryset))
	
	remove_selected.short_description = _('Remove Selected Multishop Products')

admin.site.register(MultishopProduct, MultishopProductAdmin)



"""
Unregister the original satchmo admin classes, create new admin classes,
derived from these originals but mixed in with our MultishopMixinAdmin and
register these new admin classes for the satchmo classes again.
"""
#
# product
#
admin.site.unregister(AttributeOption)
class MultishopAttributeOptionAdmin(AttributeOptionAdmin, MultishopMixinAdmin): pass
admin.site.register(AttributeOption, MultishopAttributeOptionAdmin)

admin.site.unregister(OptionGroup)
class MultishopOptionGroupOptions(OptionGroupOptions, MultishopMixinAdmin): pass
admin.site.register(OptionGroup, MultishopOptionGroupOptions)

admin.site.unregister(Product)
class MultishopProductAttribute_Inline(MultishopLimitedFieldMixin, ProductAttribute_Inline):
	site_limited_fields = ('option', )
class MultishopProductOptions(ProductOptions, MultishopMixinAdmin):
	site_limited_fields = ('category', 'related_items', 'also_purchased', \
                           'taxClass')
	inlines = [MultishopProductAttribute_Inline, Price_Inline, ProductImage_Inline]
	
	def changelist_view(self, request, extra_context=None):
		"""
		When calling this view from a virtual shop, we actually want to show
		virtual products (MultishopProducts) instead of the actual product as
		virtual shops should not have their own products anyway.
		So we check if the request is coming from a virtual shop owner and
		in that case redirect to the MultishopProduct admin.
		"""
		if request.GET.get("pop") is not None and request.user.is_multishop_owner():
			base_url = reverse('admin:multishop_multishopproduct_changelist')
			redirect_url = "%s?t=product&pop=1"%base_url
			return HttpResponseRedirect(redirect_url)
		else:
			return super(MultishopProductOptions, self).changelist_view(request, extra_context)
	
	def save_model(self, request, obj, form, change):
		"""
		Purpose of overwriting this method here is to handle the categories
		of the original product. When a non-superuser submits the form, only
		categories from his own site can be selected and hence stored. But we
		do have to keep all other categories, belonging to different sites as
		well here. Assuring this relationship doesn't break is done here.
		"""
		new_cats = set(form.cleaned_data['category'])
		# import pdb; pdb.set_trace()
		if not request.user.is_superuser:
			user_site = request.user.get_profile().site
			# current categories of the linked product
			old_cats, keep_cats = [], set([])
			if obj.pk is not None:
				old_cats = obj.category.all()
				# the ones we definitely keep (all but from this site)
				keep_cats = set(old_cats.exclude(site=user_site))
			# the (new) ones to add; same site
			new_cats = keep_cats.union(new_cats)
			form.cleaned_data = list(new_cats)
		# store the site (first saving the object for the m2m stuff)
		super(MultishopProductOptions, self).save_model(request, obj, form, change)
		for cat in new_cats:
			obj.category.add(cat)
		obj.save()
admin.site.register(Product, MultishopProductOptions)

admin.site.unregister(Category)
class MultishopCategoryAttributeInline(MultishopLimitedFieldMixin, CategoryAttributeInline):
	site_limited_fields = ('option', )
class MultishopCategoryOptions(CategoryOptions, MultishopMixinAdmin):
	site_limited_fields = ('parent', 'related_categories', )
	inlines = [MultishopCategoryAttributeInline, CategoryImage_Inline]
admin.site.register(Category, MultishopCategoryOptions)

admin.site.unregister(Option)
class MultishopOptionOptions(OptionOptions, MultishopMixinAdmin):
	site_limited_fields = ('option_group', )
	def _filter(self, user_site, queryset):
		return queryset.filter(option_group__site=user_site)
	def _obj_site(self, obj):
		return obj.option_group.site
admin.site.register(Option, MultishopOptionOptions)

admin.site.unregister(Discount)
class MultishopDiscountOptions(DiscountOptions, MultishopMixinAdmin):
	site_limited_fields = ('valid_products', 'valid_categories', )
admin.site.register(Discount, MultishopDiscountOptions)

admin.site.unregister(TaxClass)
admin.site.register(TaxClass, MultishopMixinAdmin)

#
# product.modules.configurable
#
admin.site.unregister(ConfigurableProduct)
class MultishopConfigurableProductAdmin(ConfigurableProductAdmin, MultishopMixinAdmin):
	site_limited_fields = ('option_group', 'product', )
	def _filter(self, user_site, queryset):
		return queryset.filter(product__site=user_site)
	def _obj_site(self, obj):
		return obj.product.site
admin.site.register(ConfigurableProduct, MultishopConfigurableProductAdmin)

admin.site.unregister(ProductVariation)
class MultishopProductVariationOptions(ProductVariationOptions, MultishopMixinAdmin):
	site_limited_fields = ('product' )
	def _filter(self, user_site, queryset):
		return queryset.filter(product__site=user_site)
	def _obj_site(self, obj):
		return obj.product.site
	
	def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
		"""
		Overwrite again here, to customize the way we link the parent field.
		Here we essentially allow parents only from the same site, too. By
		default we would look for a site field on the parent, which it
		doesn't have (and doesn't need).
		"""
		field = super(MultishopProductVariationOptions, self).formfield_for_foreignkey(db_field, request, **kwargs)
		if not request.user.is_superuser and db_field.name == 'parent':
			user_site = request.user.get_profile().site
			field.queryset = field.queryset.filter(product__site__exact=user_site)
		return field
	
	def formfield_for_manytomany(self, db_field, request=None, **kwargs):
		"""See explanation for #formfield_for_foreignkey."""
		field = super(MultishopProductVariationOptions, self).formfield_for_manytomany(db_field, request, **kwargs)
		if not request.user.is_superuser and db_field.name == 'options':
			user_site = request.user.get_profile().site
			field.queryset = field.queryset.filter(option_group__site__exact=user_site)
		return field
admin.site.register(ProductVariation, MultishopProductVariationOptions)

#
# registration
#
# def registrationProfileSite(self):
# 	return self.user.get_profile().site
# RegistrationProfile.add_to_class("site", registrationProfileSite)
# 
# admin.site.unregister(RegistrationProfile)
# class RegistrationProfileAdmin(MultishopMixinAdmin):
# 	# site_limited_fields = ('user', )
# 	pass
# admin.site.register(RegistrationProfile, RegistrationProfileAdmin)

#
# tax.modules.area
#
admin.site.unregister(TaxRate)
class MultishopTaxRateOptions(TaxRateOptions, MultishopMixinAdmin): pass
admin.site.register(TaxRate, MultishopTaxRateOptions)

#
# django.contrib
#
admin.site.unregister(Comment)
class MultishopCommentAdmin(CommentsAdmin, MultishopMixinAdmin): pass
admin.site.register(Comment, MultishopCommentAdmin)

#
# satchmo_store.contact
#
admin.site.unregister(ContactInteractionType)
class MultishopContactInteractionTypeAdmin(ContactInteractionTypeOptions, MultishopMixinAdmin): pass
admin.site.register(ContactInteractionType, MultishopContactInteractionTypeAdmin)

admin.site.unregister(ContactOrganizationRole)
class MultishopContactOrganizationRoleAdmin(ContactOrganizationRoleOptions, MultishopMixinAdmin): pass
admin.site.register(ContactOrganizationRole, MultishopContactOrganizationRoleAdmin)

admin.site.unregister(ContactRole)
class MultishopContactRoleAdmin(ContactRoleOptions, MultishopMixinAdmin): pass
admin.site.register(ContactRole, MultishopContactRoleAdmin)

admin.site.unregister(Interaction)
class MultishopInteractionAdmin(InteractionOptions, MultishopMixinAdmin):
	site_limited_fields = ('type', 'contact', )
admin.site.register(Interaction, MultishopInteractionAdmin)

admin.site.unregister(Contact)
class MultishopContactAdmin(ContactOptions, MultishopMixinAdmin):
	site_limited_fields = ('organization', )
admin.site.register(Contact, MultishopContactAdmin)

admin.site.unregister(Organization)
class MultishopOrganizationAdmin(OrganizationOptions, MultishopMixinAdmin):
	site_limited_fields = ('type', 'role', )
admin.site.register(Organization, MultishopOrganizationAdmin)

admin.site.unregister(ContactOrganization)
class MultishopContactOrganizationAdmin(ContactOrganizationOptions, MultishopMixinAdmin):
	site_limited_fields = ('type', 'role', )
admin.site.register(ContactOrganization, MultishopContactOrganizationAdmin)

#
# satchmo_store.shop
#
admin.site.unregister(Order)
class MultishopOrderItem_Inline(MultishopLimitedFieldMixin, OrderItem_Inline):
	site_limited_fields = ('product', )
	
	def _filter_field(self, field, db_field, request):
		"""
		OrderItems actually need to take into account MultishopProducts when
		they are used inline. So we need to change the filter here.
		"""
		user_site = request.user.get_profile().site
		if not request.user.is_superuser and db_field.name in self.site_limited_fields:
			field.queryset = field.queryset.filter(
				Q(multishopproduct__virtual_sites__in=[user_site]) |
				Q(site__exact=user_site)
			)
		return field
	

class MultishopOrderAuthorizationDetail_Inline(MultishopLimitedFieldMixin, OrderAuthorizationDetail_Inline):
	site_limited_fields = ('capture', )
	
	def _filter_field(self, field, db_field, request):
		"""OrderAuthorizations need to be limited according to the order."""
		user_site = request.user.get_profile().site
		if not request.user.is_superuser and db_field.name in self.site_limited_fields:
			field.queryset = field.queryset.filter(order__site__exact=user_site)
		return field

class MultishopOrderAdmin(OrderOptions, MultishopMixinAdmin):
	site_limited_fields = ('contact', )
	inlines = [MultishopOrderItem_Inline, OrderStatus_Inline, OrderVariable_Inline,
		OrderTaxDetail_Inline, MultishopOrderAuthorizationDetail_Inline,
		OrderPaymentDetail_Inline, OrderPaymentFailureDetail_Inline]
admin.site.register(Order, MultishopOrderAdmin)

admin.site.unregister(OrderItem)
class MultishopOrderItemAdmin(OrderItemOptions, MultishopMixinAdmin):
	site_limited_fields = ('product', )
	def _filter(self, user_site, queryset):
		return queryset.filter(order__site=user_site)
	def _obj_site(self, obj):
		return obj.order.site
admin.site.register(OrderItem, MultishopOrderItemAdmin)

admin.site.unregister(OrderPayment)
class MultishopOrderPaymentAdmin(OrderPaymentOptions, MultishopMixinAdmin):
	site_limited_fields = ('order', )
	def _filter(self, user_site, queryset):
		return queryset.filter(order__site=user_site)
	def _obj_site(self, obj):
		return obj.order.site
admin.site.register(OrderPayment, MultishopOrderPaymentAdmin)

admin.site.unregister(CartItem)
class MultishopCartItemAdmin(CartItemOptions, MultishopMixinAdmin):
	site_limited_fields = ('cart', 'product', )
	def _filter(self, user_site, queryset):
		return queryset.filter(cart__site=user_site)
	def _obj_site(self, obj):
		return obj.cart.site
admin.site.register(CartItem, MultishopCartItemAdmin)

admin.site.unregister(OrderAuthorization)
class MultishopOrderAuthorizationAdmin(OrderAuthorizationOptions, MultishopMixinAdmin):
	site_limited_fields = ('order', )
	def _filter(self, user_site, queryset):
		return queryset.filter(order__site=user_site)
	def _obj_site(self, obj):
		return obj.order.site
	
	def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
		"""
		Overwrite again here, to customize the way we link the capture field.
		Here we essentially allow captures only from the same site as the
		order's. By default we would look for a site field on the capture,
		which is doesn't have (and doesn't need).
		"""
		field = super(MultishopOrderAuthorizationAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
		if not request.user.is_superuser and db_field.name == 'capture':
			user_site = request.user.get_profile().site
			field.queryset = field.queryset.filter(order__site__exact=user_site)
		return field
admin.site.register(OrderAuthorization, MultishopOrderAuthorizationAdmin)

admin.site.unregister(Cart)
class MultishopCartItem_Inline(MultishopLimitedFieldMixin, CartItem_Inline):
	site_limited_fields = ('product', )
class MultishopCartAdmin(CartOptions, MultishopMixinAdmin):
	site_limited_fields = ('customer', )
	inlines = [MultishopCartItem_Inline]
admin.site.register(Cart, MultishopCartAdmin)

admin.site.unregister(Config)
class MultishopConfigAdmin(ConfigOptions, MultishopMixinAdmin): pass
admin.site.register(Config, MultishopConfigAdmin)


