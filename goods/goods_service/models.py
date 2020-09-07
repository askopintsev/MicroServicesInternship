from datetime import datetime

from django.db import models


class Tag(models.Model):
    """Model of Tag entity. Provides many-to-many relationship to Ad model"""

    tag_name = models.CharField(max_length=100)


class Ad(models.Model):
    """Model of Ad entity"""

    short_descr = models.CharField(max_length=100)
    full_descr = models.CharField(max_length=500)
    views_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.CharField(max_length=500, null=True)
    price = models.IntegerField(null=False, default=0)
    tag = models.ManyToManyField(Tag)

    def view_increment(self):
        self.views_cnt += 1

    def update_photo(self, photo_path):
        self.photo = photo_path
