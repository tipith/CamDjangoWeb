from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from . import charts

urlpatterns = [
    path('', views.cameras, name='cameras'),
    path('event', views.event, name='event'),
    path('movement', views.movement, name='movement'),
    path('graph', views.graph, name='graph'),
    path('debug', views.debug, name='debug'),
    path('charts/<filename>.<extension>', charts.plot, name='plot'),
    path('api/pictures', views.PictureList.as_view()),
    path('api/events', views.EventList.as_view()),
    path('api/statistics', views.Statistics.as_view()),
    path('api/command', views.Command.as_view()),

    re_path(r'^static/data/(?P<filename>.*)$', views.retrieve_file),
]

urlpatterns = format_suffix_patterns(urlpatterns)
