import os
import logging
import datetime

from django.conf import settings
from django.utils import timezone
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, permissions
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required

from django.contrib.staticfiles.templatetags.staticfiles import static

import Messaging
import Message


from .models import Camera, Picture, Picturemovement, Lightcontrol, Movement, StatisticsResponse, LightResponse

logger = logging.getLogger(__name__)


num_of_pics = 16
num_of_events = 20


def get_absolute_filename(filename='', safe=True):
    if not filename:
        return os.path.join(settings.STATIC_ROOT, 'index')
    if safe and '..' in filename.split(os.path.sep):
        return get_absolute_filename(filename='')
    return static(filename)


#@login_required
def retrieve_file(request, filename=''):
    logger.info(filename)
    response = HttpResponse()  # 200 OK
    del response['content-type']  # We'll let the web server guess this.
    response['X-Sendfile'] = settings.BASE_DIR + '/alhopics/' + static('data/' + filename)
    return response


def retrieve_file_all(request, filename=''):
    response = HttpResponse()  # 200 OK
    del response['content-type']  # We'll let the web server guess this.
    response['X-Sendfile'] = settings.BASE_DIR + '/alhopics' + static(filename)
    return response


@login_required
def cameras(request):
    context = {'cameras': [1, 2], 'type': 'picture', 'user': request.user}
    return render(request, 'alhopics/index.html', context)


@login_required
def event(request):
    context = {'user': request.user}
    return render(request, 'alhopics/events.html', context)


@login_required
def movement(request):
    context = {'cameras': [1, 2], 'type': 'movement', 'user': request.user}
    return render(request, 'alhopics/movement.html', context)


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('idpicture', 'timestamp', 'idcamera', 'filelocation', 'filesize')


class PictureList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    """
    Returns a list of pictures.

    Mandatory GET parameters are:
    camera -- Camera number index starting from 1

    Optional GET parameters are:
    dir    -- Direction of the request. Can be either 'next' or 'prev'. (default: 'prev')
    type   -- Selects which type of images are returned. Can be either 'picture' or 'movement' (default: 'picture')
    date   -- Date for the requested images. (default: latest images)
    """
    def get(self, request, format=None):
        params = request.query_params
        logger.info(params)

        pic_type = params.get('type', 'picture')
        if pic_type not in ['movement', 'picture']:
            logger.info("Invalid type")
            raise Http404("Invalid type")

        if pic_type == 'movement':
            pics = Picturemovement.objects.all()
        else:
            pics = Picture.objects.all()

        camera_id = params.get('camera', None)

        if not camera_id:
            logger.info("Camera id is missing")
            raise Http404("Camera id is missing")

        cam = get_object_or_404(Camera, pk=camera_id)
        pics = pics.filter(idcamera=camera_id)

        pic_dir = params.get('dir', 'prev')
        if pic_dir not in ['next', 'prev']:
            logger.info("Invalid direction")
            raise Http404("Invalid direction")

        datestring = params.get('date', None)
        if datestring:
            try:
                #search_date = timezone.localtime(timezone.make_aware(datetime.datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S.%fZ')))
                search_date = datetime.datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=2)
            except ValueError :
                logger.info("Invalid date")
                raise Http404("Invalid date")
        else:
            #search_date = timezone.localtime(timezone.now())
            search_date = timezone.now()

        if pic_dir == 'next':
            pics = pics.filter(timestamp__gte=search_date).order_by('timestamp')[:num_of_pics]
        else:
            pics = reversed(pics.filter(timestamp__lte=search_date).order_by('-timestamp')[:num_of_pics])

        logger.info('searching from %s' % search_date)
        #logger.info(pics.query)

        serializer = PictureSerializer(pics, many=True)
        return Response(serializer.data)


class LightEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lightcontrol
        fields = ('starttimestamp', 'idcamera', 'endtimestamp')


class MovementEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movement
        fields = ('starttimestamp', 'idcamera', 'endtimestamp', 'detector')


class EventList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    """
    Returns a list of events.

    Mandatory GET parameters are:
    type   -- Selects which type of events are returned. Can be either 'light' or 'movement'
    """
    def get(self, request, format=None):
        params = request.query_params
        logger.info(params)

        event_type = params.get('type', None)

        if not event_type:
            logger.info("Event is missing")
            raise Http404("Event is missing")

        if event_type not in ['light', 'movement']:
            logger.info("Invalid event")
            raise Http404("Invalid event")

        if event_type == 'light':
            events = Lightcontrol.objects.order_by('idlightcontrol').order_by('-starttimestamp')[:num_of_events]
            serializer = LightEventSerializer(events, many=True)
        else:
            events = Movement.objects.order_by('idmovement').order_by('-starttimestamp')[:num_of_events]
            serializer = MovementEventSerializer(events, many=True)

        return Response(serializer.data)


class StatisticsSerializer(serializers.ModelSerializer):
    data_month = serializers.IntegerField()
    data_day = serializers.IntegerField()
    pics_month = serializers.IntegerField()
    pics_day = serializers.IntegerField()

    class Meta:
        model = StatisticsResponse
        fields = '__all__'


class Statistics(APIView):
    permission_classes = [permissions.IsAuthenticated]

    """
    Returns a list of events.

    Mandatory GET parameters are:
    type   -- Selects which type of events are returned. Can be either 'light' or 'movement'
    """
    def get(self, request, format=None):
        params = request.query_params
        logger.info(params)

        pic_type = params.get('type', 'picture')
        if pic_type not in ['movement', 'picture']:
            logger.info("Invalid type")
            raise Http404("Invalid type")

        if pic_type == 'movement':
            pics = Picturemovement.objects.all()
        else:
            pics = Picture.objects.all()

        camera_id = params.get('camera', None)

        if not camera_id:
            logger.info("Camera id is missing")
            raise Http404("Camera id is missing")

        cam = get_object_or_404(Camera, pk=camera_id)

        #month_ago = timezone.localtime(timezone.now()) - datetime.timedelta(days=30)
        #day_ago = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
        month_ago = timezone.now() - datetime.timedelta(days=30)
        day_ago = timezone.now() - datetime.timedelta(days=1)

        month = dict(pics.filter(idcamera=camera_id, timestamp__gte=month_ago).aggregate(Sum('filesize'), Count('filesize')))
        day = dict(pics.filter(idcamera=camera_id, timestamp__gte=day_ago).aggregate(Sum('filesize'), Count('filesize')))
        logger.info(month)
        logger.info(day)
        stat = StatisticsResponse(month['filesize__sum'], day['filesize__sum'], month['filesize__count'], day['filesize__count'])
        serializer = StatisticsSerializer(stat)

        return Response(serializer.data)


class LightSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField()

    class Meta:
        model = LightResponse
        fields = '__all__'


class Light(APIView):
    permission_classes = [permissions.IsAuthenticated]

    """
    Returns a list of events.

    Mandatory GET parameters are:
    type   -- Selects which type of events are returned. Can be either 'light' or 'movement'
    """
    def get(self, request, format=None):
        params = request.query_params
        logger.info(params)

        messaging = Messaging.LocalClientMessaging()
        messaging.send(Message.Message.msg_command('lights', 'on'))
        messaging.stop()

        serializer = LightSerializer(LightResponse(True))

        return Response(serializer.data)
