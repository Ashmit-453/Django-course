# Django Signals Implementation Report

## Overview
This implementation demonstrates comprehensive Django signal handling including automatic slug generation, user welcome notifications, pre-deletion backups, and many-to-many relationship change tracking.

## Signal Receivers Implementation

### 1. Automatic Slug Generation (`pre_save`)

**Signal:** `pre_save`  
**Sender:** `Post` model  
**Receiver Function:** `auto_generate_slug`

**Arguments Used:**
- `sender`: The model class (Post)
- `instance`: The model instance being saved
- `**kwargs`: Additional keyword arguments

**Functionality:**
- Triggers before a Post instance is saved to the database
- Automatically generates a slug from the title using `slugify()` if the slug field is empty
- Does not call `instance.save()` to avoid recursion
- Only modifies the slug if it's currently empty (preserves existing slugs)

**Sample Output:**
```
📝 Auto-generated slug for Post: 'my-amazing-blog-post'
```

**Key Implementation Details:**
- Uses `if not instance.slug and instance.title:` to ensure slug is only generated when needed
- Uses Django's `slugify()` function for proper URL-safe slug generation
- Avoids infinite recursion by not calling save within the handler

---

### 2. User Welcome Notification (`post_save`)

**Signal:** `post_save`  
**Sender:** `User` model (Django's built-in)  
**Receiver Function:** `send_user_welcome_notification`

**Arguments Used:**
- `sender`: The model class (User)
- `instance`: The User instance that was saved
- `created`: Boolean indicating if this is a new instance
- `**kwargs`: Additional keyword arguments

**Functionality:**
- Triggers after a User instance is saved to the database
- Sends welcome email only for newly created users (when `created=True`)
- Uses dummy `send_welcome_email()` function that prints notification
- Prevents recursion by checking the `created` flag

**Sample Output:**
```
🎉 Welcome email sent to: testuser_1234567890@example.com
👤 New user created: testuser_1234567890 (testuser_1234567890@example.com)
```

**Key Implementation Details:**
- Uses `if created:` to ensure notification only sent for new users
- Does not modify the instance, avoiding any save() calls
- Implements dummy email function for demonstration purposes

---

### 3. Pre-Deletion Backup (`pre_delete`)

**Signal:** `pre_delete`  
**Sender:** `Post` model  
**Receiver Function:** `backup_post_before_deletion`

**Arguments Used:**
- `sender`: The model class (Post)
- `instance`: The Post instance being deleted
- `**kwargs`: Additional keyword arguments

**Functionality:**
- Triggers before a Post instance is deleted from the database
- Creates a backup record in the `DeletedPost` model with all original data
- Stores the original instance ID, timestamps, and content
- Does not prevent the actual deletion from occurring

**Sample Output:**
```
💾 Backed up Post before deletion: 'Post to be Deleted' (ID: 123)
```

**Key Implementation Details:**
- Creates `DeletedPost` instance with all relevant fields from the original
- Includes `original_id` to track the source post
- Adds `deleted_at` timestamp automatically via `auto_now_add=True`
- Does not interfere with the deletion process

---

### 4. Many-to-Many Change Tracking (`m2m_changed`)

**Signal:** `m2m_changed`  
**Sender:** `Post.tags.through` (the intermediate model)  
**Receiver Function:** `track_post_tags_changes`

**Arguments Used:**
- `sender`: The intermediate model class
- `instance`: The Post instance whose relationships are changing
- `action`: The type of change ('pre_add', 'post_add', 'pre_remove', 'post_remove', etc.)
- `pk_set`: Set of primary keys of the related objects being added/removed
- `**kwargs`: Additional keyword arguments

**Functionality:**
- Monitors changes to the many-to-many relationship between Post and Tag models
- Logs `pre_add` actions when tags are about to be added
- Logs `post_remove` actions after tags have been removed
- Uses `django.utils.timezone.now()` for accurate timestamps

**Sample Output:**
```
🏷️  [2025-01-15 10:30:45.123456+00:00] PRE_ADD - Post 'M2M Demo Post' adding tags with PKs: {1, 2}
🗑️  [2025-01-15 10:30:47.789012+00:00] POST_REMOVE - Post 'M2M Demo Post' removed tags with PKs: {1}
```

**Key Implementation Details:**
- Handles multiple M2M actions but focuses on `pre_add` and `post_remove`
- Uses timezone-aware timestamps for accurate logging
- Logs the post title and affected primary keys for clarity
- Does not modify the relationships, only observes them

---

## Models Implementation

### Post Model
```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)  # Can be empty for auto-generation
    content = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### DeletedPost Model
```python
class DeletedPost(models.Model):
    original_id = models.IntegerField()  # Stores the original Post ID
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField()  # Original creation time
    updated_at = models.DateTimeField()  # Original update time
    deleted_at = models.DateTimeField(auto_now_add=True)  # Deletion timestamp
```

### Tag Model
```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
```

---

## App Configuration

### notifications/apps.py
The `NotificationsConfig` class properly imports signals in the `ready()` method:

```python
def ready(self):
    """Import signal handlers when the app is ready."""
    import notifications.signals
```

This ensures signal handlers are registered when Django starts up.

---

## Management Command

### signals_demo Command
The `manage.py signals_demo` command demonstrates all signal functionality:

1. **Slug Generation Demo**: Creates posts with and without slugs, shows auto-generation
2. **User Welcome Demo**: Creates new user and updates existing user
3. **Deletion Backup Demo**: Creates and deletes a post, verifies backup creation
4. **M2M Tracking Demo**: Adds and removes tags, shows signal logging

**Usage:**
```bash
python manage.py signals_demo
```

The command also tracks and displays SQL queries executed during each demonstration phase using `connection.queries`.

---

## Sample Complete Output

 DJANGO SIGNALS DEMONSTRATION
============================================================

🔸 1. TESTING AUTOMATIC SLUG GENERATION
----------------------------------------
📝 Auto-generated slug for Post: 'my-amazing-blog-post'
✅ Created Post 1 - Title: 'Updated Amazing Blog Post', Slug: 'my-amazing-blog-post'
✅ Created Post 2 - Title: 'Another Great Post', Slug: 'custom-slug'
✅ Updated Post 1 - Title: 'Updated Amazing Blog Post', Slug: 'my-amazing-blog-post'

📋 SQL Queries executed (3):
  1. INSERT INTO "notifications_post" ("title", "slug", "content", "created_at", "updated_at") VALUES ('M...
  2. INSERT INTO "notifications_post" ("title", "slug", "content", "created_at", "updated_at") VALUES ('A...
  3. UPDATE "notifications_post" SET "title" = 'Updated Amazing Blog Post', "slug" = 'my-amazing-blog-pos...

🔸 2. TESTING USER WELCOME NOTIFICATION
----------------------------------------
🎉 Welcome email sent to: testuser_1758016719@example.com
👤 New user created: testuser_1758016719 (testuser_1758016719@example.com)
✅ Created User: testuser_1758016719 (testuser_1758016719@example.com)
✅ Updated User: testuser_1758016719 - first_name set to 'Test'

📋 SQL Queries executed (2):
  1. INSERT INTO "auth_user" ("password", "last_login", "is_superuser", "username", "first_name", "last_n...
  2. UPDATE "auth_user" SET "password" = 'pbkdf2_sha256$1000000$d7PAVwsamZRWmZ4IjAfIXe$3IInCGX5cNNDWulgNm...

🔸 3. TESTING POST DELETION BACKUP
----------------------------------------
📝 Auto-generated slug for Post: 'post-to-be-deleted'
💾 Backed up Post before deletion: 'Post to be Deleted' (ID: 3)
✅ Created Post for deletion: ID 3
✅ Post deleted successfully
✅ Backup created - DeletedPost count: 0 → 1
✅ Backup details - Title: 'Post to be Deleted', Deleted at: 2025-09-16 09:58:40.031091+00:00

📋 SQL Queries executed (9):
  1. INSERT INTO "notifications_post" ("title", "slug", "content", "created_at", "updated_at") VALUES ('P...
  2. SELECT COUNT(*) AS "__count" FROM "notifications_deletedpost"...
  3. BEGIN...
  4. INSERT INTO "notifications_deletedpost" ("original_id", "title", "slug", "content", "created_at", "u...
  5. DELETE FROM "notifications_post_tags" WHERE "notifications_post_tags"."post_id" IN (3)...
  6. DELETE FROM "notifications_post" WHERE "notifications_post"."id" IN (3)...
  7. COMMIT...
  8. SELECT COUNT(*) AS "__count" FROM "notifications_deletedpost"...
  9. SELECT "notifications_deletedpost"."id", "notifications_deletedpost"."original_id", "notifications_d...

🔸 4. TESTING M2M CHANGE TRACKING
----------------------------------------
📝 Auto-generated slug for Post: 'm2m-demo-post'
🏷️  Adding tags to post...
🏷️  [2025-09-16 09:58:40.106066+00:00] PRE_ADD - Post 'M2M Demo Post' adding tags with PKs: {1, 2}
🗑️  Removing tags from post...
🗑️  [2025-09-16 09:58:40.117076+00:00] POST_REMOVE - Post 'M2M Demo Post' removed tags with PKs: {1 }
🏷️  Adding more tags to post...
🏷️  [2025-09-16 09:58:40.124067+00:00] PRE_ADD - Post 'M2M Demo Post' adding tags with PKs: {3}
✅ Post created: 'M2M Demo Post'
✅ Final tags on post: ['python', 'signals']

SQL Queries executed (24):
  1. SELECT "notifications_tag"."id", "notifications_tag"."name" FROM "notifications_tag" WHERE "notifica...
  2. BEGIN...
  3. INSERT INTO "notifications_tag" ("name") VALUES ('django') RETURNING "notifications_tag"."id"...
  4. COMMIT...
  5. SELECT "notifications_tag"."id", "notifications_tag"."name" FROM "notifications_tag" WHERE "notifica...
  6. BEGIN...
  7. INSERT INTO "notifications_tag" ("name") VALUES ('python') RETURNING "notifications_tag"."id"...
  8. COMMIT...
  9. SELECT "notifications_tag"."id", "notifications_tag"."name" FROM "notifications_tag" WHERE "notifica...
  10. BEGIN...
  11. INSERT INTO "notifications_tag" ("name") VALUES ('signals') RETURNING "notifications_tag"."id"...
  12. COMMIT...
  13. INSERT INTO "notifications_post" ("title", "slug", "content", "created_at", "updated_at") VALUES ('M...
  14. BEGIN...
  15. SELECT "notifications_post_tags"."tag_id" AS "tag" FROM "notifications_post_tags" WHERE ("notificati...
  16. INSERT OR IGNORE INTO "notifications_post_tags" ("post_id", "tag_id") VALUES (4, 1), (4, 2)...
  17. COMMIT...
  18. BEGIN...
  19. DELETE FROM "notifications_post_tags" WHERE ("notifications_post_tags"."post_id" = 4 AND "notificati...
  20. COMMIT...
  21. BEGIN...
  22. SELECT "notifications_post_tags"."tag_id" AS "tag" FROM "notifications_post_tags" WHERE ("notificati...
  23. INSERT OR IGNORE INTO "notifications_post_tags" ("post_id", "tag_id") VALUES (4, 3)...
  24. COMMIT...