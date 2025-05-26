from django.db import models
from django.utils import timezone
from django.contrib.gis.db import models as geomodels


# Create your models here.

class MyUser(models.Model):                                       
    name=models.CharField(max_length=30)
    Mob=models.BigIntegerField(primary_key=True,unique=True)
    Email=models.EmailField()
    password = models.CharField(max_length=50, blank=True, null=True)
    address=models.CharField(max_length=100, blank=True, null=True)
    
    
    def __str__(self):
        return str(self.name)

class Pond(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    latlong = models.CharField(max_length=150)
    # location = models.GeometryField(unique=True,null=True,blank=True)
    location = geomodels.GeometryField(unique=True, null=True, blank=True)
    area = models.CharField(max_length=150, blank=True,null=True)
    address = models.CharField(max_length=150)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)


class Parameter(models.Model):
    pH = models.FloatField()
    dissolved_oxygen = models.FloatField()
    NDVI = models.FloatField()
    NDTI = models.FloatField()
    GCI = models.FloatField()                           
    NDCI = models.FloatField()
    NDWI = models.FloatField()
    TSS = models.FloatField()
    CDOM = models.FloatField()
    AQUATIC_MACROPYTES = models.FloatField()
    Phycocyanin = models.FloatField()
    Chl_a = models.FloatField(null=True, blank=True)  
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.pond)