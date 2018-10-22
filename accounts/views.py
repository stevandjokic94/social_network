# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import login, authenticate, user_logged_in
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from forms import SignUpForm
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, RedirectView
from models import Post, MyUser
from django.contrib.auth.mixins import LoginRequiredMixin
#from email_hunter import EmailHunterClient
import jwt, json
from rest_framework.response import Response
from rest_framework import viewsets, views, settings, status
from serializers import UserSerializer, PostSerializer

import clearbit


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        # Does not work on my computer for some reason, not sure why
        # client = EmailHunterClient('24f4629448d166981339d832608fe358124519ce')
        # if not client.exist('form.cleaned_data.get('email')'):
        #       form = SignUpForm()
        #       return render(request, 'accounts/signup.html', {'form': form})

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


class Login(views.APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({'Error': "Please provide username/password"}, status="400")

        username = request.data['username']
        password = request.data['password']
        try:
            user = MyUser.objects.get(username=username, password=password)
        except MyUser.DoesNotExist:
            return Response({'Error': "Invalid username/password"}, status="400")
        if user:
            payload = {
                'id': user.id,
                'email': user.email,
            }
            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}

            return HttpResponse(
                json.dumps(jwt_token),
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


@api_view(['POST'])
@permission_classes([AllowAny, ])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        user = MyUser.objects.get(email=email, password=password)
        if user:
            try:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {}
                user_details['name'] = "%s %s" % (
                    user.first_name, user.last_name)
                user_details['token'] = token
                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                return Response(user_details, status=status.HTTP_200_OK)

            except Exception as e:
                raise e
        else:
            res = {
                'error': 'can not authenticate with the given credentials or the account has been deactivated'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'please provide a email and a password'}
        return Response(res)