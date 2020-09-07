import os
import sys
from datetime import datetime, timedelta

from django.db.models import Q

import requests
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import *
from .utils import DiskWorker


class TagDistinctListView(generics.ListAPIView):
    """Class for Tags view.
    API endpoint: /api/ad/tags"""

    serializer_class = TagListSerializer
    queryset = Tag.objects.all().distinct()


class AdShortDescrView(generics.RetrieveAPIView):
    """Class for Short Ad info view.
    API endpoint: /api/ad/id/short_info"""

    serializer_class = AdShortSerializer

    def get_queryset(self):
        ad_id = self.kwargs["pk"]
        queryset = Ad.objects.filter(id=ad_id)

        return queryset


class AdFullDescrView(generics.RetrieveUpdateAPIView):
    """Class for Full Ad info view.
    API endpoint: /api/ad/id"""

    queryset = Ad.objects.all()
    serializer_class = AdShowFullSerializer

    # for GET requests
    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        # updating views count for ad
        instance.view_increment()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        self.perform_update(serializer)

        return Response(serializer.data)

    # for PUT/PATCH requests
    def update(self, request, *args, **kwargs):

        partial = kwargs.get("partial", False)

        instance = self.get_object()

        serializer = AdUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class AdFilterView(generics.ListAPIView):
    """Class for Ad filtering ads.
    API endpoint: /api/ad/filter/?params"""

    serializer_class = AdShowFullSerializer
    filterset_fields = ("tag", "created_at", "price")

    def get_queryset(self):

        # handling tags filter
        tags = self.request.query_params.get("tags", None)
        if tags:
            tags = tags.split(",")
            queryset = Ad.objects.filter(Q(tag__tag_name__in=tags))
        else:
            queryset = Ad.objects.all()

        # handling of min_date param filter
        try:
            min_date = self.request.query_params.get("min_date")
            if min_date:
                min_date_dt = datetime.strptime(min_date, "%Y-%m-%d")
            else:
                min_date_dt = datetime.strptime("1900-01-01", "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                'Incorrect min_date format. Please use format "YYYY-MM-DD"'
            )

        # handling of max_date param filter
        try:
            max_date = self.request.query_params.get("max_date")
            if max_date:
                max_date_dt = datetime.strptime(max_date, "%Y-%m-%d")
            else:
                max_date_dt = datetime.now() + timedelta(days=1)
        except ValueError:
            raise ValidationError(
                'Incorrect max_date format. Please use format "YYYY-MM-DD"'
            )

        # handling min_price filter
        min_price = self.request.query_params.get("min_price")
        if min_price is None:
            min_price = 0

        # handling max_price filter
        max_price = self.request.query_params.get("max_price")
        if max_price is None:
            max_price = sys.maxsize

        # getting final data
        queryset = queryset.filter(
            Q(created_at__range=(min_date_dt, max_date_dt)),
            Q(price__range=(min_price, max_price)),
        )

        return queryset


class AdImageHandlerView(generics.UpdateAPIView):
    """Class for Ad image management.
    Supports features: add image, update image, delete image.
    Image is stored in /static/ directory and saved as path to file in DB.
    API endpoint: /api/ad/id/image/+url or 'delete' string"""

    serializer_class = AdPhotoSerializer
    queryset = Ad.objects.all()

    def update(self, request, *args, **kwargs):

        partial = self.kwargs.get("partial", False)
        content = self.request.query_params.get("photo")

        if content == "delete":
            # removing image from DB and local directory
            instance = self.get_object()
            if instance.photo:
                os.remove(instance.photo)

            # updating info in serializer
            serializer = self.get_serializer(
                instance, data={"photo": None}, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)

        else:
            # getting image data
            try:
                image = requests.get(content)
                image.raise_for_status()
            except requests.exceptions.MissingSchema as erru:
                return Response(str(erru))
            except requests.exceptions.HTTPError as errh:
                print("Http Error: ", str(errh))
            except requests.exceptions.ConnectionError as errc:
                print("Connecting Error: ", str(errc))
            except requests.exceptions.Timeout as errt:
                print("Timeout Error: ", str(errt))
            except requests.exceptions.RequestException as err:
                print("Error: ", str(err))

            image_path = DiskWorker().save_to_disk(image.content, self.kwargs["pk"])

            # updating instance with new image info
            instance = self.get_object()
            if instance.photo:  # check if image data exist, then delete
                os.remove(instance.photo)
            instance.update_photo(image_path)

            # sending new image info to serializer
            serializer = self.get_serializer(
                instance, data={"photo": image_path}, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)
