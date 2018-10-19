# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from forms import SignUpForm
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, RedirectView
from models import Post, MyUser
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.models import User
from rest_framework import viewsets
from serializers import UserSerializer, PostSerializer

import clearbit


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            clearbit.key = 'sk_48d5da34d0bf087c83400aa13c0f317a'
            response = clearbit.Enrichment.find(email=form.cleaned_data.get('email'),
                                                stream=True)
            if response['person']['bio'] is not None:
                instance = form.save(commit=False)
                instance.bio = response['person']['bio']
                instance.save()
            else:
                form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['message']
    template_name = 'new-post.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(PostCreate, self).form_valid(form)


class PostDetails(LoginRequiredMixin, DetailView):
    template_name = 'post-details.html'
    model = Post


class PostLikeToggle(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        pk_ = self.kwargs.get('pk')
        obj = get_object_or_404(Post, pk=pk_)
        user = self.request.user
        if user.is_authenticated():
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return "/"


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = MyUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
