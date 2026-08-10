from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'Mob', 'Email', 'address','password')
    search_fields = ('name', 'Mob', 'Email')
    list_filter = ('Email',)


@admin.register(Pond)
class PondAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latlong','location', 'area', 'address')
    search_fields = ('name', 'latlong', 'address')
    list_filter = ('area',)
    ordering = ('id',)

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = (
        'pond', 'image_id','image_date','satellite_name','pH', 'dissolved_oxygen', 'NDVI', 'NDTI',
        'GCI', 'NDCI', 'NDWI', 'TSS', 'CDOM',
        'AQUATIC_MACROPYTES', 'Phycocyanin', 'Chl_a', 'created_at'
    )
    search_fields = ('pond__name',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)