from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('items.urls')),
    path('success.html', TemplateView.as_view(template_name='success.html'), name='success'),
    path('cancel.html', TemplateView.as_view(template_name='cancel.html'), name='cancel'),
]
