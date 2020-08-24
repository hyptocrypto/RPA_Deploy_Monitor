from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ShippingFormTo, ShippingFormFrom, DeviceForm, LoginForm, DeviceUpdateForm, ImageDeployForm, ToAddressBookForm, FromAddressBookForm
from .models import Device, Order
from .scripts.xml_parser import parse_and_fill_outbound, parse_and_fill_inbound
from .scripts.checkport import check_port
import sys 
import subprocess
import os


# Login view
def login_page(request):
    # If user already logged in, redirect to homepage
    if request.user.is_authenticated:
        return redirect('home')
    # If user not logged in, redirect to login page
    else:
        form = LoginForm()
        if request.method == 'POST':
            username = request.POST.get('Username')
            password = request.POST.get('Password')
            user = authenticate(request, username=username, password=password)

            # If credentilas passed in login form match a valid user, log user in and redirect to home page
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect!')

        # Pass login form to html template 
        context = {'form':form}
        return render(request, 'accounts/login.html', context)

# Logout View
def logout_user(request):
    logout(request)
    return redirect('login')



# Home View Listing all devices
class HomeView(ListView):
    model = Device
    template_name = 'home2.html'

    def get(self, *args, **kwargs):
        # For each device, check if online
        querryset = Device.objects.all()
        for device in querryset:
            try:
                if check_port(int(device.call_home_port)) == True:
                    device.online = True
                    device.save()
                else:
                    device.online = False
                    device.save()
            except:
                pass
        return super().get(*args, **kwargs)
       
# Detailed View of each device
class MonitorView(FormMixin, DetailView):
    model = Device
    template_name = 'device2.html'
    form_class = DeviceUpdateForm
    

    # Context info to pass to the html template
    def get_context_data(self, **kwargs):
        context = super(MonitorView, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['device_update_form'] = DeviceUpdateForm()
        return context
        
    # Actions if the HTTP method is POST
    def post(self, request, *args, **kwargs):
        device = self.get_object()
        form = self.get_form()
        # If the HTTP method is POST and contains 'update_management_home_' (when update managemnt port button is clicked), update managemnt port
        if 'update_management_port' in request.POST:
            if form.is_valid():
                management_port = form.cleaned_data['Management_Port']
                device.management_port = management_port
                device.save()

        # If the HTTP method is POST and contains 'update_call_home_' (when update call home portbutton is clicked), update call home port
        if 'update_call_home_port' in request.POST:
            if form.is_valid():
                call_home_port = form.cleaned_data['Call_Home_Port']
                device.call_home_port = call_home_port
                device.save()

        # If the HTTP method is POST and contains 'assigned_to_user' (when set to idle button is clicked), updated the assinged to user
        if 'update_assigned_to_user' in request.POST:
            if form.is_valid():
                assigned_to_user = form.cleaned_data['Assigned_To_User']
                device.assigned_to_user = assigned_to_user
                device.save()

        # If the HTTP method is POST and contains 'ship_home' (when ship home button is clicked), try the parse_and_fill_in function.
        if 'ship_home' in request.POST:
            try:
                parse_and_fill_inbound(device)
                return redirect('home')
            except Exception as message:
                return render(request, 'error.html', {'message': message})

        # If the HTTP method is POST and contains 'set_to_idle' (when set to idle button is clicked), reset the device atributes to idle settings
        if 'reset_to_idle' in request.POST:
            try:
                device.idle = True
                device.deployed = False
                device.assigned_to_user = 'Idle'
                device.assigned_to_client = 'Idle'
                device.tracking_number_out = 'N/A'
                device.tracking_number_in = 'N/A'
                device.save()
            except Exception as message:
                return render(request, 'error.html', {'message': message})

        # If the HTTP method is POST and contains 'docker_destroy' (when destory docker button is clicked), send the docker-destory.sh script to the device      
        if 'docker_destroy' in request.POST:
            try:
                # Find local bash script and execute it over shh via the device managment port
                module_dir = os.path.dirname(__file__)
                file_path = os.path.join(module_dir, 'scripts/docker-destroy.sh')
                subprocess.Popen(f'sshpass -p "ctek" ssh -p {device.management_port} ctek@127.0.0.1 < {file_path}', shell=True)
                # Remove the relation between device and image
                
                for image in device.docker_images.all():
                    device.docker_images.remove(image)
             
            except Exception as message:
                return render(request, 'error.html', {'message': message})

        # If the HTTP method is POST and contains 'docker_image_deploy' (when deoploy image button is clicked), send the docker_setup.sh script to the device      
        if 'docker_image_deploy' in request.POST:
            if form.is_valid():
                try:
                    image = form.cleaned_data['Images']
                    device.docker_images.add(image)
                    device.save()
                    subprocess.Popen(f'sshpass -p "ctek" ssh -p {device.management_port} ctek@127.0.0.1 < {image.deploy_script.path}', shell=True)
                    

                except Exception as message:
                    return render(request, 'error.html', {'message': message})
        # For all the images installed on device, if the remove_docker_image button for that image is selected, remove the image form the device.
        for image in device.docker_images.all():
            if f'remove_docker_image_{image.image_name}' in request.POST:
                try:
                    print(image.image_name)
                    device.docker_images.remove(image)
                    subprocess.Popen(f'sshpass -p "ctek" ssh -p {device.management_port} ctek@127.0.0.1 < {image.remove_script.path}', shell=True)
                  
                except Exception as message:
                    return render(request, 'error.html', {'message': message})



        return redirect(f'/monitor/device/{device.slug}/')




# View for successful deployment 
def success(request):
    return render(request, 'success.html')

# Depoly & order form view
@login_required(login_url='login')
def deploy_form(request):
    # If HTTP method is GET, then display the form.
    print(request.user)
    if request.method == 'GET':
        to_form = ShippingFormTo()
        from_form = ShippingFormFrom()
        device_form = DeviceForm()
        image_form = ImageDeployForm()
        to_addressbook_form = ToAddressBookForm()
        from_addressbook_form = FromAddressBookForm()

    # If HTTP method is not GET, display and process form
    elif request.method == 'POST':
        to_form = ShippingFormTo(request.POST)
        from_form = ShippingFormFrom(request.POST)
        device_form = DeviceForm(request.POST) 
        image_form = ImageDeployForm(request.POST)
        to_addressbook_form = ToAddressBookForm(request.POST)
        from_addressbook_form = FromAddressBookForm(request.POST)
        
        if image_form.is_valid():
            images = image_form.cleaned_data['Images']

        # Check if all form feilds are filled correctly ie(valid)
        if device_form.is_valid():
            Device = device_form.cleaned_data['Device'] 
           
        if to_addressbook_form.is_valid():
            to_address = to_addressbook_form.cleaned_data['To_Addresses']
            if to_address != None:
                To_Name = to_address.name
                To_Company_Name = to_address.company_name
                To_Email = to_address.email
                To_Street = to_address.street
                To_City = to_address.city
                To_State = to_address.state
                To_Postal_Code = to_address.postal_code
                To_Phone_Number = to_address.phone_number   

            elif to_address == None:
                if to_form.is_valid():           
                    # If valid clean and process data
                    To_Name = to_form.cleaned_data['To_Name']
                    To_Company_Name = to_form.cleaned_data['To_Company_Name']
                    To_Email = to_form.cleaned_data['To_Email']
                    To_Street = to_form.cleaned_data['To_Street']
                    To_City = to_form.cleaned_data['To_City']
                    To_State = to_form.cleaned_data['To_State']
                    To_Postal_Code = to_form.cleaned_data['To_Postal_Code']
                    To_Phone_Number = to_form.cleaned_data['To_Phone_Number']

            print(To_Name)


        if from_addressbook_form.is_valid():
            from_address = from_addressbook_form.cleaned_data['From_Addresses']
            if from_address != None:
                From_Name = from_address.name
                From_Company_Name = from_address.company_name
                From_Email = from_address.email
                From_Street = from_address.street
                From_City = from_address.city
                From_State = from_address.state
                From_Postal_Code = from_address.postal_code
                From_Phone_Number = from_address.phone_number 

            elif from_address == None:
                if from_form.is_valid():
            
                    # If valid, clean and process data
                    From_Name = from_form.cleaned_data['From_Name']
                    From_Company_Name = from_form.cleaned_data['From_Company_Name']
                    From_Email = from_form.cleaned_data['From_Email']
                    From_Street = from_form.cleaned_data['From_Street']
                    From_City = from_form.cleaned_data['From_City']
                    From_State = from_form.cleaned_data['From_State']
                    From_Postal_Code = from_form.cleaned_data['From_Postal_Code']
                    From_Phone_Number = from_form.cleaned_data['From_Phone_Number']
            print(From_Name)


            # # Try sending xml to fedex webservice API
            try:
                parse_and_fill_outbound(
                    To_Name, To_Company_Name, To_Email, To_Street, To_City,
                    To_State, To_Postal_Code, To_Phone_Number,
                    From_Name, From_Company_Name, From_Email, From_Street,
                    From_City, From_State, From_Postal_Code, 
                    From_Phone_Number, request.user.get_username(), Device
                )
                # Add image realtionship with device and run the deploy scripts on the device for each image selected
                for image in images:
                    Device.docker_images.add(image) 
                    subprocess.Popen(f'sshpass -p "ctek" ssh -p {Device.management_port} ctek@127.0.0.1 < {str(image.deploy_script.path)}', shell=True)
                   # module_dir = os.path.dirname(__file__)
                   # file_path = os.path.join(module_dir, 'scripts/rpa-container-setup.sh')
                   # subprocess.Popen(f'sshpass -p "ctek" ssh -tt -p {Device.management_port} ctek@127.0.0.1 < {file_path}', shell=True)
                    return redirect('home')
            # Error feedback
            except Exception as message:
                return render(request, 'error.html', {'message': message})
     
        return redirect('home')

    # Pass form info and render the html template
    return render(request, 'deploy_form2.html', {'to_form': to_form, 'from_form': from_form,
                                                 'device_form': device_form, 'image_form': image_form,
                                                 'from_addressbook_form': from_addressbook_form, 'to_addressbook_form': to_addressbook_form})

