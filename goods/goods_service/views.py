import os
import sys
from datetime import datetime, timedelta

from django.db.models import F

import requests
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Ad, Tag
from .serializers import AdFullSerializer, AdShortSerializer, TagListSerializer
from .utils import DiskWorker


class TagDistinctListView(generics.ListAPIView):
    """Class for Tags view.
    API endpoint: /api/tags"""

    serializer_class = TagListSerializer
    queryset = Tag.objects.all().distinct()


class AdShortDescrView(generics.RetrieveAPIView):
    """Class for Short Ad info view.
    API endpoint: /api/short/id"""

    serializer_class = AdShortSerializer

    def get_queryset(self):
        ad_id = self.kwargs["pk"]
        queryset = Ad.objects.filter(id=ad_id)

        return queryset


class AdFullDescrView(generics.RetrieveAPIView):
    """Class for Full Ad info view.
    API endpoint: /api/full/id"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs["pk"]
        queryset = Ad.objects.filter(id=ad_id)

        # updating views count
        queryset.filter(id=ad_id).update(views_cnt=F("views_cnt") + 1)

        return queryset


class AdUpdateView(generics.RetrieveUpdateAPIView):
    """Class for Ad parameters updating view.
    API endpoint: /api/update/id/+params"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs["pk"]
        queryset = Ad.objects.filter(id=ad_id)

        # receiving params value from request or get current value from DB
        ad_short_descr = self.request.query_params.get(
            "short_descr", queryset.values("short_descr").get()["short_descr"]
        )
        ad_full_descr = self.request.query_params.get(
            "full_descr", queryset.values("full_descr").get()["full_descr"]
        )
        ad_price = self.request.query_params.get(
            "price", queryset.values("price").get()["price"]
        )

        queryset.filter(id=ad_id).update(
            short_descr=ad_short_descr,
            full_descr=ad_full_descr,
            price=ad_price,
            updated_at=datetime.now(),
        )

        return queryset


class AdFilterTagsView(generics.ListAPIView):
    """Class for Ad filtering using tags.
    API endpoint: /api/tagsfilter/?tags=value1,value2"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        tags = self.request.query_params.get("tags", None)
        if tags is not None:
            tags = tags.split(",")
        else:
            raise ValidationError(
                "Please enter at least one tag or several tags separated with comma"
            )
        queryset = Ad.objects.filter(tag__tag_name__in=tags)

        return queryset


class AdFilterDatesView(generics.ListAPIView):
    """Class for Ad filtering using dates of creation.
    API endpoint: /api/datesfilter/+params"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        # handling of min_date param
        try:
            min_date = self.request.query_params.get("min_date", None)
            if min_date is not None:
                min_date_dt = datetime.strptime(min_date, "%Y-%m-%d")
            else:
                min_date_dt = datetime.strptime("1900-01-01", "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                'Incorrect min_date format. Please use format "YYYY-MM-DD"'
            )

        # handling of max_date param
        try:
            max_date = self.request.query_params.get("max_date", None)
            if max_date is not None:
                max_date_dt = datetime.strptime(max_date, "%Y-%m-%d")
            else:
                max_date_dt = datetime.now() + timedelta(days=1)
        except ValueError:
            raise ValidationError(
                'Incorrect max_date format. Please use format "YYYY-MM-DD"'
            )

        queryset = Ad.objects.filter(created_at__range=(min_date_dt, max_date_dt))

        return queryset


class AdFilterPriceView(generics.ListAPIView):
    """Class for Ad filtering using price.
    API endpoint: /api/pricefilter/+params"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        # handling min_price
        min_price = self.request.query_params.get("min_price", None)
        if min_price is None:
            min_price = 0

        # handling max_price
        max_price = self.request.query_params.get("max_price", None)
        if max_price is None:
            max_price = sys.maxsize

        queryset = Ad.objects.filter(price__range=(min_price, max_price))

        return queryset


class AdImageHandlerView(generics.RetrieveUpdateDestroyAPIView):
    """Class for Ad image management.
    Supports features: add image, update image, delete image.
    Image is stored in /static/ directory and saved as path to file in DB.
    API endpoint: /api/image/id/+params"""

    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs["pk"]
        queryset = Ad.objects.filter(pk=ad_id)

        # handling command type
        command = self.request.query_params.get("command", None)
        # add and update are the same in fact
        if command == "add" or command == "update":
            image_url = self.request.query_params.get("image_url", None)

            # get image data, save to disk and store the path in DB
            if image_url is not None:
                image = requests.get(image_url)
                image_path = DiskWorker().save_to_disk(image.content, ad_id)
                queryset.filter(pk=ad_id).update(photo=image_path)

        if command == "delete":
            os.remove(queryset.values("photo").get()["photo"])
            queryset.filter(pk=ad_id).update(photo=None)

        return queryset
