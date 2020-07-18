import os
import sys

from rest_framework.exceptions import ValidationError

from .models import Ad, Tag
from .serializers import AdShortSerializer, AdFullSerializer, TagListSerializer
from rest_framework import generics
from django.db.models import F
from datetime import datetime, timedelta
import requests


class TagDistinctListView(generics.ListAPIView):
    serializer_class = TagListSerializer
    queryset = Tag.objects.all().distinct()


class AdShortDescrView(generics.RetrieveAPIView):
    serializer_class = AdShortSerializer

    def get_queryset(self):
        ad_id = self.kwargs['pk']
        queryset = Ad.objects.filter(id=ad_id)

        return queryset


class AdFullDescrView(generics.RetrieveAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs['pk']
        queryset = Ad.objects.filter(id=ad_id)
        queryset.filter(id=ad_id).update(views_cnt=F("views_cnt") + 1)

        return queryset


class AdUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs['pk']
        queryset = Ad.objects.filter(id=ad_id)
        # 2/?price=776
        ad_short_descr = self.request.query_params.get('short_descr',
                                                       queryset.values('short_descr').get()['short_descr'])
        ad_full_descr = self.request.query_params.get('full_descr', queryset.values('full_descr').get()['full_descr'])
        ad_photo = self.request.query_params.get('photo', queryset.values('photo').get()['photo'])
        ad_price = self.request.query_params.get('price', queryset.values('price').get()['price'])

        queryset.filter(id=ad_id).update(short_descr=ad_short_descr,
                                         full_descr=ad_full_descr,
                                         photo=ad_photo,
                                         price=ad_price,
                                         updated_at=datetime.now())

        return queryset


class AdFilterTagsView(generics.ListAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        tags = self.request.query_params.get('tags', None)
        if tags is not None:
            tags = tags.split(',')
        else:
            raise ValidationError('Please enter at least one tag or several tags separated with comma')
        queryset = Ad.objects.filter(tag__tag_name__in=tags)

        return queryset


class AdFilterDatesView(generics.ListAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        try:
            min_date = self.request.query_params.get('min_date', None)
            if min_date is not None:
                min_date_dt = datetime.strptime(min_date, '%Y-%m-%d')
            else:
                min_date_dt = datetime.strptime('1900-01-01', '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Incorrect min_date format. Please use format "YYYY-MM-DD"')

        try:
            max_date = self.request.query_params.get('max_date', None)
            if max_date is not None:
                max_date_dt = datetime.strptime(max_date, '%Y-%m-%d')
            else:
                max_date_dt = datetime.now() + timedelta(days=1)
        except ValueError:
            raise ValidationError('Incorrect max_date format. Please use format "YYYY-MM-DD"')

        queryset = Ad.objects.filter(created_at__range=(min_date_dt, max_date_dt))

        return queryset


class AdFilterPriceView(generics.ListAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        min_price = self.request.query_params.get('min_price', None)
        if min_price is None:
            min_price = 0

        max_price = self.request.query_params.get('max_price', None)
        if max_price is None:
            max_price = sys.maxsize

        queryset = Ad.objects.filter(price__range=(min_price, max_price))

        return queryset


class AdImageHandlerView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdFullSerializer

    def get_queryset(self):
        ad_id = self.kwargs['pk']
        queryset = Ad.objects.filter(pk=ad_id)

        command = self.request.query_params.get('command', None)
        if command == 'add' or command == 'update':
            image_url = self.request.query_params.get('image_url', None)
            if image_url is not None:
                image = requests.get(image_url)
                filename = str(ad_id)+'.jpeg'
                image_path = DiskWorker().save_to_disk(image.content, filename)
                queryset.filter(pk=ad_id).update(photo=image_path)
        if command == 'delete':
            os.remove(queryset.values('photo').get()['photo'])
            queryset.filter(pk=ad_id).update(photo=None)

        return queryset


class DiskWorker:
    """Class performs saving of the random image to local directory
    and search of image by given uuid"""

    def __init__(self):
        self.path = os.getcwd() + "/static/"

    def save_to_disk(self, file_data, file_name):
        """Function receives image data and name to save this in file in local directory.
        Returns full path to created file"""

        fullpath_to_file = self.path + file_name

        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(fullpath_to_file, 'wb') as file:
            file.write(file_data)

        return fullpath_to_file
