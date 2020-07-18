from rest_framework import serializers
from .models import Ad, Tag


class AdShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('short_descr',)


class AdFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('short_descr', 'full_descr',
                  'views_cnt', 'photo', 'price', 'created_at', 'updated_at')


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tag_name',)
