from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Post, PostLike, PostComment, Notification

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Standart Django UserAdmin-di keńeytiw.
    Avatar, Bio, Website hám Followers maydanların qosamız.
    """
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Profile Info'), {'fields': ('avatar', 'bio', 'website', 'followers')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # ManyToMany maydanlar ushın
    filter_horizontal = ('groups', 'user_permissions', 'followers')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'caption_preview', 'created_at', 'likes_count', 'comments_count')
    list_filter = ('created_at', 'author')
    search_fields = ('caption', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def caption_preview(self, obj):
        return obj.caption[:50] + "..." if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = "Túsindirme"

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Like sanı"

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = "Pikir sanı"


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__caption')


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text_preview', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('text', 'user__username', 'post__caption')

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = "Pikir"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'type', 'post', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    list_editable = ('is_read',)