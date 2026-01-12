from django.db.models import Count
from rest_framework import viewsets, permissions, status, filters, generics
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from .models import CustomUser, Post, PostLike, PostComment, Notification
from .serializers import (
    UserSerializer, 
    PostSerializer, 
    PostCreateSerializer,
    CommentSerializer,
    NotificationSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAuthorOrReadOnly




class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Paydalanıwshılardı kóriw hám olarǵa jazılıw (Follow).
    ReadOnly - sebebi paydalanıwshını jaratıw (Register) bólek auth view-da boladı.
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name']

    def get_queryset(self):
        return CustomUser.objects.annotate(
            followers_count=Count('followers'),
            following_count=Count('following')
        )
    
    def get_serializer_class(self):
        """
        Hár qıylı action (háreket) ushın hár qıylı serializer qaytarıw.
        """
        if self.action == 'change_password':
            return ChangePasswordSerializer
        
        return UserSerializer

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        """
        /api/users/me/
        GET: Óz profilimdi kóriw.
        PATCH: Óz profilimdi (avatar, bio, website) ózgertiw.
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        /api/users/change-password/
        """
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Parol tabıslı ózgertildi."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['post'], url_path='follow')
    def follow(self, request, pk=None):
        """Paydalanıwshıǵa jazılıw"""
        target_user = self.get_object()
        user = request.user
        
        if target_user == user:
            return Response(
                {"detail": "Óz-ozińizge jazıla almaysız."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        target_user.followers.add(user)
        return Response({"detail": "Siz jazıldıńız."}, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['post'])
    def unfollow(self, request, pk=None):
        """Jazılıwdı bıykar etiw"""
        target_user = self.get_object()
        user = request.user
        target_user.followers.remove(user)
        return Response({"detail": "Jazılıw bıykar etildi."}, status=status.HTTP_200_OK)
    
    
    

class PostViewSet(viewsets.ModelViewSet):
    """
    Postlar menen islesiw (CRUD), Feed, Like hám Kommentariy.
    """
    filter_backends = [filters.SearchFilter]
    search_fields = ['caption']

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action == 'comment':
            return CommentSerializer
        return PostSerializer
    
    def get_permissions(self):
        """
        Hár qıylı háreketler ushın hár qıylı ruxsatlar.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Post.objects.select_related('author').prefetch_related(
            'comments', 'comments__user'
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        """
        News Feed: Tek men jazılǵan (follow qılǵan) adamlardıń postları.
        """
        user = request.user
        following_ids = user.following.values_list('id', flat=True)
        
        posts = self.get_queryset().filter(author_id__in=following_ids)
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(request=None, responses={200: None})
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like basıw yamasa qaytarıp alıw (Toggle)"""
        post = self.get_object()
        user = request.user

        like_obj = PostLike.objects.filter(user=user, post=post).first()
        if like_obj:
            like_obj.delete()
            return Response({"detail": "Like alındı."}, status=status.HTTP_200_OK)
        
        PostLike.objects.create(user=user, post=post)
        return Response({"detail": "Like basıldı."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """Postqa kommentariy qaldırıw"""
        post = self.get_object()
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            receiver=self.request.user
        ).select_related('sender', 'post').order_by('-created_at')