from django.conf.urls import patterns, include, url
from liga import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', include('liga.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', views.home, name='home'),
    url(r'^leagues/', views.leagues, name='leagues'),
    url(r'^league/(?P<l_id>\d+)/', views.league, name='league'),
    url(r'^team/(?P<t_id>\d+)/(?P<l_id>\d+)/', views.team, name='team'),
    url(r'^register/', views.register, name='register'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
)