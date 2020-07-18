from django.db import models


class Ad(models.Model):
    short_descr = models.CharField(max_length=100)
    full_descr = models.CharField(max_length=500)
    views_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField()
    photo = models.CharField(max_length=500, null=True)
    price = models.IntegerField(null=False, default=0)


class Tag(models.Model):
    tag_name = models.CharField(max_length=100)
    ad = models.ManyToManyField(Ad)
