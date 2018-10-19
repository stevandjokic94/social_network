from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractUser
from django.db import models

from social_network import settings


class MyUser(AbstractUser, models.Model):
    bio = models.TextField(max_length=400)


class Post(models.Model):
    message = models.TextField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   blank=True, related_name='post_likes')

    def get_absolute_url(self):
        return reverse('posts:details', kwargs={'pk': self.pk})
