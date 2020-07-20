from django.urls import path

from . import views

urlpatterns = [
    path("api/tags/", views.TagDistinctListView.as_view()),
    path("api/short/<int:pk>", views.AdShortDescrView.as_view()),
    path("api/full/<int:pk>", views.AdFullDescrView.as_view()),
    path("api/update/<int:pk>/", views.AdUpdateView.as_view()),
    path("api/tagsfilter/", views.AdFilterTagsView.as_view()),
    path("api/datesfilter/", views.AdFilterDatesView.as_view()),
    path("api/pricefilter/", views.AdFilterPriceView.as_view()),
    path("api/image/<int:pk>/", views.AdImageHandlerView.as_view()),
]
