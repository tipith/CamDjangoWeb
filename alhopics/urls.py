from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
    url(r'^$', views.cameras, name='cameras'),
    url(r'^event$', views.event, name='event'),
    url(r'^movement$', views.movement, name='movement'),
    url(r'^static/data/(?P<filename>.*)$', views.retrieve_file),
    #url(r'^static/(?P<filename>.*)$', views.retrieve_file_all),
    url(r'^api/pictures$', views.PictureList.as_view()),
    url(r'^api/events$', views.EventList.as_view()),
    url(r'^api/statistics$', views.Statistics.as_view()),
    url(r'^api/light$', views.Light.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
