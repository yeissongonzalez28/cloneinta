from rest_framework import generics
from .models import Post, Profile
from .serializers import PostSerializer, ProfileSerializer
from django.contrib.auth.models import User

class FeedListAPIView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

class ProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'user__username'
