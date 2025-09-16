from django.db import models

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,blank=True)
    content = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class DeletedPost(models.Model):
    original_id = models.IntegerField()
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,blank=True)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Deleted: {self.title}"