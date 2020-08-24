from Form.models import Order, Device
import requests
import datetime
import sys
from bs4 import BeautifulSoup
import os
import xml.dom.minidom

'''
These functions fill out the fedex.xml document needed for the FedEx webserice api. 
The functions then save any relevent information associated with the deoployment order.
Beautiful soup is used to manage the parsing, the api post is send using the requests library.
'''

# Outbound deoployment order and shipping label creation
def parse_and_fill_outbound( To_Name, To_Company_Name, To_Email, To_Street, To_City,
                    To_State, To_Postal_Code, To_Phone_Number,
                    From_Name, From_Company_Name, From_Email, From_Street,
                    From_City, From_State, From_Postal_Code, 
                    From_Phone_Number, User, Dev_Serial):

    # Define selected device
    device = Device.objects.get(serial_number = Dev_Serial)

    # Open fedex.xml file and parse out the raw text into a BS4 Soup object
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'fedex.xml')
    with open(file_path, 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'xml')

    # Create timestamp for fedex API and update in xml
    now = datetime.datetime.now()
    current_timestamp = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'+04:00')
    soup.ShipTimestamp.string = current_timestamp

    # Update xml with FROM values in django form
    #Contact
    soup.Shipper.Contact.PersonName.string = From_Name
    soup.Shipper.Contact.CompanyName.string = From_Company_Name
    soup.Shipper.Contact.PhoneNumber.string = From_Phone_Number
    # Adress
    soup.Shipper.Address.StreetLines.string = From_Street
    soup.Shipper.Address.City.string = From_City
    soup.Shipper.Address.StateOrProvinceCode.string = From_State
    soup.Shipper.Address.PostalCode.string = From_Postal_Code


    # Update xml with TO values in django form
    #Contact
    soup.Recipient.Contact.PersonName.string = To_Name
    soup.Recipient.Contact.CompanyName.string = To_Company_Name
    soup.Recipient.Contact.PhoneNumber.stirng = To_Phone_Number
    soup.Recipient.Contact.EMailAddress.string = To_Email
    # Adress
    soup.Recipient.Address.StreetLines.string = To_Street
    soup.Recipient.Address.City.string = To_City
    soup.Recipient.Address.StateOrProvinceCode.string = To_State
    soup.Recipient.Address.PostalCode.string = To_Postal_Code

    # Update xml device info
    soup.RequestedPackageLineItems.Weight.Value.string = str(device.weight)
    soup.RequestedPackageLineItems.Dimensions.Length.string = str(device.length)
    soup.RequestedPackageLineItems.Dimensions.Width.string = str(device.width)
    soup.RequestedPackageLineItems.Dimensions.Height.string = str(device.height)

    print(soup)
    # Send post request to Fedex API
    r = requests.post('https://wsbeta.fedex.com:443/web-services', data = str(soup))

    # Fedex response
    response = BeautifulSoup(r.content, 'xml')
    print(response)

    # Parse the response from fedex to extract the tracking number
    Tracking_Number = response.TrackingNumber.string

    # Parse the response from fedex to extract the label
    Img_Data = response.Image.string

    # Save instace of the Order class
    order = Order(
        User_Name = User, 
        Device_Serial = Dev_Serial,
        to_name = To_Name,
        to_company_name = To_Company_Name,
        to_email = To_Email,
        to_street = To_Street,
        to_city = To_City,
        to_state = To_State,
        to_postal_code = To_Postal_Code,
        to_phone_number = To_Phone_Number,
        from_name = From_Name,
        from_company_name = From_Company_Name,
        from_email = From_Email,
        from_street = From_Street,
        from_city = From_City,
        from_state = From_State,
        from_postal_code = From_Postal_Code,
        from_phone_number = From_Phone_Number,
        tracking_number_out = Tracking_Number,
        label_image_out = Img_Data,

    )
    order.save(Img_Data)

    # Update the device info associated with the order
    device.deployed = True
    device.assigned_to_user = User
    device.assigned_to_client = To_Company_Name
    device.tracking_number_out = Tracking_Number
    device.associated_order_id = order.id
    device.save()



# Inbound deoployment order shipping label creation
def parse_and_fill_inbound(return_device):

    # Define the order associated with the device
    order = Order.objects.get(id = return_device.associated_order_id, tracking_number_in = 'N/A')
    print(order)
    print(return_device)

    # Open fedex.xml file and parse out the raw text into a BS4 Soup object
    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, 'fedex.xml')
    with open(file_path, 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'xml')

    # Create timestamp for fedex API and update in xml
    now = datetime.datetime.now()
    current_timestamp = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'+04:00')
    soup.ShipTimestamp.string = current_timestamp

        # Update xml with FROM values in django form
    #Contact
    soup.Shipper.Contact.PersonName.string = order.to_name
    soup.Shipper.Contact.CompanyName.string = order.to_company_name
    soup.Shipper.Contact.PhoneNumber.string = order.to_phone_number
    # Adress
    soup.Shipper.Address.StreetLines.string = order.to_street
    soup.Shipper.Address.City.string = order.to_city
    soup.Shipper.Address.StateOrProvinceCode.string = order.to_state
    soup.Shipper.Address.PostalCode.string = order.to_postal_code


    # Update xml with TO values in django form
    #Contact
    soup.Recipient.Contact.PersonName.string = order.from_name
    soup.Recipient.Contact.CompanyName.string = order.from_company_name
    soup.Recipient.Contact.PhoneNumber.stirng = order.from_phone_number
    soup.Recipient.Contact.EMailAddress.string = order.from_email
    # Adress
    soup.Recipient.Address.StreetLines.string = order.from_street
    soup.Recipient.Address.City.string = order.from_city
    soup.Recipient.Address.StateOrProvinceCode.string = order.from_state
    soup.Recipient.Address.PostalCode.string = order.from_postal_code

    # Update xml device info
    soup.RequestedPackageLineItems.Weight.Value.string = str(return_device.weight)
    soup.RequestedPackageLineItems.Dimensions.Length.string = str(return_device.length)
    soup.RequestedPackageLineItems.Dimensions.Width.string = str(return_device.width)
    soup.RequestedPackageLineItems.Dimensions.Height.string = str(return_device.height)

    print(soup)
    # Send post request to Fedex API
    r = requests.post('https://wsbeta.fedex.com:443/web-services', data = str(soup))

    # Fedex response
    response = BeautifulSoup(r.content, 'xml')
    print(response)

    # Parse the response from fedex to extract the tracking number
    Tracking_Number = response.TrackingNumber.string

    # Parse the response from fedex to extract the label
    Img_Data = response.Image.string


    # Update the inbound tracking info for the order and mark the associated device and no longer deployed 
    order.tracking_number_in = Tracking_Number
    return_device.tracking_number_in = Tracking_Number
    return_device.deployed = False
    order.save2(Img_Data)
    return_device.save()
