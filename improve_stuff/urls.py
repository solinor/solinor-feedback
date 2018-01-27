from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView

import feedback.views

admin.autodiscover()

urlpatterns = [
    path('', feedback.views.frontpage, name="frontpage"),
    path('ask_for_feedback', feedback.views.ask_for_feedback, name="ask_for_feedback"),
    path('submit_response', feedback.views.record_response),
    path('get_missing_forms', feedback.views.get_missing_forms),
    path('store_forms', feedback.views.store_forms),
    path('admin/', admin.site.urls),
    path('get_script_triggers', feedback.views.get_forms_for_script),
    path('admin_book_feedback', feedback.views.admin_book_feedback, name="admin_book_feedback"),
    path('admin_view_feedback/<user_email>', feedback.views.admin_view_feedback, name="admin_view_feedback"),
    path('user_view_feedback', feedback.views.user_view_feedback, name="user_view_feedback"),
    url(r'^accounts/', include('googleauth.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(pattern_name='frontpage', permanent=False)),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
