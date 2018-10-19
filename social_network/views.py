# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView
from accounts.models import Post


class HomePage(ListView):
    template_name = 'index.html'
    model = Post
    context_object_name = 'all_posts'
    ordering = ['-date']
