from rest_framework import serializers

from accounts.models import Post, MyUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('message', 'likes')
