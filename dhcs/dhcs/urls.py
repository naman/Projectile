# //=======================================================================
# // Copyright Projectile, IIIT Delhi 2017.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

handler500 = "projectile.views.server_error"
handler404 = "projectile.views.not_found"

urlpatterns = patterns('',
                       url('', include('projectile.urls')),
                       url('', include(
                           'social.apps.django_app.urls', namespace='social')),
                       url(r'^search/', include('haystack.urls')),
                       url(r'^batcave/', include(admin.site.urls)),
                       ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
