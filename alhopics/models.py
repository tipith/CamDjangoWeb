# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class CommandResponse(models.Model):
    def __init__(self, status):
        self.status = status


class StatisticsResponse(models.Model):
    def __init__(self, data_month=0, data_day=0, pics_month=0, pics_day=0):
        self.data_month = data_month / 1024 / 1024 if data_month else 0
        self.data_day = data_day / 1024 / 1024 if data_day else 0
        self.pics_month = pics_month if pics_month else 0
        self.pics_day = pics_day if pics_day else 0


class Camera(models.Model):
    idcamera = models.AutoField(db_column='idCamera', primary_key=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Camera'
        app_label = 'pictures'


class Lightcontrol(models.Model):
    idlightcontrol = models.AutoField(db_column='idLightControl', primary_key=True)  # Field name made lowercase.
    idcamera = models.ForeignKey(Camera, models.DO_NOTHING, db_column='idCamera', blank=True, null=True)  # Field name made lowercase.
    starttimestamp = models.DateTimeField(db_column='StartTimestamp', blank=True, null=True)  # Field name made lowercase.
    endtimestamp = models.DateTimeField(db_column='EndTimestamp', blank=True, null=True)  # Field name made lowercase.
    uuid = models.CharField(db_column='UUID', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'LightControl'
        app_label = 'pictures'


class Movement(models.Model):
    idmovement = models.AutoField(db_column='idMovement', primary_key=True)  # Field name made lowercase.
    idcamera = models.ForeignKey(Camera, models.DO_NOTHING, db_column='idCamera', blank=True, null=True)  # Field name made lowercase.
    starttimestamp = models.DateTimeField(db_column='StartTimestamp', blank=True, null=True)  # Field name made lowercase.
    endtimestamp = models.DateTimeField(db_column='EndTimestamp', blank=True, null=True)  # Field name made lowercase.
    detector = models.CharField(db_column='Detector', max_length=45, blank=True, null=True)  # Field name made lowercase.
    uuid = models.CharField(db_column='UUID', max_length=128, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Movement'
        app_label = 'pictures'


class Picture(models.Model):
    idpicture = models.AutoField(db_column='idPicture', primary_key=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    idcamera = models.ForeignKey(Camera, models.DO_NOTHING, db_column='idCamera', blank=True, null=True)  # Field name made lowercase.
    filelocation = models.CharField(db_column='FileLocation', max_length=128, blank=True, null=True)  # Field name made lowercase.
    filesize = models.IntegerField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    uploadtime = models.CharField(db_column='UploadTime', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Picture'
        app_label = 'pictures'


class Picturemovement(models.Model):
    idpicturemovement = models.AutoField(db_column='idPictureMovement', primary_key=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    idcamera = models.ForeignKey(Camera, models.DO_NOTHING, db_column='idCamera', blank=True, null=True)  # Field name made lowercase.
    filelocation = models.CharField(db_column='FileLocation', max_length=128, blank=True, null=True)  # Field name made lowercase.
    filesize = models.IntegerField(db_column='FileSize', blank=True, null=True)  # Field name made lowercase.
    uuid = models.CharField(db_column='UUID', max_length=128, blank=True, null=True)  # Field name made lowercase.
    uploadtime = models.CharField(db_column='UploadTime', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PictureMovement'
        app_label = 'pictures'


class Rpitemperature(models.Model):
    idrpitemperature = models.AutoField(db_column='idRpiTemperature', primary_key=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    idcamera = models.ForeignKey(Camera, models.DO_NOTHING, db_column='idCamera', blank=True, null=True)  # Field name made lowercase.
    temperature = models.DecimalField(db_column='Temperature', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RpiTemperature'
        app_label = 'pictures'


class Uplink(models.Model):
    iduplink = models.AutoField(db_column='idUplink', primary_key=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    uptimeseconds = models.IntegerField(db_column='UptimeSeconds', blank=True, null=True)  # Field name made lowercase.
    radioaccesstechnology = models.CharField(db_column='RadioAccessTechnology', max_length=45, blank=True, null=True)  # Field name made lowercase.
    ipaddress = models.CharField(db_column='IPAddress', max_length=45, blank=True, null=True)  # Field name made lowercase.
    networkname = models.CharField(db_column='NetworkName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    signalstrength = models.IntegerField(db_column='SignalStrength', blank=True, null=True)  # Field name made lowercase.
    signalqualitypercent = models.IntegerField(db_column='SignalQualityPercent', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Uplink'
        app_label = 'pictures'
