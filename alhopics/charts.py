import io
import datetime
import logging

from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter


from .models import Rpitemperature, Picture


logger = logging.getLogger(__name__)
cams = {1: 'Piha', 2: 'Autotalli'}


def get_ax_and_response(title):
    fig = Figure()
    ax = fig.add_subplot(111)
    yield ax

    ax.set_title(title)
    ax.grid()
    ax.legend()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.xaxis.set_major_formatter(DateFormatter('%d.%m'))
    fig.autofmt_xdate()
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    yield HttpResponse(buf.getvalue(), content_type='image/png')


@login_required
def rpi_temp(request):
    gen = get_ax_and_response('Prosessorilämpötila')
    ax = next(gen)

    days_ago = timezone.now() - datetime.timedelta(days=360)

    for cam_id, cam_name in cams.items():
        temps = Rpitemperature.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .order_by('timestamp')
        temps = temps.values_list('timestamp', 'temperature')
        x = [point[0] for point in temps]
        y = [float(point[1]) for point in temps]
        ax.plot_date(x, y, '-', label=cam_name)

    return next(gen)


@login_required
def pics_per_day(request):
    gen = get_ax_and_response('Kuvia päivässä')
    ax = next(gen)

    days_ago = timezone.now() - datetime.timedelta(days=360)

    for cam_id, cam_name in cams.items():
        counts = Picture.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .extra({'date': "date(timestamp)"}) \
            .values('date') \
            .annotate(pic_count=Count('idpicture'))
        x = [c['date'] for c in counts]
        y = [c['pic_count'] for c in counts]
        ax.plot_date(x, y, '-', label=cam_name)

    ax.set_ylim(bottom=0)
    return next(gen)


@login_required
def megabytes_per_day(request):
    gen = get_ax_and_response('Megatavuja päivässä')
    ax = next(gen)

    days_ago = timezone.now() - datetime.timedelta(days=360)

    for cam_id, cam_name in cams.items():
        counts = Picture.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .extra({'date': "date(timestamp)"}) \
            .values('date') \
            .annotate(bytes=Sum('filesize'))
        x = [c['date'] for c in counts]
        y = [c['bytes'] // 1024**2 for c in counts]
        ax.plot_date(x, y, '-', label=cam_name)

    ax.set_ylim(bottom=0)
    return next(gen)
