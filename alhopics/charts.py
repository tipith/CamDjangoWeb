import io
import datetime
import logging

from django.http import HttpResponse, HttpResponseNotFound
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter


from .models import Rpitemperature, Picture, Uplink


logger = logging.getLogger(__name__)
cams = {1: 'Piha', 2: 'Autotalli'}


def get_ax_and_response(titles, fmt=DateFormatter('%d.%m')):
    fig = Figure(tight_layout=True)
    titles = titles if isinstance(titles, list) else [titles]

    for ind, title in enumerate(titles):
        # nrows, ncols, index
        ax = fig.add_subplot(1, len(titles), ind + 1)
        yield ax
        ax.set_title(title)
        ax.grid()
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        if fmt:
            ax.xaxis.set_major_formatter(fmt)

    fig.autofmt_xdate()
    canvas = FigureCanvasAgg(fig)
    buf = io.BytesIO()
    canvas.print_png(buf)
    yield HttpResponse(buf.getvalue(), content_type='image/png')


def rpi_temp(request):
    days_ago = timezone.now() - datetime.timedelta(days=7)
    gen = get_ax_and_response(['Prosessorilämpötila (viikko)', 'Prosessorilämpötila (vuosi)'])
    ax = next(gen)

    for cam_id, cam_name in cams.items():
        temps = Rpitemperature.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .order_by('timestamp')
        temps = temps.values_list('timestamp', 'temperature')
        x = [point[0] for point in temps]
        y = [float(point[1]) for point in temps]
        ax.plot_date(x, y, '-', label=cam_name)

    days_ago = timezone.now() - datetime.timedelta(days=360)

    ax = next(gen)

    for cam_id, cam_name in cams.items():
        temps = Rpitemperature.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .extra({'date': "date(timestamp)"}) \
            .values('date') \
            .annotate(temp=Avg('temperature')) \
            .order_by('date')
        temps = temps.values_list('date', 'temp')
        x = [point[0] for point in temps]
        y = [float(point[1]) for point in temps]
        ax.plot_date(x, y, '-', label=cam_name)

    return next(gen)


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


def megabytes_per_day(request):
    days_ago = timezone.now() - datetime.timedelta(days=360)
    gen = get_ax_and_response(['Mt / vrk', 'Mt / kk'], fmt=None)
    ax = next(gen)

    for cam_id, cam_name in cams.items():
        counts = Picture.objects.filter(idcamera=cam_id, timestamp__gte=days_ago) \
            .extra({'date': "date(timestamp)"}) \
            .values('date') \
            .annotate(bytes=Sum('filesize'))
        x = [c['date'] for c in counts]
        y = [c['bytes'] // 1024**2 for c in counts]
        ax.plot_date(x, y, '-', label=cam_name)
    ax.set_ylim(bottom=0)

    ax = next(gen)

    counts = Picture.objects.filter(timestamp__gte=days_ago) \
        .extra({'month': "month(timestamp)"}) \
        .values('month') \
        .annotate(bytes=Sum('filesize')) \
        .order_by('month')
    x = [int(c['month']) for c in counts]
    y = [c['bytes'] // 1024**2 for c in counts]
    ax.bar(x, y)
    ax.set_ylim(bottom=0)

    return next(gen)


def uplink(request):
    gen = get_ax_and_response('Modeemisignaali')
    ax = next(gen)

    days_ago = timezone.now() - datetime.timedelta(days=7)

    vals = Uplink.objects.filter(timestamp__gte=days_ago).order_by('timestamp')
    print(vals)
    x = [v.timestamp for v in vals]
    y1 = [v.signalstrength for v in vals]
    y2 = [v.signalqualitypercent for v in vals]
    ax.plot_date(x, y1, '-', label='Voimakkuus')
    ax.plot_date(x, y2, '-', label='Laatu')

    ax.set_ylim(bottom=0)
    return next(gen)


@login_required
def plot(request, filename=None, extension=None):
    plot_mapping = {
        'rpi_temp': rpi_temp,
        'pics_per_day': pics_per_day,
        'megabytes_per_day': megabytes_per_day,
        'uplink': uplink
    }
    if filename in plot_mapping and extension == 'png':
        return plot_mapping[filename](request)
    else:
        return HttpResponseNotFound()
