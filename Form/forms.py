from django import forms
from .models import Device, DockerImage, AddressBook
from django.contrib.auth.models import User


users = [(user.username, user.username) for user in User.objects.all()]
user_choices = tuple(users)
class DeviceUpdateForm(forms.Form):
    Images = forms.ModelChoiceField(DockerImage.objects.all(), required=False)
    Management_Port = forms.IntegerField(required=False) 
    Call_Home_Port = forms.IntegerField(required=False)
    Assigned_To_User = forms.ChoiceField(initial = {'Users': 'Users'}, choices = user_choices, required=False)
    def __init__(self, *args, **kwargs):
        super(DeviceUpdateForm, self).__init__(*args, **kwargs)
        self.fields['Assigned_To_User'].empty_label = 'Users'


class ImageDeployForm(forms.Form):
    Images = forms.ModelMultipleChoiceField(DockerImage.objects.all(), widget = forms.CheckboxSelectMultiple(), required = True)
    def __init__(self, *args, **kwargs):
        super(ImageDeployForm, self).__init__(*args, **kwargs)
        self.fields['Images'].label = ''


class ToAddressBookForm(forms.Form):
    To_Addresses = forms.ModelChoiceField(AddressBook.objects.all(), required = False)
    def __init__(self, *args, **kwargs):
        super(ToAddressBookForm, self).__init__(*args, **kwargs)
        self.fields['To_Addresses'].label = 'Address Book '

class FromAddressBookForm(forms.Form):
    From_Addresses = forms.ModelChoiceField(AddressBook.objects.all(), required = False)
    def __init__(self, *args, **kwargs):
        super(FromAddressBookForm, self).__init__(*args, **kwargs)
        self.fields['From_Addresses'].label = 'Address Book '

# Form to select device
class DeviceForm(forms.Form):
    Device = forms.ModelChoiceField(Device.objects.filter(deployed=False), widget = forms.Select(), required = True)
    def __init__(self, *args, **kwargs):
        super(DeviceForm, self).__init__(*args, **kwargs)
        self.fields['Device'].label = ''

# Form for shipping recipient
class ShippingFormTo(forms.Form):
    To_Name = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Name'}), required = False)
    To_Company_Name = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Company Name'}), required = False)
    To_Email = forms.EmailField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Email'}), required = False)
    To_Street = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Street'}), required = False)
    To_City = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'City'}), required = False)
    To_State = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'AL, FL, CA, ect'}), required = False)
    To_Postal_Code = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Postal Code'}), required = False)
    To_Phone_Number = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Phone Number'}), required = False)
    def __init__(self, *args, **kwargs):
        super(ShippingFormTo, self).__init__(*args, **kwargs)
        self.fields['To_Name'].label = ''
        self.fields['To_Company_Name'].label = ''
        self.fields['To_Email'].label = ''
        self.fields['To_Street'].label = ''
        self.fields['To_City'].label = ''
        self.fields['To_State'].label = ''
        self.fields['To_Postal_Code'].label = ''
        self.fields['To_Phone_Number'].label = ''

# Form for shipping sender 
class ShippingFormFrom(forms.Form):
    From_Name = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Name'}), required = False)
    From_Company_Name = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Company Name'}), required = False)
    From_Email = forms.EmailField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Email'}), required = False)
    From_Street = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Street'}), required = False)
    From_City = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'City'}), required = False)
    From_State = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'AL, FL, CA, ect'}), required = False)
    From_Postal_Code = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Postal Code'}), required = False)
    From_Phone_Number = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Phone Number'}), required = False)
    def __init__(self, *args, **kwargs):
        super(ShippingFormFrom, self).__init__(*args, **kwargs)
        self.fields['From_Name'].label = ''
        self.fields['From_Company_Name'].label = ''
        self.fields['From_Email'].label = ''
        self.fields['From_Street'].label = ''
        self.fields['From_City'].label = ''
        self.fields['From_State'].label = ''
        self.fields['From_Postal_Code'].label = ''
        self.fields['From_Phone_Number'].label = ''

# Login Form
class LoginForm(forms.Form):
    Username = forms.CharField(widget  = forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Username'}), required = True)
    Password = forms.CharField(widget  = forms.PasswordInput(attrs={'class': 'input100', 'placeholder': 'Password'}), required = True)