from django.contrib import admin
from .models import Order, Device, DockerImage, AddressBook

# How things are displayed in the admin panel
class DeviceInfo(admin.ModelAdmin):
    list_display = ('serial_number','deployed', 'online')


admin.site.register(Order)
admin.site.register(Device, DeviceInfo)
admin.site.register(DockerImage)
admin.site.register(AddressBook)