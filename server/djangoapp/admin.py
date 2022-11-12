from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel



#TODO: Please use root as user name and root as password for your reviewer to login your app.


# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 6

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name',  'dealer_id', 'c_type', 'year']
    search_fields = ['name']


# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']
    search_fields = ['name']

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel)