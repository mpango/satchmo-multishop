# encoding: utf-8
# from django.contrib.auth.backends import ModelBackend

class MultishopAuthBackend(object):
	"""
	Extends default django.contrib.auth.backends.ModelBackend.
	"""
	supports_object_permissions = True
	
	
	def has_perm(self, user_obj, perm, obj=None):
		print "checking object %s for user %s with perms: %s"%(obj, user_obj, perm)
		return False
	
	
	def get_user(self, user_id):
		print "getting user %d", user_id
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
