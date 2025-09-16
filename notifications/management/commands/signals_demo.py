from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from notifications.models import Post, Tag, DeletedPost
import time


class Command(BaseCommand):
    help = 'Demonstrate Django signals functionality'

    def handle(self, *args, **options):
        """Main command handler to demonstrate all signal functionality."""
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('🚀 DJANGO SIGNALS DEMONSTRATION')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Clear previous queries
        connection.queries.clear()
        
        self.demo_slug_generation()
        self.demo_user_welcome()
        self.demo_post_deletion_backup()
        self.demo_m2m_changes()
        
        self.stdout.write(
            self.style.SUCCESS('\n' + '=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS('📊 DEMONSTRATION COMPLETED')
        )
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )

    def demo_slug_generation(self):
        """Demonstrate automatic slug generation for Post model."""
        self.stdout.write(
            self.style.WARNING('\n🔸 1. TESTING AUTOMATIC SLUG GENERATION')
        )
        self.stdout.write('-' * 40)
        
  
        queries_before = len(connection.queries)
        
     
        post1 = Post.objects.create(
            title="My Amazing Blog Post",
            content="This is some content"
        )
        
        post2 = Post.objects.create(
            title="Another Great Post",
            slug="custom-slug",
            content="More content here"
        )
        
        post1.title = "Updated Amazing Blog Post"
        post1.save()
        
        queries_after = len(connection.queries)
        new_queries = connection.queries[queries_before:queries_after]
        
        self.stdout.write(f"✅ Created Post 1 - Title: '{post1.title}', Slug: '{post1.slug}'")
        self.stdout.write(f"✅ Created Post 2 - Title: '{post2.title}', Slug: '{post2.slug}'")
        self.stdout.write(f"✅ Updated Post 1 - Title: '{post1.title}', Slug: '{post1.slug}'")
        
        self.stdout.write(f"\n📋 SQL Queries executed ({len(new_queries)}):")
        for i, query in enumerate(new_queries, 1):
            self.stdout.write(f"  {i}. {query['sql'][:100]}...")

    def demo_user_welcome(self):
        self.stdout.write(
            self.style.WARNING('\n🔸 2. TESTING USER WELCOME NOTIFICATION')
        )
        self.stdout.write('-' * 40)
        
        queries_before = len(connection.queries)
        
        username = f"testuser_{int(time.time())}"
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="testpass123"
        )
        
        user.first_name = "Test"
        user.save()
        
        queries_after = len(connection.queries)
        new_queries = connection.queries[queries_before:queries_after]
        
        self.stdout.write(f"✅ Created User: {user.username} ({user.email})")
        self.stdout.write(f"✅ Updated User: {user.username} - first_name set to '{user.first_name}'")
        
        self.stdout.write(f"\n📋 SQL Queries executed ({len(new_queries)}):")
        for i, query in enumerate(new_queries, 1):
            self.stdout.write(f"  {i}. {query['sql'][:100]}...")

    def demo_post_deletion_backup(self):
        """Demonstrate post deletion backup signal."""
        self.stdout.write(
            self.style.WARNING('\n🔸 3. TESTING POST DELETION BACKUP')
        )
        self.stdout.write('-' * 40)
        
        queries_before = len(connection.queries)
        
        # Create a post to delete
        post_to_delete = Post.objects.create(
            title="Post to be Deleted",
            content="This post will be deleted and backed up"
        )
        original_id = post_to_delete.id
        
        # Count deleted posts before deletion
        deleted_count_before = DeletedPost.objects.count()
        
        # Delete the post (should trigger backup)
        post_to_delete.delete()
        
        # Verify backup was created
        deleted_count_after = DeletedPost.objects.count()
        backup_post = DeletedPost.objects.get(original_id=original_id)
        
        queries_after = len(connection.queries)
        new_queries = connection.queries[queries_before:queries_after]
        
        self.stdout.write(f"✅ Created Post for deletion: ID {original_id}")
        self.stdout.write(f"✅ Post deleted successfully")
        self.stdout.write(f"✅ Backup created - DeletedPost count: {deleted_count_before} → {deleted_count_after}")
        self.stdout.write(f"✅ Backup details - Title: '{backup_post.title}', Deleted at: {backup_post.deleted_at}")
        
        self.stdout.write(f"\n📋 SQL Queries executed ({len(new_queries)}):")
        for i, query in enumerate(new_queries, 1):
            self.stdout.write(f"  {i}. {query['sql'][:100]}...")

    def demo_m2m_changes(self):
        """Demonstrate many-to-many change tracking signals."""
        self.stdout.write(
            self.style.WARNING('\n🔸 4. TESTING M2M CHANGE TRACKING')
        )
        self.stdout.write('-' * 40)
        
        queries_before = len(connection.queries)
        
        # Create tags
        tag1, _ = Tag.objects.get_or_create(name="django")
        tag2, _ = Tag.objects.get_or_create(name="python")
        tag3, _ = Tag.objects.get_or_create(name="signals")
        
        # Create a post
        post = Post.objects.create(
            title="M2M Demo Post",
            content="Testing many-to-many signals"
        )
        
        # Add tags (should trigger pre_add signal)
        self.stdout.write("🏷️  Adding tags to post...")
        post.tags.add(tag1, tag2)
        
        # Remove tags (should trigger post_remove signal)
        self.stdout.write("🗑️  Removing tags from post...")
        post.tags.remove(tag1)
        
        # Add more tags
        self.stdout.write("🏷️  Adding more tags to post...")
        post.tags.add(tag3)
        
        queries_after = len(connection.queries)
        new_queries = connection.queries[queries_before:queries_after]
        
        current_tags = post.tags.all()
        self.stdout.write(f"✅ Post created: '{post.title}'")
        self.stdout.write(f"✅ Final tags on post: {[tag.name for tag in current_tags]}")
        
        self.stdout.write(f"\n📋 SQL Queries executed ({len(new_queries)}):")
        for i, query in enumerate(new_queries, 1):
            self.stdout.write(f"  {i}. {query['sql'][:100]}...")