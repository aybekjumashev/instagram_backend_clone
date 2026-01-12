from rest_framework import serializers
from .models import CustomUser, Post, PostComment, Notification
from django.contrib.auth.password_validation import validate_password


class UserMiniSerializer(serializers.ModelSerializer):
    """
    Basqa modellerdiń ishinde (Nested) qollanıw ushın qısqasha User maǵlıwmatı.
    Mısalı: Posttıń avtorı, Kommentariy jazǵan adam.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    """
    Paydalanıwshınıń tolıq profili.
    Followers hám Following sanın qosamız (View-da annotate qılınǵan).
    """
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'avatar', 'bio', 'website', 
            'followers_count', 'following_count', 'is_following'
        ]
        read_only_fields = ['followers_count', 'following_count']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(id=request.user.id).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'text', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostCreateSerializer(serializers.ModelSerializer):
    """
    Post jaratıw ushın (Tekst hám Súwret).
    Avtor avtomatlıq qoyıladı.
    """
    class Meta:
        model = Post
        fields = ['id', 'image', 'caption']

class PostSerializer(serializers.ModelSerializer):
    """
    Posttı oqıw ushın (Feed hám Detail).
    Quramalı maǵlıwmatlardı óz ishine aladı.
    """
    author = UserMiniSerializer(read_only=True)
    
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    
    is_liked = serializers.SerializerMethodField()
    
    recent_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'image', 'caption', 
            'created_at', 'likes_count', 'comments_count', 
            'is_liked', 'recent_comments'
        ]

    def get_is_liked(self, obj):
        """Házirgi paydalanıwshı like basqan ba?"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_recent_comments(self, obj):
        """
        Postqa jazılǵan sońǵı 3 kommentariydi qaytaradı.
        """
        comments = obj.comments.all().order_by('-created_at')[:3]
        return CommentSerializer(comments, many=True).data

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    post_image = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'type', 'sender', 'post', 'post_image', 'is_read', 'created_at']

    def get_post_image(self, obj):
        if obj.post and obj.post.image:
            return obj.post.image.url
        return None

class RegisterSerializer(serializers.ModelSerializer):
    """
    Paydalanıwshını dizimnen ótkeriw ushın.
    Paroldi qayta tekseriw hám xeshlew (hash) kerek.
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'password_confirm', 'email', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Paroller sáykes kelmedi."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Paroldi ózgertiw ushın.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol qáte.")
        return value