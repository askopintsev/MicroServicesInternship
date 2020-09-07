from django.urls import path

from . import views

urlpatterns = [
    path("api/ad/tags/", views.TagDistinctListView.as_view()),
    path("api/ad/<int:pk>/short_info", views.AdShortDescrView.as_view()),
    path("api/ad/<int:pk>/", views.AdFullDescrView.as_view()),
    path("api/ad/filter/", views.AdFilterView.as_view()),
    path("api/ad/<int:pk>/image/", views.AdImageHandlerView.as_view()),
]
