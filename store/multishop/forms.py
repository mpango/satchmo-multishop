# encoding: utf-8
from django import forms
# from django.db.models import ManyToManyRel
# from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext_lazy as _
from product.models import Product, Category
from multishop.models import MultishopProduct


class MultishopProductAdminForm(forms.ModelForm):
	categories = forms.ModelMultipleChoiceField(label=_("Categories"), queryset=Category.objects, required=False)
	
	class Meta:
		model = MultishopProduct
	
	
	def clean(self):
		cleaned_data = self.cleaned_data
		if cleaned_data.get('product').site in cleaned_data.get('virtual_sites', []):
			raise forms.ValidationError(_("Virtual Site '%s' may not be set,"
				" as the selected product already belongs to that site."
				%cleaned_data.get('product').site))
		return cleaned_data
	#
	# Wrap the categories field in a RelatedFieldWidgetWrapper so we can make
	# use of the green plus sign added next to it by django. This allows us
	# to add new categories right from this form, too.
	#
	# def __init__(self, *args, **kwargs):
	# 	super(MultishopProductAdminForm, self).__init__(*args, **kwargs)
	# 	rel = ManyToManyRel(self.instance.product.category.model, 'id')
	# 	self.fields['categories'].widget = RelatedFieldWidgetWrapper(self.fields['categories'].widget, rel, self.admin_site)
	# 
	# def save(self, commit=True):
	# 	# super(MultishopProductAdminForm, self).save(commit)
	# 	print "saved: "%self.instance
	# 	return self.instance
