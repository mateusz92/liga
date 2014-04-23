from django.conf.urls import patterns, include, url
from liga import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', include('liga.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', views.home, name='home'),
)