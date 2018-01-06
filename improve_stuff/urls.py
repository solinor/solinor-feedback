from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView

import feedback.views

urlpatterns = [
    path('', feedback.views.frontpage, name="frontpage"),
    path('ask_for_feedback', feedback.views.ask_for_feedback, name="ask_for_feedback"),
    path('submit_response', feedback.views.record_response),
    path('store_forms', feedback.views.store_forms),
    path('admin/', admin.site.urls),
    url(r'^accounts/', include('googleauth.urls')),
    url(r'^accounts/profile/$', RedirectView.as_view(pattern_name='frontpage', permanent=False)),
]
