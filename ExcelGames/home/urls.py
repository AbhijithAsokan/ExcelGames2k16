from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tokensignin$', views.token_signin, name='tokensignin'),
    url(r'^signout$', views.signout, name='signout'),
]