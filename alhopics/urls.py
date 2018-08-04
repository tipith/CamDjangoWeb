from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import charts

urlpatterns = [
    url(r'^$', views.cameras, name='cameras'),
    url(r'^event$', views.event, name='event'),
    url(r'^movement$', views.movement, name='movement'),
    url(r'^graph$', views.graph, name='graph'),
    url(r'^debug$', views.debug, name='debug'),
    url(r'^charts/rpi_temp.png$', charts.rpi_temp, name='rpi_temp'),
    url(r'^charts/pics_per_day.png$', charts.pics_per_day, name='pics_per_day'),
    url(r'^charts/megabytes_per_day.png$', charts.megabytes_per_day, name='megabytes_per_day'),
    url(r'^static/data/(?P<filename>.*)$', views.retrieve_file),
    url(r'^api/pictures$', views.PictureList.as_view()),
    url(r'^api/events$', views.EventList.as_view()),
    url(r'^api/statistics$', views.Statistics.as_view()),
    url(r'^api/command$', views.Command.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
