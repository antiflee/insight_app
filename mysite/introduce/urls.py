from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^send_uid/$', views.get_user_info, name='get_user_info'),
    url(r'^$', views.index, name='index'),
    url(r'^slides$', views.slides, name='slides'),
]
