Django Development Server Integration &mdash; Transmogrify v0.1beta2 documentation

# Django Development Server Integration #
transmogrify.views.transmogrify_serve

	from django.conf import settings

	if settings.DEBUG:
	    urlpatterns += patterns ('',
	        (r'^static/(?P<path>.*)$', 'transmogrify.views.transmogrify_serve',
	             {'document_root': settings.MEDIA_ROOT}),
	    )
