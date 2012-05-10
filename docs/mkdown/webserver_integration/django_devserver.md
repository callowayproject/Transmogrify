Django Development Server Integration &mdash; Transmogrify v0.1beta2 documentation

# Django Development Server Integration #
transmogrify.views.transmogrify_serve

	from django.conf import settings

	if settings.DEBUG:
	    urlpatterns += patterns (&#39;&#39;,
	        (r&#39;^static/(?P&lt;path&gt;.*)$&#39;, &#39;transmogrify.views.transmogrify_serve&#39;,
	             {&#39;document_root&#39;: settings.MEDIA_ROOT}),
	    )
