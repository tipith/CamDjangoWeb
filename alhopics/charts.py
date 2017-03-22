import random
import django
import datetime
import logging

from django.utils import timezone

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

from .models import Rpitemperature


logger = logging.getLogger(__name__)


def rpi_temp(request):
    days_ago = timezone.now() - datetime.timedelta(days=3)
    temps = Rpitemperature.objects.filter(idcamera=1, timestamp__gte=days_ago).order_by('timestamp')
    temps_cam1 = temps.values_list('timestamp', 'temperature')
    temps = Rpitemperature.objects.filter(idcamera=2, timestamp__gte=days_ago).order_by('timestamp')
    temps_cam2 = temps.values_list('timestamp', 'temperature')

    fig = Figure()
    ax = fig.add_subplot(111)

    x1 = [point[0] for point in temps_cam1]
    y1 = [float(point[1]) for point in temps_cam1]
    ax.plot_date(x1, y1, '-')

    x2 = [point[0] for point in temps_cam2]
    y2 = [float(point[1]) for point in temps_cam2]
    ax.plot_date(x2, y2, '-')

    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
