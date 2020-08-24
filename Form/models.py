from django.db import models
from django.core.files import File
from PIL import Image
from io import BytesIO
import base64
from django.utils.text import slugify
from model_utils import Choices



# Docker Image Model
class DockerImage(models.Model):
    image_name = models.CharField(max_length=200)
    os_type = models.CharField(max_length=200)
    description = models.TextField(max_length=500, default='Description')
    deploy_script = models.FileField(upload_to = 'bash_scripts/')
    remove_script = models.FileField(upload_to = 'bash_scripts/')


    def __str__(self):
        return self.image_name


# Pentesting device Model
class Device(models.Model):
    device_choices = Choices('RPA', 'Qualys', 'VRPA', 'Laptop') 
    device_type = models.CharField(choices=device_choices, max_length=200)
    device_name = models.CharField(max_length=200, null=True, blank=True)
    serial_number = models.CharField(max_length=200)
    online = models.BooleanField(default=False)
    idle = models.BooleanField(default=True)
    docker_images = models.ManyToManyField(DockerImage, blank=True)
    image_hostname = models.CharField(max_length=200, default='0.0.0.0')
    call_home_port = models.IntegerField(blank=True, null=True, default = 00000)
    management_port = models.IntegerField(blank=True, null=True, default = 00000)
    assigned_to_user = models.CharField(max_length=200, default='Idle')
    assigned_to_client = models.CharField(max_length=200, default='Idle')
    deployed = models.BooleanField(default=False)
    weight = models.IntegerField(default=10)
    length = models.IntegerField(default=13)
    width = models.IntegerField(default=10)
    height = models.IntegerField(default=5)
    value = models.IntegerField(default=1000)
    inventory_description = models.TextField(max_length=500, default='Inventory & Description')
    associated_order_id = models.IntegerField(blank=True, null=True)
    tracking_number_out = models.CharField(max_length=200, default = 'N/A')
    tracking_number_in = models.CharField(max_length=200, default = 'N/A')
    slug = models.SlugField(blank=True, null=True)

    # How to order devices when all are listed such as on the 'Monitor Devices' home page
    class Meta:
        ordering = ['-online', '-deployed']

    # String representation of a device when called
    def __str__(self):
        return self.serial_number

    # Customized save method to create a slug(identifier) for each device
    def save(self, *args, **kwargs):
        self.slug = slugify(self.serial_number)
        self.device_name = self.device_type + '-' + str(self.management_port)[-3:]
        super().save(*args, **kwargs)

    # Create url endpoint for each device
    def get_absolute_url(self):
        return f'/monitor/device/{self.slug}'




# Adress Model
class AddressBook(models.Model):
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    def __str__(self):
        return self.company_name




# Shipment Model
class Order(models.Model):
    # Device Info 
    User_Name = models.CharField(max_length=200)
    Device_Serial = models.CharField(max_length=200)
    #Device = models.OneToOneField(Device, on_delete=models.DO_NOTHING, null=True)
    

    # To Feilds
    to_name = models.CharField(max_length=200)
    to_company_name = models.CharField(max_length=200)
    to_email = models.CharField(max_length=200)
    to_street = models.CharField(max_length=200)
    to_city = models.CharField(max_length=200)
    to_state = models.CharField(max_length=200)
    to_postal_code = models.CharField(max_length=200)
    to_phone_number = models.CharField(max_length=200)
    
    # From Feilds
    from_name = models.CharField(max_length=200)
    from_company_name = models.CharField(max_length=200)
    from_email = models.CharField(max_length=200)
    from_street = models.CharField(max_length=200)
    from_city = models.CharField(max_length=200)
    from_state = models.CharField(max_length=200)
    from_postal_code = models.CharField(max_length=200)
    from_phone_number = models.CharField(max_length=200)

    # Shipping label info
    tracking_number_out = models.CharField(max_length=200, default='N/A')
    tracking_number_in = models.CharField(max_length=200, default='N/A')
    label_image_out = models.ImageField(null=True, blank=True, upload_to='outbound_labels/')
    label_image_in = models.ImageField(null=True, blank=True, upload_to='inbound_labels/')

    # Custom save method to write raw image data into image file saved in outbound labels
    def save(self, Img_Data, *args, **kwargs):
        Label = Image.open(BytesIO(base64.b64decode(Img_Data)))
        blob = BytesIO()
        Label.save(blob, 'PNG')
        self.label_image_out.save(f'{self.to_company_name.capitalize()}_label.png', File(blob), save=False)
        super(Order, self).save(*args, **kwargs)

    # Custom save method to write raw image data into image file saved in inbound labels
    def save2(self, Img_Data, *args, **kwargs):
        Label = Image.open(BytesIO(base64.b64decode(Img_Data)))
        blob = BytesIO()
        Label.save(blob, 'PNG')
        self.label_image_in.save(f'{self.to_company_name.capitalize()}_label.png', File(blob), save=False)
        super(Order, self).save(*args, **kwargs)

    # Name of shipments in djangos admin pannel
    def __str__(self):
        return str(str(f'({self.id}) - ') + self.to_company_name.capitalize())
