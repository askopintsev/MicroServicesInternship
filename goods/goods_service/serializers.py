from rest_framework import serializers

from .models import Ad, Tag


class AdShortSerializer(serializers.ModelSerializer):
    """Provides short preview of Ad model data"""

    class Meta:
        model = Ad
        fields = ("short_descr",)


class AdFullSerializer(serializers.ModelSerializer):
    """Provides full data of Ad model"""

    class Meta:
        model = Ad
        fields = (
            "short_descr",
            "full_descr",
            "views_cnt",
            "photo",
            "price",
            "created_at",
            "updated_at",
        )


class TagListSerializer(serializers.ModelSerializer):
    """Provides data of Tag model"""

    class Meta:
        model = Tag
        fields = ("tag_name",)
