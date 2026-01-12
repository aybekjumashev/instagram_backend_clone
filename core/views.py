from django.shortcuts import render
from rest_framework import viewsets, generics
from .models import CustomUser, Post, PostLike, PostComment, Notification
from .serializers import (CustomUserSerializer, PostSerializer, PostLikeSerializer, PostCommentSerializer, NotificationSerializer)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CustomUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', None)
        if q is not None:
            queryset = queryset.filter(username__icontains=q)
        
        return queryset

class CustomUserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

