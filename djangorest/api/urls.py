from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = {
    url(r'^all/$', views.listAll, name="listAll"),
    url(r'^connect/$', views.connect, name="connect"),
    url(r'^retrieve/$',views.retrieve,name='retrieve'),
    url(r'^common/$',views.common,name='common'),
    url(r'^follow/$',views.follow,name='follow'),
    url(r'^block/$',views.block,name='block'),
    url(r'^message/$',views.message,name='message'),
    url(r'^index/$',views.index,name='index')
}

urlpatterns = format_suffix_patterns(urlpatterns)