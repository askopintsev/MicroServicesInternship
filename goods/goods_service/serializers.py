from rest_framework import serializers

from .models import Ad, Tag


class AdShortSerializer(serializers.ModelSerializer):
    """Provides short preview of Ad model data"""

    class Meta:
        model = Ad
        fields = ("short_descr",)


class AdPhotoSerializer(serializers.ModelSerializer):
    """Provides Ad's image field to manage"""

    class Meta:
        model = Ad
        fields = ("photo",)


class AdUpdateSerializer(serializers.ModelSerializer):
    """Provides Ad's fields for update"""

    class Meta:
        model = Ad
        fields = (
            "short_descr",
            "full_descr",
            "price",
        )


class AdShowFullSerializer(serializers.ModelSerializer):
    """Provides full data of Ad model"""

    class Meta:
        model = Ad
        fields = (
            "short_descr",
            "full_descr",
            "tag",
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
