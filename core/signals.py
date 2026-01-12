from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import CustomUser, PostLike, PostComment, Notification

@receiver(post_save, sender=PostLike)
def notify_post_like(sender, instance, created, **kwargs):
    """
    Paydalanıwshı postqa like basqanda (created=True) iske túsedi.
    """
    if created:
        like = instance
        post = like.post
        sender_user = like.user
        receiver_user = post.author

        if sender_user != receiver_user:
            Notification.objects.create(
                sender=sender_user,
                receiver=receiver_user,
                type='like',
                post=post
            )

@receiver(post_save, sender=PostComment)
def notify_post_comment(sender, instance, created, **kwargs):
    """
    Paydalanıwshı kommentariy jazǵanda iske túsedi.
    """
    if created:
        comment = instance
        post = comment.post
        sender_user = comment.user
        receiver_user = post.author

        if sender_user != receiver_user:
            Notification.objects.create(
                sender=sender_user,
                receiver=receiver_user,
                type='comment',
                post=post
            )

@receiver(m2m_changed, sender=CustomUser.followers.through)
def notify_user_follow(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    CustomUser.followers (ManyToMany) ózgergende iske túsedi.
    action='post_add' - bul jańa jazılıwshı qosıldı degeni.
    """
    if action == 'post_add':
        # instance: Kimge jazılıp atır (Qabıllawshı)
        # pk_set: Kim jazılıp atır (Jiberiwshi ID-leri)
        
        receiver_user = instance
        
        for follower_id in pk_set:
            sender_user = CustomUser.objects.get(pk=follower_id)
            
            if sender_user != receiver_user:
                Notification.objects.create(
                    sender=sender_user,
                    receiver=receiver_user,
                    type='follow',
                    post=None # Follow ushın post kerek emes
                )