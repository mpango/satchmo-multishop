"""
DEPRECATED
simply using django's request.user should be fine

This context processors needs to be added to the CONTEXT_PROCESSORS setting
in settings.py. It will then create a `current_user` attribute that's going
to be available throughout the templates. It will always hold the currently
logged in django.contrib.auth.user.
"""

def current_user(request):
	if hasattr(request, 'user'):
		return {'current_user': request.user}
	return {}
