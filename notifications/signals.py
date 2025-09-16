from django.db.models.signals import post_save,pre_save,pre_delete,m2m_changed
from django.dispatch import receiver
from .models import Post,DeletedPost
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone

def send_welcome_email(user_email):
    print(f"🎉 Welcome email sent to: {user_email}")

@receiver(pre_save, sender=Post)
def auto_generate_slug(sender, instance, **kwargs):
    if not instance.slug and instance.title:
        instance.slug = slugify(instance.title)
        print(f"📝 Auto-generated slug for Post: '{instance.slug}'")

@receiver(post_save, sender=User)
def send_user_welcome_notification(sender, instance, created, **kwargs):
    if created:
        send_welcome_email(instance.email)
        print(f"👤 New user created: {instance.username} ({instance.email})")

@receiver(pre_delete, sender=Post)
def backup_post_before_deletion(sender, instance, **kwargs):
    DeletedPost.objects.create(
        original_id=instance.id,
        title=instance.title,
        slug=instance.slug,
        content=instance.content,
        created_at=instance.created_at,
        updated_at=instance.updated_at
    )
    print(f"💾 Backed up Post before deletion: '{instance.title}' (ID: {instance.id})")

@receiver(m2m_changed,sender = Post.tags.through)
def track_post_tags_changes(sender,instance,action,pk_set,**kwargs):
    if action == 'pre_add':
        timestamp = timezone.now()
        print(f"🏷️  [{timestamp}] PRE_ADD - Post '{instance.title}' adding tags with PKs: {pk_set}")
    
    elif action == 'post_remove':
        timestamp = timezone.now()
        print(f"🗑️  [{timestamp}] POST_REMOVE - Post '{instance.title}' removed tags with PKs: {pk_set}")