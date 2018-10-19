from django.conf.urls import url

from accounts import views
from views import signup
from views import PostCreate, PostDetails, PostLikeToggle
from django.contrib.auth import views as auth_views


app_name = 'accounts'

urlpatterns = [
    url(r'^signup/$', signup, name='signup'),
    url(r'^login/$', auth_views.login,
        {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'}, name='logout'),
    url(r'^make_post/$', PostCreate.as_view(), name='create_post'),
    url(r'^posts/(?P<pk>[0-9]+)/$', PostDetails.as_view(), name='post-details'),
    url(r'^posts/(?P<pk>[0-9]+)/like', PostLikeToggle.as_view(), name='post-like-toggle'),
]
