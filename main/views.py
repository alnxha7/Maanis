import re
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core import serializers
from django.db import reset_queries, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Max
from .models import Brand, Vehicle, Vehicle_type, Vehicle_master, Employee_master, Trip_sheet, VoucherConfiguration, Table_companyDetailschild, Table_BillItems, Table_BillMaster, LocationMaster, VendorMaster
from django.db.models import Max

    
from django.contrib.auth import get_user_model
User = get_user_model()


# Create your views here.

# index page
def index(request):
    return render(request, 'index.html')
def co_login_view(request):
    companies = Table_Companydetailsmaster.objects.all()
    fyears = Table_companyDetailschild.objects.values('fycode').distinct()
    # branchs = Branch_master.objects.all()
    if request.method == "POST":
        co_id = request.POST.get('company_id')
        name = request.POST.get('name')

        branch = request.POST.get('branch')
        fycode = request.POST.get('fycode')

        request.session['co_id'] = co_id
        request.session['branch'] = branch
        request.session['fycode'] = fycode
        print("session",request.session.get('co_id'))
        # Process the form data here (e.g., authentication, validation)

        # Redirect to the login page after submission
        return redirect('main:login')  # Redirects to the login p
    # return render(request, 'auth/co_login.html',{'companies': companies,'fyears':fyears,"branchs": branchs })
    return render(request, 'auth/co_login.html', {'companies': companies, 'fyears': fyears, })

def get_branches(request):
    company_id = request.GET.get('company_id')
    print("Company ID received from JS:", company_id)

    branches = Branch_master.objects.filter(co_id=company_id).values('branch_name')
    print("Filtered branches:", list(branches))  # Debugging output

    return JsonResponse(list(branches), safe=False)

import random
import string
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Table_Companydetailsmaster, Branch_master  # adjust as needed

# Function to generate a random string
def generate_captcha():
    length = 6  # Length of CAPTCHA string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def user_login(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        co_id = request.session.get('co_id')
        branch = request.session.get('branch')
        comp = Table_Companydetailsmaster.objects.get(company_id=co_id)
        bran = Branch_master.objects.get(branch_name=branch)

        user_id = request.POST.get('user_id')
        password = request.POST.get('password')
        user_captcha = request.POST.get('captcha_answer')
        correct_captcha = request.session.get('captcha_answer')

        # CAPTCHA check start here
        if not user_captcha or not correct_captcha or user_captcha.lower() != correct_captcha.lower():
            messages.error(request, "Invalid CAPTCHA. Please try again.")
            return redirect('main:login')
        # CAPTCHA end here

        request.session['user'] = user_id
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            if user.company == comp and user.branch == bran:
                login(request, user)
                return redirect('main:index')
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

        return redirect('main:login')

    # GET request: generate CAPTCHA word
    captcha_word = generate_captcha()
    request.session['captcha_answer'] = captcha_word

    return render(request, 'auth/login.html', {'captcha_word': captcha_word})

def driver_register(request):
    companies = Table_Companydetailsmaster.objects.all()
    branchs = Branch_master.objects.all()
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        co_id = request.POST.get('company_id')
        branch = request.POST.get('branch')
        if password != password2:
            messages.error(request, "password do not match")
            return redirect("main:driver_register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "User alreadt exists")
            return redirect("main:driver_register")
        try:
            company = Table_Companydetailsmaster.objects.get(id=co_id)
        except Table_Companydetailsmaster.DoesNotExist:
            messages.error(request, "Selected company does not exist")
            return redirect("main:driver_register")

        try:
            branch = Branch_master.objects.get(id=branch)
        except Branch_master.DoesNotExist:
            messages.error(request, "Selected company does not exist")
            return redirect("main:driver_register")

        user = User.objects.create_user(username=username, email=email, password=password,company=company, branch=branch)
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("main:driver_register")
    return render(request, "auth/driver_register.html",{'companies': companies,'branchs':branchs})


def driver_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("main:index")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("main:driver_login")
    return render(request, "auth/driver_login.html")


def driver_logout(request):
    logout(request)
    request.session.flush()
    # messages.success(request, "You have been logged out")
    return redirect("main:index")


# search Brand & List Brands
def brand_list(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    query = request.GET.get('q')
    if query:
        brands = Brand.objects.filter(brand_name__icontains=query,co_id=co_id,branch_id=branch)
    else:
        # brands = Brand.objects.all()
        brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'brands/brand_list.html', {'brands': brands, 'query': query})


# Create a Brand
def brand_create(request):
    error_message = None
    co_id = request.session.get('co_id', 'Default')
    branch = request.session.get('branch')
    print(co_id)
    if request.method == "POST":

        brand_name = request.POST.get('brand_name', '').strip().upper()

        if not brand_name:
            error_message = "Brand name cannot be empty."
        elif Brand.objects.filter(brand_name__iexact=brand_name,co_id=co_id,branch_id=branch).exists():
            error_message = "This brand already exists."
        else:
            # Generate the next brand_custom_id for this co_id + branch_id
            max_id = Brand.objects.filter(co_id=co_id, branch_id=branch).aggregate(Max('brand_custom_id'))[
                         'brand_custom_id__max'] or 0
            next_custom_id = max_id + 1

            Brand.objects.create(brand_name=brand_name,co_id=co_id,branch_id=branch, brand_custom_id=next_custom_id)
            messages.success(request, "Brand added successfully!")
            return redirect(reverse('main:brand_create'))
    return render(request, 'brands/brand_form.html', {'error_message': error_message})
    
# brand read only mode
def brand_readonly(request, pk):
    brand = get_object_or_404(Brand, pk=pk)

    return render(request, 'brands/brand_edit.html', {'brand': brand})
    
# Update a Brand
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == "POST":
        brand_name = request.POST.get('brand_name', '').strip().upper()
        if brand_name:
            brand.brand_name = brand_name
            brand.save()
            messages.success(request, "Brand updated successfully!")
            return render(request, 'brands/brand_edit.html',{'brand': brand})
    return render(request, 'brands/brand_form.html', {'brand': brand})


# Delete a Brand
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == "POST":
        brand.delete()
        messages.success(request, "Data deleted successfully!")
        # return redirect(reverse('main:brand_list'))
        return render(request,"brands/brand_confirm.html")
    return render(request, 'brands/brand_confirm_delete.html', {'brand': brand})


def vehicle_list(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    query = request.GET.get('q')
    if query:
        vehicles = Vehicle.objects.filter(model_name__iexact=query,co_id=co_id,branch_id=branch)
    else:
        # vehicles = Vehicle.objects.all()
        vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_list.html', {'vehicles': vehicles, 'query': query})


# vehiocle Create view
def vehicle_create(request):
    error_message = None
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if request.method == 'POST':
        model_name = request.POST.get('model_name', '').strip().upper()
        fuel = request.POST.get('fuel')
        brand_id = request.POST.get('brand_id')

        # Check if the vehicle already exists with the same model_name and fuel
        if Vehicle.objects.filter(model_name=model_name, fuel=fuel, co_id=co_id,branch_id=branch).exists():
            error_message = "A vehicle with this model and fuel type already exists."
        else:
            # Get the brand and create a new vehicle
            brand = get_object_or_404(Brand, pk=brand_id)
            Vehicle.objects.create(model_name=model_name, fuel=fuel, brand_id=brand, co_id=co_id,branch_id=branch)
            messages.success(request, "Model added successfully")
            return redirect(reverse('main:vehicle_add'))

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_form.html', {'brands': brands, 'error_message': error_message})
    
# vehicle read only
def vehicle_readonly(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_edit.html', {'vehicle': vehicle, 'brands': brands})


# vehicle Update view
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if request.method == 'POST':
        vehicle.model_name = request.POST.get('model_name', '').strip().upper()
        vehicle.fuel = request.POST.get('fuel')
        vehicle.brand_name = request.POST.get('brand_name')
        vehicle.brand_id = get_object_or_404(Brand, pk=request.POST.get('brand_id'))
        vehicle.save()
        messages.success(request, "Model updated successfully!")
        return render(request, "vehicle_edit.html",{'vehicle':vehicle})

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_form.html', {'vehicle': vehicle, 'brands': brands})


# Vehicle Delete view
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        # return redirect(reverse('main:vehicle_list'))
        return render(request,'vehicle_confirm.html')
    return render(request, 'vehicle_confirm_delete.html', {'vehicle': vehicle})


# vehicle_type list view
def vehicle_type_list(request):
    query = request.GET.get('q')
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if query:
        vehicles = Vehicle_type.objects.filter(vehicle_name__icontains=query,co_id=co_id,branch_id=branch)
    else:
        vehicles = Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_type/vehicle_type_list.html', {'vehicles': vehicles, 'query': query})


# vehicle type create view
def vehicle_type_create(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if request.method == "POST":
        vehicle_name = request.POST.get('vehicle_name').strip().upper()
        brand_id = request.POST.get('brand_id')
        vehicle_id = request.POST.get('vehicle_id')

        print(vehicle_name, brand_id, vehicle_id)
        # Check if vehicle_name already exists
        if Vehicle_type.objects.filter(vehicle_name=vehicle_name, co_id=co_id,branch_id=branch).exists():
            error_message = "A vehicle with this type already exists."
            messages.error(request, error_message)
            # messages.error(request, "Vehicle type already exists!")
            return redirect(reverse('main:vehicle_type_create'))

        brand = Brand.objects.get(id=brand_id) if brand_id else None
        # vehicle = Vehicle.objects.filter(model_name=vehicle_id).first() if vehicle_id else None
        vehicle = Vehicle.objects.get(id=vehicle_id) if vehicle_id else None
        print(vehicle)

        # Generate the next brand_custom_id for this co_id + branch_id
        max_id = Vehicle_type.objects.filter(co_id=co_id, branch_id=branch).aggregate(Max('vehicle_type_custom_id'))[
                     'vehicle_type_custom_id__max'] or 0
        next_custom_id = max_id + 1
        Vehicle_type.objects.create(vehicle_name=vehicle_name, brand_id=brand, vehicle_id=vehicle, co_id=co_id,branch_id=branch,vehicle_type_custom_id= next_custom_id)
        messages.success(request, "Vehicle type added successfully")
        return redirect(reverse('main:vehicle_type_create'))
    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles = Vehicle.objects.values('model_name').distinct()
    # vehicles = Vehicle.objects.values('id', 'model_name', 'brand_id')
    vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_type/vehicle_type_form.html', {'brands': brands, 'vehicles': vehicles})

# vehicle type read only
def vehicle_type_readonly(request, pk):
    vehicle = get_object_or_404(Vehicle_type, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch).values('model_name').distinct()
    vehicles = Vehicle.objects.filter(co_id=co_id, branch_id=branch).distinct()
    return render(request, 'vehicle_type/vehicle_type_edit.html',
                  {'vehicle': vehicle, 'brands': brands, 'vehicles': vehicles})


# vehicle type Update View
def vehicle_type_update(request, pk):
    vehicle = get_object_or_404(Vehicle_type, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if request.method == "POST":
        vehicle.vehicle_name = request.POST.get('vehicle_name', '').strip().upper()
        brand_id = request.POST.get('brand_id')
        vehicle_id = request.POST.get('vehicle_id')

        vehicle.brand_id = Brand.objects.filter(id=brand_id).first() if brand_id else None
        # vehicle.vehicle_id = Vehicle.objects.filter(model_name=vehicle_id).first() if vehicle_id else None
        vehicle.vehicle_id = Vehicle.objects.filter(id=vehicle_id).first() if vehicle_id else None
        vehicle.save()
        messages.success(request, "Data updated successfully!")

        return render(request, "vehicle_type/vehicle_type_edit.html",{'vehicle':vehicle})

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch).values('model_name').distinct()
    vehicles = Vehicle.objects.filter(co_id=co_id, branch_id=branch).distinct()
    return render(request, 'vehicle_type/vehicle_type_form.html',
                  {'vehicle': vehicle, 'brands': brands, 'vehicles': vehicles})

# vehicle type delete
def vehicle_type_delete(request, pk):
    vehicle = get_object_or_404(Vehicle_type, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        # return redirect(reverse('main:vehicle_type_list'))
        return render(request,'vehicle_type/vehicle_type_confirm.html')
    return render(request, 'vehicle_type/vehicle_type_delete.html', {'vehicle': vehicle})
# vehicle master list & search
def vehicle_master_list(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    query=request.GET.get('q')
    if query:
        vehicle_masters=Vehicle_master.objects.filter(registration_number__icontains=query,co_id=co_id,branch_id=branch)
    else:
        vehicle_masters=Vehicle_master.objects.filter(co_id=co_id,branch_id=branch)
    return render(request,'vehicle_master/vehicle_master_list.html',{'vehicle_masters':vehicle_masters})


def vehicle_master_add(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    brands=Brand.objects.filter(co_id=co_id,branch_id=branch)
    vehicles=Vehicle.objects.filter(co_id=co_id,branch_id=branch).values('model_name').distinct()
    vehicle_types=Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    accounts = Table_Accountsmaster.objects.filter(company__company_id=co_id, group="SUNDRY DEBTORS").order_by('head')

    if request.method == "POST":
        rc_owner_name = request.POST.get('rc_owner_name').strip().upper()
        mobile = request.POST.get('mobile')
        brand_id = request.POST.get('brand_id')
        vehicle_id = request.POST.get('vehicle_id')
        vehicle_type_id = request.POST.get('vehicle_type')
        fuel = request.POST.get('fuel')
        registration_number = request.POST.get('registration_number').strip().upper()
        make_year = request.POST.get('make_year')
        chase_number = request.POST.get('chase_number').strip().upper()
        engine_number = request.POST.get('engine_number').strip().upper()
        insurance_renewal = request.POST.get('insurance_renewal')
        pollution_renewal = request.POST.get('pollution_renewal')
        driver_id = request.POST.get('driver_id')

        print("vehicle_id :",vehicle_id)

        # Check if registration_number already exists
        if Vehicle_master.objects.filter(registration_number=registration_number,co_id=co_id,branch_id=branch).exists():
            messages.error(request, "Error: Registration number already exists!")
            return redirect('main:vehicle_master_add')

        # Check if chase_number already exists
        if Vehicle_master.objects.filter(chase_number=chase_number,co_id=co_id,branch_id=branch).exists():
            messages.error(request, "Error: Chase number already exists!")
            return redirect('main:vehicle_master_add')

        # Check if engine_number already exists
        if Vehicle_master.objects.filter(engine_number=engine_number,co_id=co_id,branch_id=branch).exists():
            messages.error(request, "Error: Engine number already exists!")
            return redirect('main:vehicle_master_add')

        # Convert brand, vehicle, and vehicle_type to objects
        brand = Brand.objects.filter(id=brand_id).first()
        vehicle = Vehicle.objects.filter(model_name=vehicle_id).first()
        # This will correctly retrieve the Vehicle object that matches the selected model_name.

        vehicle_type = Vehicle_type.objects.filter(id=vehicle_type_id).first()
        # driver_instance = User.objects.filter(username=driver_username).first()
        driver_instance = Employee_master.objects.filter(id=driver_id).first()if driver_id else None
        print("driver")

        # Handle empty date fields properly
        def parse_date(date_str):
            return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

        # make_year = parse_date(make_year)
        insurance_renewal = parse_date(insurance_renewal)
        pollution_renewal = parse_date(pollution_renewal)

        # Generate the next brand_custom_id for this co_id + branch_id
        max_id = Vehicle_master.objects.filter(co_id=co_id, branch_id=branch).aggregate(Max('rc_owner_id'))[
                     'rc_owner_id__max'] or 0
        next_custom_id = max_id + 1

        # Save data manually
        vehicle =Vehicle_master.objects.create(
            rc_owner_id=next_custom_id,
            rc_owner_name=rc_owner_name,
            mobile=mobile,
            brand_id=brand,
            vehicle_id=vehicle,
            vehicle_type=vehicle_type,
            fuel=fuel,
            registration_number=registration_number,
            make_year=make_year,
            chase_number=chase_number,
            engine_number=engine_number,
            insurance_renewal=insurance_renewal,
            pollution_renewal=pollution_renewal,
            driver= driver_instance,
            co_id=co_id,
            branch_id=branch
        )

        messages.success(request, "Vehicle master added successfully")
        return redirect('main:vehicle_master_add')
        # except Exception as e:
        #     return HttpResponse(f"Error: {e}")
    # brands=Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles=Vehicle.objects.filter(co_id=co_id,branch_id=branch).values('model_name').distinct()
    # vehicle_types=Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    # drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    # users=User.objects.filter(is_superuser=False)

    return render(request, 'vehicle_master/vehicle_master_form.html',{'brands':brands,'vehicles':vehicles,'vehicle_types':vehicle_types,'drivers':drivers, 'accounts':accounts})

# vehicle master readonly
def vehicle_master_readonly(request, pk):
    vehicle = get_object_or_404(Vehicle_master, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch).values('model_name').distinct()
    vehicles = Vehicle.objects.filter(co_id=co_id, branch_id=branch)
    vehicle_types = Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    # users = User.objects.filter(is_superuser=False)
    drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    return render(request, 'vehicle_master/vehicle_master_edit.html', {
        'vehicle': vehicle,
        'brands': brands,
        'vehicles': vehicles,
        'vehicle_types': vehicle_types,
        'drivers': drivers
    })

# udate vehicle master
def vehicle_master_update(request, pk):
    vehicle = get_object_or_404(Vehicle_master, pk=pk)
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch)
    vehicle_types = Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    accounts = Table_Accountsmaster.objects.filter(user=request.user,group="SUNDRY DEBTORS").order_by('head')

    if request.method == "POST":
        rc_owner_name = request.POST.get('rc_owner_name').strip().upper()
        mobile = request.POST.get('mobile')
        brand_id = request.POST.get('brand_id')
        vehicle_model_name = request.POST.get('vehicle_id')
        vehicle_type_id = request.POST.get('vehicle_type')
        fuel = request.POST.get('fuel')
        registration_number = request.POST.get('registration_number').strip().upper()
        make_year = request.POST.get('make_year')
        chase_number = request.POST.get('chase_number').strip().upper()
        engine_number = request.POST.get('engine_number').strip().upper()
        insurance_renewal = request.POST.get('insurance_renewal')
        pollution_renewal = request.POST.get('pollution_renewal')
        driver_id = request.POST.get('driver_id')

        # Check for duplicate values excluding the current record
        if Vehicle_master.objects.filter(registration_number=registration_number,co_id=co_id,branch_id=branch).exclude(id=pk).exists():
            messages.error(request, "Error: Registration number already exists!")
            return redirect('main:vehicle_master_update',pk=pk)

        if Vehicle_master.objects.filter(chase_number=chase_number,co_id=co_id,branch_id=branch).exclude(id=pk).exists():
            messages.error(request, "Error: Chase number already exists!")
            return redirect('main:vehicle_master_update', pk=pk)

        if Vehicle_master.objects.filter(engine_number=engine_number,co_id=co_id,branch_id=branch).exclude(id=pk).exists():
            messages.error(request, "Error: Engine number already exists!")
            return redirect('main:vehicle_master_update', pk=pk)

        # Convert brand, vehicle, and vehicle_type to objects
        brand = Brand.objects.filter(id=brand_id).first()
        vehicle_model = Vehicle.objects.filter(id=vehicle_model_name).first()
        vehicle_type = Vehicle_type.objects.filter(id=vehicle_type_id).first()
        driver_instance = Employee_master.objects.filter(id=driver_id).first()if driver_id else None

        # Handle empty date fields properly
        def parse_date(date_str):
            return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

        # make_year = parse_date(make_year)
        insurance_renewal = parse_date(insurance_renewal)
        pollution_renewal = parse_date(pollution_renewal)

        # Update the vehicle instance
        vehicle.rc_owner_name = rc_owner_name
        vehicle.mobile = mobile
        vehicle.brand_id = brand
        vehicle.vehicle_id = vehicle_model
        vehicle.vehicle_type = vehicle_type
        vehicle.fuel = fuel
        vehicle.registration_number = registration_number
        vehicle.make_year = make_year
        vehicle.chase_number = chase_number
        vehicle.engine_number = engine_number
        vehicle.insurance_renewal = insurance_renewal
        vehicle.pollution_renewal = pollution_renewal
        vehicle.driver = driver_instance

        vehicle.save()

        messages.success(request, "Vehicle master updated successfully")
        # return redirect('main:vehicle_master_update', pk=pk)
        return render(request,'vehicle_master/vehicle_master_edit.html',{'vehicle':vehicle})

    # brands = Brand.objects.filter(co_id=co_id,branch_id=branch)
    # vehicles = Vehicle.objects.filter(co_id=co_id,branch_id=branch)
    # vehicle_types = Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    # drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    # users = User.objects.filter(is_superuser=False)

    return render(request, 'vehicle_master/vehicle_master_form.html', {
        'vehicle': vehicle,
        'brands': brands,
        'vehicles': vehicles,
        'vehicle_types': vehicle_types,
        'drivers': drivers,
        'accounts': accounts
    })
# Delete a vehicle master delete
def vehicle_master_delete(request, pk):
    vehicle_master = get_object_or_404(Vehicle_master, pk=pk)
    if request.method == "POST":
        vehicle_master.delete()
        return render(request,"vehicle_master/vehicle_master_confirm.html")
    return render(request, 'vehicle_master/vehicle_master_delete.html', {'vehicle_master': vehicle_master})
    
    
    

# List Employees
def employee_list(request):
    query=request.GET.get('q')
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    if query:
        employees = Employee_master.objects.filter(employee_name__icontains=query,co_id=co_id,branch_id=branch)
    else:
        employees = Employee_master.objects.filter(co_id=co_id,branch_id=branch)
    return render(request, 'employee/employee_list.html', {'employees': employees,'query':query})
# create employees
def employee_create(request):
    existing_departments = Employee_master.objects.values_list('department', flat=True).distinct()
    existing_designations = Employee_master.objects.values_list('designation', flat=True).distinct()
    co_id = request.session.get('co_id')
    branch_id = request.session.get('branch')
    if request.method == "POST":
        employee_name = request.POST.get('employee_name').strip().upper()
        address_1 = request.POST.get('address_1').strip().upper()
        address_2 = request.POST.get('address_2').strip().upper()
        address_3 = request.POST.get('address_3').strip().upper()
        telephone = request.POST.get('telephone')
        mobile = request.POST.get('mobile')
        working_status = request.POST.get('working_status')
        # dob = request.POST.get('dob')
        designation = request.POST.get('designation').strip().upper()
        department = request.POST.get('department').strip().upper()
        salary = request.POST.get('salary')
        esi = request.POST.get('esi')
        pf = request.POST.get('pf')
        date_joining = request.POST.get('date_joining')
        bank_name = request.POST.get('bank_name').strip().upper()
        branch = request.POST.get('branch').strip().upper()
        ifsc_code = request.POST.get('ifsc_code').strip().upper()
        casual_leaves = request.POST.get('casual_leaves')

        # Validate mobile number (must be exactly 10 digits)
        if not re.fullmatch(r'\d{10}', mobile):
            messages.error(request, "Invalid mobile number! It must be exactly 10 digits.")
            return render(request, 'employee/employee_form.html',{'existing_departments': existing_departments,'existing_designations': existing_designations})
        # Check if mobile already exists
        if Employee_master.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already exists!")
            return render(request, 'employee/employee_form.html', {'existing_departments': existing_departments,'existing_designations': existing_designations})

        # Generate the next brand_custom_id for this co_id + branch_id
        max_id = Employee_master.objects.filter(co_id=co_id, branch_id=branch_id).aggregate(Max('employee_custom_id'))[
                     'employee_custom_id__max'] or 0
        next_custom_id = max_id + 1

        Employee_master.objects.create(
            employee_custom_id=next_custom_id ,
            employee_name=employee_name,
            address_1=address_1,
            address_2=address_2,
            address_3=address_3,
            telephone=telephone,
            mobile=mobile,
            working_status=working_status,

            designation=designation,
            department=department,
            salary=salary,
            esi=esi,
            pf=pf,
            date_joining=date_joining,
            bank_name=bank_name,
            branch=branch,
            ifsc_code=ifsc_code,
            casual_leaves=casual_leaves,
            co_id=co_id,
            branch_id = branch_id
        )
        messages.success(request, "Employee added successfully")
        return redirect('main:employee_create')

    return render(request, 'employee/employee_form.html',{'existing_departments': existing_departments,'existing_designations': existing_designations})
def employee_readonly(request, pk):
    existing_departments = Employee_master.objects.values_list('department', flat=True).distinct()
    existing_designations = Employee_master.objects.values_list('designation', flat=True).distinct()
    employee = get_object_or_404(Employee_master, pk=pk)



    return render(request, 'employee/employee_edit.html',
                  {'employee': employee, 'existing_departments': existing_departments,
                   'existing_designations': existing_designations})

# employee update view
def employee_update(request, pk):
    existing_departments = Employee_master.objects.values_list('department', flat=True).distinct()
    existing_designations = Employee_master.objects.values_list('designation', flat=True).distinct()
    employee = get_object_or_404(Employee_master, pk=pk)

    if request.method == "POST":
        employee_id = request.POST.get('employee_id')  # Capture ID (not editable)
        employee_name = request.POST.get('employee_name').strip().upper()
        address_1 = request.POST.get('address_1').strip().upper()
        address_2 = request.POST.get('address_2').strip().upper()
        address_3 = request.POST.get('address_3').strip().upper()
        telephone = request.POST.get('telephone')
        mobile = request.POST.get('mobile')
        working_status = request.POST.get('working_status')
        # dob = request.POST.get('dob')
        designation = request.POST.get('designation').strip().upper()
        department = request.POST.get('department').strip().upper()
        salary = request.POST.get('salary')
        esi = request.POST.get('esi')
        pf = request.POST.get('pf')
        date_joining = request.POST.get('date_joining')
        bank_name = request.POST.get('bank_name').strip().upper()
        branch = request.POST.get('branch').strip().upper()
        ifsc_code = request.POST.get('ifsc_code').strip().upper()
        casual_leaves = request.POST.get('casual_leaves')

        # Validate mobile number (must be exactly 10 digits)
        if not re.fullmatch(r'\d{10}', mobile):
            messages.error(request, "Invalid mobile number! It must be exactly 10 digits.")
            return render(request, 'employee/employee_form.html',{ 'employee': employee,'existing_departments': existing_departments,'existing_designations': existing_designations})
        # Check if mobile already exists for another employee
        if Employee_master.objects.filter(mobile=mobile).exclude(pk=pk).exists():
            messages.error(request, "Mobile number already exists!")
            return render(request, 'employee/employee_form.html', { 'employee': employee,'existing_departments': existing_departments,'existing_designations': existing_designations})

        # Update employee data
        employee.employee_name = employee_name
        employee.address_1 = address_1
        employee.address_2 = address_2
        employee.address_3 = address_3
        employee.telephone = telephone
        employee.mobile = mobile
        employee.working_status = working_status

        employee.designation = designation
        employee.department = department
        employee.salary = salary
        employee.esi = esi
        employee.pf = pf
        employee.date_joining = date_joining
        employee.bank_name = bank_name
        employee.branch = branch
        employee.ifsc_code = ifsc_code
        employee.casual_leaves = casual_leaves

        employee.save()
        messages.success(request, "Employee updated successfully!")
        return render(request,'employee/employee_edit.html',{'employee':employee,'existing_departments': existing_departments,'existing_designations': existing_designations})

    return render(request, 'employee/employee_form.html', {'employee': employee,'existing_departments': existing_departments,'existing_designations': existing_designations})


# Delete Employee
def employee_delete(request, pk):
    employee = get_object_or_404(Employee_master, pk=pk)

    if request.method == "POST":
        employee.delete()
        return render(request,'employee/employee_confirm.html')

    return render(request, 'employee/employee_delete.html', {'employee': employee})



def trip_list(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')

    series_list = Trip_sheet.objects.filter(co_id=co_id,branch_id=branch).values_list('series', flat=True).distinct()
    print("series",series_list)
    series = request.GET.get('series')
    entry_number = request.GET.get('entry_number')
    # print("series",series,"entry",entry_number)
    if series and entry_number:
        trip = Trip_sheet.objects.filter(series=series, entry_number=entry_number).first()

        if trip:
            return redirect('main:trip_update', series=trip.series, entry_number=trip.entry_number)
        else:
            return render(request, 'trip_sheet/trip_search.html', {'error': 'No matching trip sheet found.','series_list': series_list})
    return render(request, 'trip_sheet/trip_search.html',{'series_list': series_list} )
# trip create

def trip_create(request):
    fycode = request.session.get('fycode')
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    user = request.session.get('user')
    vehicles = Vehicle_master.objects.filter(co_id=co_id,branch_id=branch)
    vehicle_types = Vehicle_type.objects.filter(co_id=co_id,branch_id=branch)
    drivers = Employee_master.objects.filter(designation="Driver",co_id=co_id,branch_id=branch)
    # customers = Table_Accountsmaster.objects.all()
    customers = Table_Accountsmaster.objects.filter(
        children__company_id=co_id,children__branch_id=branch, category='Customers'
    )
    loading_points = LocationMaster.objects.values_list("loading_point", flat=True).distinct()
    unloading_points = LocationMaster.objects.values_list("unloading_point", flat=True).distinct()
    fuel_stations = VendorMaster.objects.filter(company__company_id=request.session.get("co_id"))

    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    branch = Branch_master.objects.get(branch_name=branch)
    vouchers  = VoucherConfiguration.objects.filter(category="Trip sheet", company=company,branch=branch)
    is_update = False
    # Get the last `sl_no` and increment it
    # last_trip = Trip_sheet.objects.order_by('-sl_no').first()
    # next_sl_no = (last_trip.sl_no + 1) if last_trip else 1
    next_sl_no = 1
    if request.method == "POST":
        # Fetch related model instances
        vehicle_instance = Vehicle_master.objects.get(id=request.POST.get('vehicle_number'))
        vehicle_type_instance = Vehicle_type.objects.get(id=request.POST.get('vehicle_type_id'))
        driver_instance = Employee_master.objects.get(id=request.POST.get('driver_name'))
        series_instance = VoucherConfiguration.objects.get(id=request.POST.get('series'))
        print("series_inst:",series_instance)
        # Retrieve multiple row values
        customer_name_list = request.POST.getlist('customer_name[]')
        loading_point_list = request.POST.getlist('loading_point[]')
        unloading_point_list = request.POST.getlist('unloading_point[]')
        product_list = request.POST.getlist('product[]')
        remark_list = request.POST.getlist('remark[]')

        # Use the series name instead of the foreign key
        series_name = series_instance.series
        print("series_name:",series_name)

        # Fetch related model instances
        series_instance = VoucherConfiguration.objects.get(id=request.POST.get('series'))

        # Use its serial_no as entry number
        entry_number = series_instance.serial_no + 1

        # Update the serial_no in VoucherConfiguration
        series_instance.serial_no = entry_number
        series_instance.save()

        # Insert multiple trip records
        for i in range(len(customer_name_list)):
            customer_instance = Table_Accountsmaster.objects.get(id=customer_name_list[i])  # Fetch the customer instance
            # print("customer instance",customer_instance.account_code)
            Trip_sheet.objects.create(
                financial_year=fycode,
                user=user,
                co_id=co_id,
                branch_id=branch,
                series=series_name,
                series_id=series_instance,
                entry_number=entry_number,
                loading_date=request.POST.get('loading_date'),
                vehicle_number_id=vehicle_instance,
                vehicle_type_id=vehicle_type_instance,
                unloading_date=request.POST.get('unloading_date'),
                driver_name_id=driver_instance,
                sl_no=i + 1,
                # customer_name=customer_name_list[i].strip().upper(),
                customer_name=customer_instance,  # Use the ForeignKey instance
                account_code=customer_instance.account_code,

                loading_point=loading_point_list[i].strip().upper(),
                unloading_point=unloading_point_list[i].strip().upper(),
                product=product_list[i].strip().upper(),
                remark=remark_list[i].strip().upper(),
                payment_by=request.POST.get('payment_by'),
                statutory_narration=request.POST.get('statutory_narration'),


                # FloatFields (convert empty string to None)
                starting_km=float(request.POST.get('starting_km')or 0),
                ending_km=float(request.POST.get('ending_km')or 0),
                km_rate=float(request.POST.get('km_rate')or 0),
                filling_km=float(request.POST.get('filling_km')or 0),
                tyre_work=float(request.POST.get('tyre_work')or 0),
                battery=float(request.POST.get('battery')or 0),
                mech_electric=float(request.POST.get('mech_electric')or 0),
                statutory_charge=float(request.POST.get('statutory_charge')or 0),
                total_km=float(request.POST.get('total_km')or 0),
                km_charge_total=float(request.POST.get('km_charge_total')or 0),
                extra_hour_charge_total=float(request.POST.get('extra_hour_charge_total')or 0),
                fixed_charge_total=float(request.POST.get('fixed_charge_total')or 0),
                haulting_charge_total=float(request.POST.get('haulting_charge_total')or 0),
                toll_parking_total=float(request.POST.get('toll_parking_total')or 0),

                rate_type=request.POST.get('rate_type'),
               
                diesel_ltr=float(request.POST.get('diesel_ltr') or 0),
                diesel_charges=float(request.POST.get('diesel_charges')or 0),
                advance_driver=float(request.POST.get('advance_driver')or 0),
                
                driver_bata=float(request.POST.get('driver_bata') or 0),
                advance_from_customer=float(request.POST.get('advance_from_customer')or 0),
                total_freight_charges=float(request.POST.get('total_freight_charges')or 0),

            )
        messages.success(request, "Trip sheet added successfully")
        return redirect('main:trip_create')

    return render(request, 'trip_sheet/tripsheet_form.html',{'vehicles':vehicles,'vehicle_types':vehicle_types,'drivers':drivers,
                                                             'next_sl_no': next_sl_no,"is_update": is_update,"customers":customers,"vouchers":vouchers,
                                                             'loading_points': loading_points, 'unloading_points': unloading_points, 'fuel_stations': fuel_stations})




def get_rate(request):
    vehicle_id = request.GET.get("vehicle_id")
    customer_id = request.GET.get("customer_id")
    co_id = request.session.get("co_id")

    try:
        if vehicle_id:
            vehicle = Vehicle_master.objects.get(id=vehicle_id, co_id=co_id)
            vehicle_type_id = vehicle.vehicle_type.id if vehicle.vehicle_type else None
            vehicle_type = vehicle.vehicle_type.vehicle_name if vehicle.vehicle_type else None

            response_data = {
                "success": True,
                "vehicle_type_id": vehicle_type_id,
                "vehicle_type": vehicle_type,
            }

            # If customer also selected ? add rate to response
            if customer_id:
                customer = Table_Accountsmaster.objects.get(id=customer_id)
                company = Table_Companydetailsmaster.objects.get(company_id=co_id)

                child = RateChild.objects.get(
                    vehicle=vehicle.vehicle_type.vehicle_name,
                    type='Km Wise',
                    master__customer_name=customer.head,
                    master__company=company
                )
                print("child rate:",child.rate)
                response_data["rate"] = child.rate

            return JsonResponse(response_data)

        return JsonResponse({"success": False, "message": "Invalid request"})

    except Exception as e:
        print("Error:", e)
        return JsonResponse({"success": False, "message": str(e)})

def get_fixed_rate(request):
    vehicle_id = request.GET.get("vehicle_id")
    customer_id = request.GET.get("customer_id")
    loading_point = request.GET.get("loading_point")
    unloading_point = request.GET.get("unloading_point")
    co_id = request.session.get("co_id")

    customer = Table_Accountsmaster.objects.filter(id=customer_id).first()

    print("DEBUG => vehicle_id:", vehicle_id,
      "customer:", customer.head,
      "loading_point:", loading_point,
      "unloading_point:", unloading_point,
      "co_id:", co_id)

    try:
        master = LocationMaster.objects.filter(company__company_id=co_id, customer=customer.head, loading_point=loading_point, 
                                      unloading_point=unloading_point, vehicle_type=vehicle_id).first()
        if master:
            rate = master.rate
            response_data = {"success": True, "rate": rate}
        else:
            response_data = {"success": False, "message": "No matching fixed rate found"}
        return JsonResponse(response_data)    
    except Exception as e:
        print("Error:", e)
        return JsonResponse({"success": False, "message": str(e)})


# function
def get_next_entry_number(request):
    series_id = request.GET.get('series_id')
    if series_id:
        try:
            series_instance = VoucherConfiguration.objects.get(id=series_id)
            next_entry_number = series_instance.serial_no + 1
            return JsonResponse({'entry_number': next_entry_number})
        except VoucherConfiguration.DoesNotExist:
            return JsonResponse({'error': 'Invalid series'}, status=400)
    return JsonResponse({'error': 'Missing series_id'}, status=400)

def trip_update(request, series, entry_number):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    # trips = get_object_or_404(Trip_sheet, series=series, entry_number=entry_number)
    trips = Trip_sheet.objects.filter(series=series, entry_number=entry_number)
    first_trip = trips.first()
    is_update = True # flag for setting trip loop
    # print("trips",trips)
    # for trip in trips:
    #     print("trips series:", trip.series)
    next_sl_no = 1
    if request.method == "POST":

        vehicle_number_id = request.POST.get('vehicle_number')
        vehicle_type_id = request.POST.get('vehicle_type_id')
        driver_name_id = request.POST.get('driver_name')

        if vehicle_number_id:
            vehicle = Vehicle_master.objects.filter(id=vehicle_number_id).first()
            # print("vehicle :",vehicle)
            if vehicle:
                for trip in trips:
                    print("trip :",trip)
                    trip.vehicle_number_id = vehicle

            else:
                messages.error(request, "Selected vehicle does not exist.")
                return redirect(request.path_info)


        if vehicle_type_id:
            vehicle_type_instance = Vehicle_type.objects.filter(id=vehicle_type_id).first()
            if vehicle_type_instance:
                for trip in trips:
                    trip.vehicle_type_id = vehicle_type_instance
                    # print(f"Assigned Vehicle Type: {trips.vehicle_type_id}")
            else:
                messages.error(request, "Invalid Vehicle Type selected.")
                return redirect(request.path_info)
        if driver_name_id:
            driver_name_instance = Employee_master.objects.filter(id=driver_name_id).first()
            if driver_name_instance:
                for trip in trips:
                    trip.driver_name_id = driver_name_instance
            else:
                messages.error(request, "Invalid driver .")

            # if driver_name_id:
            #     driver_name_instance = Employee_master.objects.filter(id=driver_name_id).first()
            #     if driver_name_instance:
            #         # for trip in trips:
            #         print("driver_name_instance : ",driver_name_instance.employee_name)
            #         trips.driver_name_id = driver_name_instance
            #     else:
            #         messages.error(request, "Invalid driver .")

        # Retrieve multiple row values
        customer_name_list = request.POST.getlist('customer_name[]')
        # print("customer_name",customer_name_list)
        loading_point_list = request.POST.getlist('loading_point[]')
        unloading_point_list = request.POST.getlist('unloading_point[]')
        product_list = request.POST.getlist('product[]')
        remark_list = request.POST.getlist('remark[]')

        # Fetch existing trip records and create a mapping with `sl_no`
        existing_trips = {trip.sl_no: trip for trip in trips}
        print("existing_trip :",trip.sl_no)
        updated_sl_numbers = []  # Track updated records to remove unused ones later

        for i in range(len(customer_name_list)):
            sl_no = i + 1
            updated_sl_numbers.append(sl_no)

            if sl_no in existing_trips:
                # Update existing trip
                trip = existing_trips[sl_no]
            else:
                # Create new trip record
                trip = Trip_sheet(series=series, entry_number=entry_number, sl_no=sl_no)


            # Assign updated values
            customer = Table_Accountsmaster.objects.filter(id=customer_name_list[i]).first()
            trip.customer_name = customer
            trip.account_code = customer.account_code
            trip.loading_date = request.POST.get('loading_date')
            trip.unloading_date = request.POST.get('unloading_date')
            # trip.customer_name = customer_name_list[i].strip().upper()
            trip.loading_point = loading_point_list[i].strip().upper()
            trip.unloading_point = unloading_point_list[i].strip().upper()
            trip.product = product_list[i].strip().upper()
            trip.remark = remark_list[i].strip().upper()
            trip.payment_by = request.POST.get('payment_by')
            trip.statutory_narration = request.POST.get('statutory_narration')
            trip.rate_type = request.POST.get('rate_type')

            # FloatFields (convert empty string to None)
            trip.starting_km = float(request.POST.get('starting_km')) if request.POST.get('starting_km') else None
            trip.ending_km = float(request.POST.get('ending_km')) if request.POST.get('ending_km') else None
            trip.km_rate = float(request.POST.get('km_rate')) if request.POST.get('km_rate') else None
            trip.filling_km = float(request.POST.get('filling_km')) if request.POST.get('filling_km') else None
            trip.tyre_work = float(request.POST.get('tyre_work')) if request.POST.get('tyre_work') else None
            trip.battery = float(request.POST.get('battery')) if request.POST.get('battery') else None
            trip.mech_electric = float(request.POST.get('mech_electric')) if request.POST.get('mech_electric') else None
            trip.statutory_charge = float(request.POST.get('statutory_charge')) if request.POST.get('statutory_charge') else None
            trip.total_km = float(request.POST.get('total_km')) if request.POST.get('total_km') else None
            trip.km_charge_total = float(request.POST.get('km_charge_total')) if request.POST.get('km_charge_total') else None
            trip.extra_hour_charge_total = float(request.POST.get('extra_hour_charge_total')) if request.POST.get('extra_hour_charge_total') else None
            trip.fixed_charge_total = float(request.POST.get('fixed_charge_total')) if request.POST.get('fixed_charge_total') else None
            trip.haulting_charge_total = float(request.POST.get('haulting_charge_total')) if request.POST.get('haulting_charge_total') else None
            trip.toll_parking_total = float(request.POST.get('toll_parking_total')) if request.POST.get('toll_parking_total') else None
            trip.diesel_ltr = float(request.POST.get('diesel_ltr')) if request.POST.get('diesel_ltr') else None
            trip.diesel_charges = float(request.POST.get('diesel_charges')) if request.POST.get('diesel_charges') else None
            trip.advance_driver = float(request.POST.get('advance_driver')) if request.POST.get('advance_driver') else None
            trip.driver_bata = float(request.POST.get('driver_bata')) if request.POST.get('driver_bata') else None
            trip.advance_from_customer = float(request.POST.get('advance_from_customer')) if request.POST.get('advance_from_customer') else None
            trip.total_freight_charges = float(request.POST.get('total_freight_charges')) if request.POST.get('total_freight_charges') else None
            trip.user = request.session.get('user')
            trip.save()
        # Remove records that were not included in the update
        trips.exclude(sl_no__in=updated_sl_numbers).delete()

        messages.success(request, "Trip sheet updated successfully!")
        return redirect('main:trip_list')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    branch = Branch_master.objects.get(branch_name=branch)
    context = {
        'trips': trips,
        'first_trip': first_trip,
        'vehicles': Vehicle_master.objects.filter(co_id=co_id,branch_id=branch),
        'drivers': Employee_master.objects.filter(designation='Driver',co_id=co_id,branch_id=branch),
        'vehicle_types': Vehicle_type.objects.filter(co_id=co_id,branch_id=branch),
        'next_sl_no': next_sl_no,
        "is_update": is_update,
        "customers": Table_Accountsmaster.objects.filter(children__company_id=co_id,children__branch_id=branch, category='Customers'),
        "vouchers":VoucherConfiguration.objects.filter(category="Trip sheet",company=company,branch=branch)
    }
    return render(request, 'trip_sheet/tripsheet_form.html', context)
# def trip_read_only(request):
#     series_list = Trip_sheet.objects.values_list('series', flat=True).distinct()
#     print("series",series_list)
#     series = request.GET.get('series')
#     entry_number = request.GET.get('entry_number')
#     # print("series",series,"entry",entry_number)
#     if series and entry_number:
#         trip = Trip_sheet.objects.filter(series=series, entry_number=entry_number).first()
#
#         if trip:
#             return redirect('main:trip_update', series=trip.series, entry_number=trip.entry_number)
#         else:
#             return render(request, 'trip_sheet/trip_read_only.html', {'error': 'No matching trip sheet found.','series_list': series_list})
#     return render(request, 'trip_sheet/trip_read_only.html',{'series_list': series_list} )
def trip_search_delete(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    series_list = Trip_sheet.objects.filter(co_id=co_id,branch_id=branch).values_list('series', flat=True).distinct()
    series = request.GET.get('series')
    entry_number = request.GET.get('entry_number')

    if series and entry_number:
        trip = Trip_sheet.objects.filter(series=series, entry_number=entry_number).first()


        if trip:
            return redirect('main:trip_read_only', series=trip.series, entry_number=trip.entry_number)
        else:
            return render(request, 'trip_sheet/search_delete.html', {
                'error': 'No matching trip sheet found.',
                'series_list': series_list
            })

    return render(request, 'trip_sheet/search_delete.html', {'series_list': series_list})
# Trip
def trip_read_only(request, series, entry_number):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    # trips = get_object_or_404(Trip_sheet, series=series, entry_number=entry_number)
    trips = Trip_sheet.objects.filter(series=series, entry_number=entry_number)
    first_trip = trips.first()
    is_update = True # flag for setting trip loop in tripsheet_form
    # print("trips",trips)
    # for trip in trips:
    #     print("trips series:", trip.series)
    next_sl_no = 1


    context = {
        'trips': trips,
        'first_trip': first_trip,
        'vehicles': Vehicle_master.objects.filter(co_id=co_id,branch_id=branch),
        'drivers': Employee_master.objects.filter(designation='Driver',co_id=co_id,branch_id=branch),
        'vehicle_types': Vehicle_type.objects.filter(co_id=co_id,branch_id=branch),
        "customers": Table_Accountsmaster.objects.filter(children__company_id=co_id,children__branch_id=branch ),
        'next_sl_no': next_sl_no,
        "is_update": is_update,

    }
    return render(request, 'trip_sheet/trip_readonly.html', context)
# Trip delete
def trip_delete(request, series, entry_number):
    trips = Trip_sheet.objects.filter(series=series, entry_number=entry_number)
    first_trip = trips.first()
    if request.method == "POST":
        trips = Trip_sheet.objects.filter(series=series, entry_number=entry_number)
        if trips.exists():
            trips.delete()
            return render(request,'trip_sheet/tripsheet_confirm.html')

    return render(request, 'trip_sheet/tripsheet_delete.html',{'trips':trips,"first_trip":first_trip} )




###############################------ACCOUNTS-------##############################

# - ACCOUNT MASTER

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Table_Accountsmaster
from .forms import AccountMasterForm
import json


class AccountMasterView(LoginRequiredMixin, CreateView):
    model = Table_Accountsmaster
    form_class = AccountMasterForm
    template_name = 'account_master/acc-master.html'
    success_url = reverse_lazy("main:acc_master")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        company = Table_Companydetailsmaster.objects.get(company_id=self.request.session.get('co_id'))
        branch = Branch_master.objects.get(branch_name=self.request.session.get('branch'))
        fy_code = self.request.session.get('fycode')

        form.instance.user = self.request.user
        form.instance.company = company
        form.instance.branch = branch
        form.instance._fycode = fy_code
        
        opbalance = form.cleaned_data.get('opbalance', 0)  # Get the opening balance
        debitcredit = form.cleaned_data.get('debitcredit')  # Get the debit/credit choice
        
        # Set opbalance and currentbalance based on debitcredit selection
        if debitcredit == 'Debit':
            form.instance.opbalance = abs(opbalance)  # Ensure positive
            form.instance.currentbalance = abs(opbalance)  # Ensure positive
        elif debitcredit == 'Credit':
            form.instance.opbalance = -abs(opbalance)  # Ensure negative
            form.instance.currentbalance = -abs(opbalance)  # Ensure negative
        
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Account created successfully!')
            return response
        except IntegrityError:
            form.add_error('head', 'This head already exists for this user. Please choose a different one.')
            return self.form_invalid(form)



from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Table_Accountsmaster  # Adjust the import according to your structure

from django.http import JsonResponse

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Table_Accountsmaster  # Adjust the import according to your structure

from django.http import JsonResponse

class AccountmMasterUserView(LoginRequiredMixin, ListView):
    model = Table_Accountsmaster
    template_name = "account_master/acc_master_list.html"
    context_object_name = "userlists"

    def get_queryset(self):
        queryset = self.model.objects.filter(
            user=self.request.user,
        )

        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(head__icontains=search_query)

        return queryset

    def get(self, request, *args, **kwargs):
        # Check if the request is AJAX by inspecting the HTTP headers
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            queryset = self.get_queryset()
            results = [{
                'account_code': userlist.account_code,
                'head': userlist.head,
                'group': userlist.group,
                'category': userlist.category,
                'mobile': userlist.mobile,
                'slug': userlist.slug,
                'get_absolute_url': userlist.get_absolute_url()
            } for userlist in queryset]
            return JsonResponse({'results': results})  # Return JSON response

        return super().get(request, *args, **kwargs)  # Default behavior for non-AJAX requests

class AccountMasterDetailView(DetailView):
    model = Table_Accountsmaster
    template_name = 'account_master/acc_master_detail.html'  # Ensure this template exists

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        user = self.request.user
        
        # Fetch the account associated with the current user using get_object_or_404
        return get_object_or_404(Table_Accountsmaster, slug=slug, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["userlist"] = self.get_object()
        return context


class EditAccountmMasterUserView(LoginRequiredMixin, UpdateView):
    model = Table_Accountsmaster
    form_class = AccountMasterForm
    template_name = 'account_master/acc-master.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        user = self.request.user
        return get_object_or_404(Table_Accountsmaster, slug=slug, user=user)

    def form_valid(self, form):
        form.instance.user = self.request.user

        opbalance = form.cleaned_data.get('opbalance', 0)
        debitcredit = form.cleaned_data.get('debitcredit')

        try:
            opbalance = float(opbalance)
        except (TypeError, ValueError):
            opbalance = 0.0

        if debitcredit == 'Debit':
            form.instance.opbalance = abs(opbalance)
        elif debitcredit == 'Credit':
            form.instance.opbalance = -abs(opbalance)

        old_instance = self.get_object()

        try:
            old_opbalance = float(old_instance.opbalance)
            old_currentbalance = float(old_instance.currentbalance)
        except (TypeError, ValueError):
            old_opbalance = 0.0
            old_currentbalance = 0.0

        opbalance_change = form.instance.opbalance - old_opbalance
        form.instance.currentbalance = old_currentbalance + opbalance_change

        #  Pass fycode from session before saving
        fycode = self.request.session.get("fycode")
        form.instance._fycode = fycode  

        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Account updated successfully!')
            return response
        except IntegrityError:
            form.add_error('head', 'This head already exists for this user. Please choose a different one.')
            return self.form_invalid(form)




class DeleteAccountmMasterUserView(DeleteView):
    model = Table_Accountsmaster
    template_name = 'account_master/acc-master.html'
    success_url = reverse_lazy('main:acc_master')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return JsonResponse({'message': 'Deleted successfully'})

    def get(self, request, *args, **kwargs):
        # Ensure that the view only handles DELETE requests
        return JsonResponse({'error': 'GET method not allowed'}, status=405)


# - Voucher
class VoucherConfigurationListView(LoginRequiredMixin, View):
    template_name = 'accounts/voucher-configuration/voucher_configuration.html'
    success_url = reverse_lazy('main:voucher_configuration')

    def get(self, request, *args, **kwargs):
        co_id = request.session.get('co_id')
        branch_name = request.session.get('branch')

        company = Table_Companydetailsmaster.objects.get(company_id=co_id)
        branch = Branch_master.objects.get(branch_name=branch_name)

        configurations = VoucherConfiguration.objects.filter(
            company=company,
            branch=branch
        )
        next_serial_numbers = {}

        for config in configurations:
            category_series = (config.category, config.series)
            last_serial = VoucherConfiguration.objects.filter(
                company=company,
                branch=branch,
                category=config.category,
                series=config.series
            ).order_by('-serial_no').first()
            if last_serial:
                next_serial_numbers[category_series] = last_serial.serial_no + 1
            else:
                next_serial_numbers[category_series] = 1

        context = {
            'object_list': configurations,
            'next_serial_numbers': next_serial_numbers
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        co_id = request.session.get('co_id')
        branch_name = request.session.get('branch')
        fy_year = request.session.get('fycode')

        category = request.POST.get('category')
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')

        if category and series and serial_no:
            company = get_object_or_404(Table_Companydetailsmaster, company_id=co_id)
            branch = get_object_or_404(Branch_master, branch_name=branch_name)

            # Convert series to uppercase before checking and saving
            series = series.upper()  

            exists = VoucherConfiguration.objects.filter(
                company=company,
                branch=branch,
                category=category,
                series=series
            ).exists()

            if exists:
                configurations = VoucherConfiguration.objects.filter(company=company, branch=branch)
                context = {
                    'object_list': configurations,
                    'error': 'This combination of category and series already exists for this company and branch.'
                }
                return render(request, self.template_name, context)

            VoucherConfiguration.objects.create(
                company=company,
                branch=branch,
                category=category,
                series=series,  # stored in uppercase
                serial_no=serial_no,
                fy_year=fy_year  
            )
            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})

        configurations = VoucherConfiguration.objects.filter(company=company, branch=branch)
        context = {
            'object_list': configurations,
            'error': 'All fields are required.'
        }
        return render(request, self.template_name, context)



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from .models import VoucherConfiguration

def voucher_update(request, pk):
    voucher = get_object_or_404(VoucherConfiguration, pk=pk)

    if request.method == 'POST':
        category = request.POST.get('category')
        series = request.POST.get('series').upper()
        serial_no = request.POST.get('serial_no')

        voucher.category = category
        voucher.series = series
        voucher.serial_no = serial_no

        try:
            voucher.save()
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('main:voucher_search')
            })
        except IntegrityError:
            return JsonResponse({
                'success': False,
                'error': "This combination of company, branch, category, and series already exists."
            })

    return render(request, 'accounts/voucher-configuration/voucher_configuration.html', {
        'voucher': voucher
    })

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import VoucherConfiguration

def voucher_delete(request, pk):
    voucher = get_object_or_404(VoucherConfiguration, pk=pk)
    voucher.delete()
    messages.success(request, "Voucher deleted successfully.")
    return redirect('main:voucher_search')  


class ValidateVoucherConfiguration(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        series = request.GET.get('series')
        next_serial_no = 1  # Default to 1 if no existing serial number

        if series:
            last_serial = Table_Voucher.objects.filter(Series=series, FYCode=self.request.session.get('fycode')).order_by('-VoucherNo').first()
            if last_serial:
                next_serial_no = last_serial.VoucherNo + 1

        return JsonResponse({'next_serial_no': next_serial_no})
    

class VoucherConfigurationTable(LoginRequiredMixin, ListView):
    model = VoucherConfiguration
    template_name = 'accounts/voucher-configuration/voucher_search.html'
    context_object_name = "voucherconfiguration"

    def get_queryset(self):
        co_id = self.request.session.get('co_id')
        branch = self.request.session.get('branch')
        return VoucherConfiguration.objects.filter(
            company__company_id=co_id,
            branch__branch_name=branch
        )# - Voucher Configuration
class VoucherConfigurationListView(LoginRequiredMixin, View):
    template_name = 'accounts/voucher-configuration/voucher_configuration.html'
    success_url = reverse_lazy('main:voucher_configuration')

    def get(self, request, *args, **kwargs):
        co_id = request.session.get('co_id')
        branch_name = request.session.get('branch')

        company = Table_Companydetailsmaster.objects.get(company_id=co_id)
        branch = Branch_master.objects.get(branch_name=branch_name)

        configurations = VoucherConfiguration.objects.filter(
            company=company,
            branch=branch
        )
        next_serial_numbers = {}

        for config in configurations:
            category_series = (config.category, config.series)
            last_serial = VoucherConfiguration.objects.filter(
                company=company,
                branch=branch,
                category=config.category,
                series=config.series
            ).order_by('-serial_no').first()
            if last_serial:
                next_serial_numbers[category_series] = last_serial.serial_no + 1
            else:
                next_serial_numbers[category_series] = 1

        context = {
            'object_list': configurations,
            'next_serial_numbers': next_serial_numbers
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        co_id = request.session.get('co_id')
        branch_name = request.session.get('branch')

        category = request.POST.get('category')
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')

        if category and series and serial_no:
            company = get_object_or_404(Table_Companydetailsmaster, company_id=co_id)
            branch = get_object_or_404(Branch_master, branch_name=branch_name)

            exists = VoucherConfiguration.objects.filter(
                company=company,
                branch=branch,
                category=category,
                series=series
            ).exists()

            if exists:
                configurations = VoucherConfiguration.objects.filter(company=company, branch=branch)
                context = {
                    'object_list': configurations,
                    'error': 'This combination of category and series already exists for this company and branch.'
                }
                return render(request, self.template_name, context)

            VoucherConfiguration.objects.create(
                company=company,
                branch=branch,
                category=category,
                series=series,
                serial_no=serial_no
            )
            return JsonResponse({'success': True, 'redirect_url': str(self.success_url)})

        configurations = VoucherConfiguration.objects.filter(company=company, branch=branch)
        context = {
            'object_list': configurations,
            'error': 'All fields are required.'
        }
        return render(request, self.template_name, context)


class ValidateVoucherConfiguration(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        series = request.GET.get('series')
        next_serial_no = 1  # Default to 1 if no existing serial number

        if series:
            last_serial = Table_Voucher.objects.filter(Series=series, FYCode=self.request.session.get('fycode')).order_by('-VoucherNo').first()
            if last_serial:
                next_serial_no = last_serial.VoucherNo + 1

        return JsonResponse({'next_serial_no': next_serial_no})
    

class VoucherConfigurationTable(LoginRequiredMixin, ListView):
    model = VoucherConfiguration
    template_name = 'accounts/voucher-configuration/voucher_search.html'
    context_object_name = "voucherconfiguration"

    def get_queryset(self):
        co_id = self.request.session.get('co_id')
        branch = self.request.session.get('branch')
        return VoucherConfiguration.objects.filter(
            company__company_id=co_id,
            branch__branch_name=branch
        )

# - COMPANY MASTER


from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Table_Companydetailsmaster
from .forms import ComapnyDetailsMasterForm
from django.core.exceptions import ValidationError


class CompanyDetailsMasterView(LoginRequiredMixin, CreateView):
    model = Table_Companydetailsmaster
    form_class = ComapnyDetailsMasterForm
    template_name = "accounts/company-master/companydetailsmaster.html"
    success_url = reverse_lazy("main:company_details_master")
    success_message = "Company Details Created Successfully"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, self.success_message, extra_tags="form_submit")
            return response
        except ValidationError as e:
            messages.error(self.request, str(e), extra_tags="form_error")
            return self.form_invalid(form)





class CompanyMasterUserView(LoginRequiredMixin, ListView):
    model = Table_Companydetailsmaster
    template_name = "accounts/company-master/companymaster_list.html"
    context_object_name = "companylists"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search")
        if search_query:
            queryset = queryset.filter(head__icontains=search_query)
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            qs_json = serializers.serialize("json", self.get_queryset())
            return JsonResponse({"results": json.loads(qs_json)}, safe=False)
        else:
            return super(CompanyMasterUserView, self).render_to_response(
                context, **response_kwargs
            )


class CompanyMasterDetailView(LoginRequiredMixin, DetailView):
    model = Table_Companydetailsmaster
    template_name = "accounts/company-master/companymaster_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        companylists = get_object_or_404(Table_Companydetailsmaster, slug=slug)
        context["companylist"] = companylists
        return context


class DeletecompanymMasterUserView(LoginRequiredMixin, DeleteView):
    model = Table_Companydetailsmaster
    success_url = reverse_lazy("main:company_details_master")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(
            request, "Account Deleted Successfully", extra_tags="form_delete"
        )
        return HttpResponseRedirect(success_url)


from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.db import IntegrityError
from .models import Table_Companydetailsmaster
from .forms import ComapnyDetailsMasterForm

class EditCompanyMasterUserView(LoginRequiredMixin, UpdateView):
    model = Table_Companydetailsmaster
    form_class = ComapnyDetailsMasterForm
    template_name = "accounts/company-master/companydetailsmaster.html"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Account edited successfully!")
            return response
        except IntegrityError:
            form.add_error(
                "company_id", "This Company ID already exists. Please choose a different one."
            )
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            "main:companymaster_detail", kwargs={"slug": self.object.slug}
        )

# branch Create View
def branch_create(request):
    if request.method == 'POST':
        branch_name = request.POST.get('branch_name').strip().upper()
        co_id = request.POST.get('co_id').strip().upper()

        # Check if the branch name already exists
        # if Branch_master.objects.filter(branch_name=branch_name).exists():
        #     error_message = f"Branch with name '{branch_name}' already exists."
        #     return render(request, 'accounts/branch-master/branch_form.html', {'error_message': error_message})
        if branch_name:
            Branch_master.objects.create(branch_name=branch_name,co_id=co_id)
            messages.success(request, "Branch added successfully!")
            return redirect('main:branch_list')
    companies=Table_Companydetailsmaster.objects.all()
    return render(request, 'accounts/branch-master/branch_form.html',{'companies': companies,})

def branch_list(request):
    co_id = request.session.get('co_id')
    branch = request.session.get('branch')
    query = request.GET.get('q')
    if query:
        branches = Branch_master.objects.filter(branch_name__icontains=query,co_id=co_id)
    else:
        branches = Branch_master.objects.all()
        # branches = Branch_master.objects.filter(co_id=co_id)
    return render(request, 'accounts/branch-master/branch_list.html', {'branches': branches})

def branch_readonly(request,pk):
    branch = get_object_or_404(Branch_master, pk=pk)
    return render(request, 'accounts/branch-master/branch_edit.html', {'branch': branch})

# Update View
def branch_update(request, pk):
    branch = get_object_or_404(Branch_master, pk=pk)
    if request.method == 'POST':
        co_id = request.POST.get('co_id')
        branch_name = request.POST.get('branch_name')
        # if co_id:
        branch.co_id = co_id
        # if branch_name:
        branch.branch_name = branch_name
        branch.save()
        return redirect('main:branch_list')
    companies = Table_Companydetailsmaster.objects.all()
    return render(request, 'accounts/branch-master/branch_form.html', {'branch': branch,'companies': companies})

# Delete View
def branch_delete(request, pk):
    branch = get_object_or_404(Branch_master, pk=pk)
    if request.method == 'POST':
        branch.delete()
        return redirect('main:branch_list')
    return render(request, 'accounts/branch-master/branch_confirm_delete.html', {'branch': branch})








# -------------------------------       BILL       ---------------------------------------





from datetime import date
from .models import Table_Acntchild

def bill_details(request):
    co_id = request.session.get('co_id')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'go':
            series=request.POST.get('series')
            entry_number=request.POST.get('entry_number')
            bill_date=request.POST.get('bill_date')
            bill_type=request.POST.get('bill_type')
            customer_name=request.POST.get('customer_name')
            customer_id=request.POST.get('customer_id')
            address=request.POST.get('address')
            rate_type = request.POST.get('rate_type')
            gst=request.POST.get('gst')
            from_date=request.POST.get('from_date')
            to_date=request.POST.get('to_date')

            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()

            # voucher_conf = VoucherConfiguration.objects.get(category='Trip sheet', id=series, serial_no=entry_number)
            account_master = Table_Accountsmaster.objects.get(user=request.user, head=customer_name, account_code=customer_id)
            trips = Trip_sheet.objects.filter(account_code=customer_id, customer_name=account_master, rate_type=rate_type, loading_date__range=(from_date_obj, to_date_obj))
            vouchers = VoucherConfiguration.objects.filter(category='Sales')
            customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
            company = Table_Companydetailsmaster.objects.get(company_id=co_id)

            context = {
                'account_master': account_master,
                'vouchers': vouchers,
                'customers': customers,
                'trips': trips,
                'series': series,
                'entry_number': entry_number,
                'bill_date': bill_date,
                'bill_type': bill_type,
                'customer_name': customer_name,
                'customer_id': customer_id,
                'address': address,
                'rate_type': rate_type,
                'gst': gst,
                'from_date': from_date,
                'to_date': to_date,
                'today_date': date.today().isoformat(),
                'prefill': True,
                'company': company,
            }
            return render(request, 'bill_details/bill_details.html', context)
        
        elif action == 'save' or action == 'print':
            trips_id = request.POST.getlist('trip_id[]')
            user = request.user
            series_id = request.POST.get('series')
            bill_no = request.POST.get('entry_number')
            bill_date = request.POST.get('bill_date')
            gst_type = request.POST.get('gst_type')
            bill_type = request.POST.get('bill_type')
            customer_id = request.POST.get('customer_id')
            customer_name = request.POST.get('customer_name')
            date_from = request.POST.get('from_date')
            date_to = request.POST.get('to_date')
            rate_type = request.POST.get('rate_type')
            sp_disc_perc = request.POST.get('sp_disc_percent')
            sp_disc_amt = request.POST.get('sp_disc_amt')
            round_off = request.POST.get('round_off')
            total_km = request.POST.get('total_km')
            total_gross = request.POST.get('total_gross')
            amt_before_tax = request.POST.get('net_total')
            cgst = request.POST.get('cgst')
            sgst = request.POST.get('sgst')
            igst = request.POST.get('igst')
            total_discounts = request.POST.get('total_discounts')
            grand_total = request.POST.get('grand_total')

            try:
                company = Table_Companydetailsmaster.objects.get(company_id=co_id)
                branch = Branch_master.objects.get(branch_name=(request.session.get('branch')))
                fy_code = request.session.get('fycode')
                series = VoucherConfiguration.objects.get(id=series_id)
                customer = Table_Accountsmaster.objects.get(user=user, head=customer_name, account_code=customer_id)
                sales_acc = Table_Accountsmaster.objects.filter(head='SALES ACCOUNT', user__company=company).first()
                sales_account = Table_Acntchild.objects.filter(account_master=sales_acc).first()
                cashbook_master = Table_Accountsmaster.objects.filter(category='Cashbook', user__company=company).first()
                cashbook = Table_Acntchild.objects.get(account_master=cashbook_master)
                customer_credit = Table_Acntchild.objects.get(account_master=customer)
                cgst_master = Table_Accountsmaster.objects.filter(head='CGST', user__company=company).first()
                sgst_master = Table_Accountsmaster.objects.filter(head='SGST', user__company=company).first()
                igst_master = Table_Accountsmaster.objects.filter(head='IGST', user__company=company).first()
                cgst_account = Table_Acntchild.objects.get(account_master=cgst_master)
                sgst_account = Table_Acntchild.objects.get(account_master=sgst_master)
                igst_account = Table_Acntchild.objects.get(account_master=igst_master)
                round_off_master = Table_Accountsmaster.objects.filter(head='ROUND OFF', user__company=company).first()
                round_off_acc = Table_Acntchild.objects.get(account_master=round_off_master)
                discount_master = Table_Accountsmaster.objects.filter(head='DISCOUNT ALLOWED', user__company=company).first()
                discount_acc = Table_Acntchild.objects.get(account_master=discount_master)

                master = Table_BillMaster.objects.create(
                    user = user, 
                    company = company,
                    branch = branch,
                    fy_code = fy_code,
                    series = series,
                    bill_no = bill_no, 
                    bill_date = bill_date,
                    gst_type = gst_type,
                    bill_type = bill_type,
                    customer=customer, 
                    date_from = date_from, 
                    date_to = date_to, 
                    rate_type = rate_type,
                    sp_disc_perc = sp_disc_perc, 
                    sp_disc_amt = sp_disc_amt,
                    round_off = round_off, 
                    total_km = total_km,
                    total_gross = total_gross, 
                    amt_before_tax = amt_before_tax, 
                    cgst = cgst, 
                    sgst = sgst, 
                    igst = igst, 
                    total_discounts = total_discounts,
                    grand_total = grand_total
                )
                try:
                    net_values = request.POST.getlist('net_values[]')
                    freight_charges = request.POST.getlist('freight_charges[]')
                    for index, trips in enumerate(trips_id):
                        trip = get_object_or_404(Trip_sheet, id=trips)
                        km_rate = request.POST.get(f'km_rate_{trips}')
                        ehr_rate = request.POST.get(f'extra_hour_rate_{trips}')
                        toll_parking = request.POST.get(f'toll_parking_{trips}')
                        haulting = request.POST.get(f'haulting_{trips}')
                        net_value = net_values[index] 
                        gross_amount = freight_charges[index]

                        Table_BillItems.objects.create(
                            master=master, 
                            trip=trip, 
                            code=trip.entry_number, 
                            vehicle_no=trip.vehicle_number_id.registration_number,
                            vehicle_type=trip.vehicle_type_id.vehicle_name,
                            total_km=trip.total_km,
                            km_rate=km_rate, 
                            ehr_rate=ehr_rate, 
                            fixed_charge=trip.fixed_charge_total, 
                            toll_parking=toll_parking, 
                            haulting=haulting, 
                            monthly_fixed_charge=0.00, 
                            tax=trip.customer_name.tax, 
                            gross_amount=gross_amount, 
                            net_value=net_value 
                        )
                    series.serial_no = series.serial_no +  1
                    series.save()
                    sales_account.current_balance = float(sales_account.current_balance) +float(amt_before_tax)
                    sales_account.save()

                    if bill_type == 'Cash':
                        cashbook.current_balance = float(cashbook.current_balance) + float(grand_total)
                        cashbook.save()
                        print('cashbook current balance updated...!!')
                    elif bill_type == 'Credit':
                        customer_credit.current_balance = float(customer_credit.current_balance) + float(grand_total)
                        customer_credit.save()
                        print('customer credit current balance updated...!!')

                    if gst_type == 'gst':
                        cgst_account.current_balance = float(cgst_account.current_balance) + float(cgst)
                        sgst_account.current_balance = float(sgst_account.current_balance) + float(sgst)
                        cgst_account.save()
                        sgst_account.save()
                    elif gst_type == 'igst':
                        igst_account.current_balance = float(igst_account.current_balance) + float(igst)
                        igst_account.save()

                    if  float(total_discounts) > 0.00:
                        discount_acc.current_balance = float(discount_acc.current_balance) + float(total_discounts)
                        discount_acc.save()

                    if float(round_off) != 0.00:
                        round_off_acc.current_balance = float(round_off_acc.current_balance) + float(round_off)
                        round_off_acc.save()

                    vouchers = VoucherConfiguration.objects.filter(category='Sales', company__company_id=co_id)
                    customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
                    context = {
                        'vouchers': vouchers,
                        'customers': customers,
                        'status': 'success',
                        'print': True if action == 'print' else False,
                        'master': master,
                        'children': Table_BillItems.objects.filter(master=master),
                    }
                    return render(request, 'bill_details/bill_details.html', context)


                except Exception as e:
                    print(e)
                    vouchers = VoucherConfiguration.objects.filter(category='Sales', company__company_id=co_id)
                    customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
                    context = {
                        'vouchers': vouchers,
                        'customers': customers,
                        'status': 'error'
                    }
                    return render(request, 'bill_details/bill_details.html', context)
            except Exception as e:
                print(e)
                vouchers = VoucherConfiguration.objects.filter(category='Sales', company__company_id=co_id)
                customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
                context = {
                    'vouchers': vouchers,
                    'customers': customers,
                    'status': 'error'
                }
                return render(request, 'bill_details/bill_details.html', context)

        else:
            vouchers = VoucherConfiguration.objects.filter(category='Sales', company__company_id=co_id)
            customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
            company = Table_Companydetailsmaster.objects.get(company_id=co_id)
            context = {
                'vouchers': vouchers,
                'customers': customers,
                'company': company,
            }
            return render(request, 'bill_details/bill_details.html', context)
        
    vouchers = VoucherConfiguration.objects.filter(category='Sales', company__company_id=co_id)
    customers = Table_Accountsmaster.objects.filter(user__username=request.user.username)
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    context = {
        'vouchers': vouchers,
        'customers': customers,
        'company': company,
    }
    return render(request, 'bill_details/bill_details.html', context)

def get_serial_number(request):
    series_id = request.GET.get('series_id')
    try:
        voucher = VoucherConfiguration.objects.get(id=series_id, category='Sales')
        return JsonResponse({'serial_no': voucher.serial_no})
    except VoucherConfiguration.DoesNotExist:
        return JsonResponse({'error': 'Invalid series selected'}, status=400)
    
from django.db.models import Q
def autocomplete_customers(request):
    if request.GET.get('term'):
        term = request.GET.get('term')
        results = Table_Accountsmaster.objects.filter(
            Q(head__icontains=term),
            Q(category__in=['Customers', 'Suppliers']),
            Q(group__in=['SUNDRY DEBTORS', 'SUNDRY CREDITORS'])
        )[:10]
        data = [{'label': x.head, 
                 'value': x.head, 
                 'account_code': x.account_code, 
                 'address': x.address1,
                 'gstno': x.gstno,
                 } for x in results]
        for x in results:
            print(x.gstno)
        return JsonResponse(data, safe=False)

def bill_search(request):
    series_ids = Table_BillMaster.objects.filter(user=request.user, series__category='Sales').values_list('series', flat=True).distinct()
    series = VoucherConfiguration.objects.filter(id__in=series_ids)

    if request.method == 'POST':
        series_id = request.POST.get('series')
        bill_no = request.POST.get('entry_number')

        try:
            seriess = VoucherConfiguration.objects.filter(id=series_id).first()
            bill = Table_BillMaster.objects.filter(bill_no=bill_no, series=seriess).first()
            return redirect('main:bill_edit', bill_id=bill.id)               
        except Exception as e:
            print(e)
            series_ids = Table_BillMaster.objects.filter(user=request.user, series__category='Sales').values_list('series', flat=True).distinct()
            series = VoucherConfiguration.objects.filter(id__in=series_ids)
            return render(request, "bill_details/bill_search.html", {'error': 'No bill found for your bill number and series', 'series': series})

    context = {      
        'series': series,                                  
    }
    return render(request, "bill_details/bill_search.html", context)

def bill_edit(request, bill_id):
    co_id = request.session.get('co_id')
    bill_master  = Table_BillMaster.objects.filter(id=bill_id).first()
    trips = Table_BillItems.objects.filter(master=bill_master)
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    sp_disc_amt = bill_master.sp_disc_amt or 0
    sp_disc_perc = bill_master.sp_disc_perc or 0
    grand_total = bill_master.grand_total

    # Reverse the discount calculation
    base_amount = (grand_total + sp_disc_amt) / (1 - (sp_disc_perc / 100)) if sp_disc_perc else (grand_total + sp_disc_amt)

    bill_master.original_total = round(base_amount, 2)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'save':
            bill_type=request.POST.get('bill_type')
            sp_disc_percent = request.POST.get('sp_disc_percent')
            sp_disc_amt = request.POST.get('sp_disc_amt')
            round_off = request.POST.get('round_off')
            net_total = request.POST.get('net_total')
            total_discounts = request.POST.get('total_discounts')
            cgst = request.POST.get('cgst')
            sgst = request.POST.get('sgst')
            igst = request.POST.get('igst')
            grand_total = request.POST.get('grand_total')

            try:
                sales_acc = Table_Accountsmaster.objects.filter(head='SALES ACCOUNT', user__company=company).first()
                sales_account = Table_Acntchild.objects.filter(account_master=sales_acc).first()
                cashbook_master = Table_Accountsmaster.objects.filter(category='Cashbook', user__company=company).first()
                cashbook = Table_Acntchild.objects.get(account_master=cashbook_master)
                customer_credit = Table_Acntchild.objects.get(account_master=bill_master.customer)
                cgst_master = Table_Accountsmaster.objects.filter(head='CGST', user__company=company).first()
                sgst_master = Table_Accountsmaster.objects.filter(head='SGST', user__company=company).first()
                igst_master = Table_Accountsmaster.objects.filter(head='IGST', user__company=company).first()
                cgst_account = Table_Acntchild.objects.get(account_master=cgst_master)
                sgst_account = Table_Acntchild.objects.get(account_master=sgst_master)
                igst_account = Table_Acntchild.objects.get(account_master=igst_master)
                round_off_master = Table_Accountsmaster.objects.filter(head='ROUND OFF', user__company=company).first()
                round_off_acc = Table_Acntchild.objects.get(account_master=round_off_master)
                discount_master = Table_Accountsmaster.objects.filter(head='DISCOUNT ALLOWED', user__company=company).first()
                discount_acc = Table_Acntchild.objects.get(account_master=discount_master)

                sales_account.current_balance = float(sales_account.current_balance) - float(bill_master.amt_before_tax)
                sales_account.current_balance = float(sales_account.current_balance) + float(net_total)
                sales_account.save()
                round_off_acc.current_balance = float(round_off_acc.current_balance) - float(bill_master.round_off)
                round_off_acc.current_balance = float(round_off_acc.current_balance) + float(round_off)
                round_off_acc.save()
                discount_acc.current_balance = float(discount_acc.current_balance) - float(bill_master.total_discounts)
                discount_acc.current_balance = float(discount_acc.current_balance) + float(total_discounts)
                discount_acc.save()

                try:
                    if bill_type == 'Cash' and bill_master.bill_type =='Cash':
                        cashbook.current_balance = float(cashbook.current_balance) - float(bill_master.grand_total)
                        cashbook.current_balance = float(cashbook.current_balance) + float(grand_total)
                        cashbook.save()
                        print('same cash on cashbook current balance updated')

                    elif bill_type == 'Credit' and bill_master.bill_type =='Credit':
                        customer_credit.current_balance = float(customer_credit.current_balance) - float(bill_master.grand_total)
                        customer_credit.current_balance = float(customer_credit.current_balance) + float(grand_total)
                        customer_credit.save()
                        print('same Credit on customer current balance updated')
                    
                    elif bill_type == 'Cash' and bill_master.bill_type == "Credit":
                        customer_credit.current_balance = float(customer_credit.current_balance) - float(bill_master.grand_total)
                        customer_credit.save()
                        cashbook.current_balance = float(cashbook.current_balance) + float(grand_total)
                        cashbook.save()
                        print('bill type is cash but bill master was Credit so cashbook current balance updated')

                    elif bill_type == 'Credit' and bill_master.bill_type =='Cash':
                        cashbook.current_balance = float(cashbook.current_balance) - float(bill_master.grand_total)
                        cashbook.save()
                        customer_credit.current_balance = float(customer_credit.current_balance) + float(grand_total)
                        customer_credit.save()
                        print('bill type is Credit but bill master was cash so on customer current balance updated')

                    if bill_master.gst_type == 'gst':
                        cgst_account.current_balance = float(cgst_account.current_balance) - float(bill_master.cgst)
                        cgst_account.current_balance = float(cgst_account.current_balance) + float(cgst)
                        sgst_account.current_balance = float(sgst_account.current_balance) - float(bill_master.sgst)
                        sgst_account.current_balance = float(sgst_account.current_balance) + float(sgst)
                        cgst_account.save()
                        sgst_account.save()
                    elif bill_master.gst_type == 'igst':
                        igst_account.current_balance = float(igst_account.current_balance) - float(bill_master.igst)
                        igst_account.current_balance = float(igst_account.current_balance) + float(igst)
                        igst_account.save()

                except Exception as e:
                    print(e)
                    context = {
                        'bill_master': bill_master,
                        'trips': trips,
                        'company': company,
                        'status': 'error'
                    }
                    return render(request, 'bill_details/bill_edit.html', context)

                bill_master.bill_type = bill_type
                bill_master.sp_disc_perc = sp_disc_percent
                bill_master.sp_disc_amt = sp_disc_amt
                bill_master.round_off = round_off
                bill_master.amt_before_tax = net_total
                bill_master.total_discounts = total_discounts
                bill_master.cgst = cgst
                bill_master.sgst = sgst
                bill_master.igst = igst
                bill_master.grand_total = grand_total
                try:
                    net_values = request.POST.getlist('net_values[]')
                    freight_charges = request.POST.getlist('freight_charges[]')
                    bills_id = request.POST.getlist('trip_id[]')

                    for index, trips in enumerate(bills_id):
                        bill_item = get_object_or_404(Table_BillItems, id=trips)
                        km_rate = request.POST.get(f'km_rate_{trips}')
                        ehr_rate = request.POST.get(f'extra_hour_rate_{trips}')
                        toll_parking = request.POST.get(f'toll_parking_{trips}')
                        haulting = request.POST.get(f'haulting_{trips}')
                        gross_amount = freight_charges[index]
                        net_value = net_values[index] 
                        bill_item.km_rate = km_rate
                        bill_item.ehr_rate = ehr_rate
                        bill_item.toll_parking = toll_parking
                        bill_item.haulting = haulting
                        bill_item.gross_amount = gross_amount
                        bill_item.net_value = net_value
                        bill_item.save()
                    bill_master.save()
                    context = {
                        'bill_master': bill_master,
                        'trips': trips,
                        'company': company,
                        'status': 'success'
                    }
                    return render(request, 'bill_details/bill_edit.html', context)

                except Exception as e:
                    print(e)
                    context = {
                        'bill_master': bill_master,
                        'trips': trips,
                        'company': company,
                        'status': 'error'
                    }
                    return render(request, 'bill_details/bill_edit.html', context)
            except Exception as e:
                print(e)
                context = {
                        'bill_master': bill_master,
                        'trips': trips,
                        'company': company,
                        'status': 'error'
                    }
                return render(request, 'bill_details/bill_edit.html', context)
        
    context = {
        'bill_master': bill_master, 
        'trips': trips, 
        'company': company, 
        'bill_master.original_total': bill_master.original_total
    }
    return render(request, 'bill_details/bill_edit.html', context)


def bill_delete_search(request):
    series_ids = Table_BillMaster.objects.filter(user=request.user, series__category='Sales').values_list('series', flat=True).distinct()
    series = VoucherConfiguration.objects.filter(id__in=series_ids)

    if request.method == 'POST':
        series_id = request.POST.get('series')
        bill_no = request.POST.get('entry_number')

        try:
            seriess = VoucherConfiguration.objects.filter(id=series_id).first()
            bill = Table_BillMaster.objects.filter(bill_no=bill_no, series=seriess).first()
            return redirect('main:bill_delete', bill_id=bill.id)               
        except Exception as e:
            print(e)
            series_ids = Table_BillMaster.objects.filter(user=request.user, series__category='Sales').values_list('series', flat=True).distinct()
            series = VoucherConfiguration.objects.filter(id__in=series_ids)
            return render(request, "bill_details/bill_delete_search.html", {'error': 'No bill found for your bill number and series', 'series': series})

    context = {      
        'series': series,                                  
    }
    return render(request, 'bill_details/bill_delete_search.html', context)

def bill_delete(request, bill_id):
    co_id = request.session.get('co_id')
    bill_master  = Table_BillMaster.objects.filter(id=bill_id).first()
    trips = Table_BillItems.objects.filter(master=bill_master)
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel':
            return redirect('main:bill_delete_search')
        if action == 'delete':
            try:
                sales_acc = Table_Accountsmaster.objects.filter(head='SALES ACCOUNT', user__company=company).first()
                sales_account = Table_Acntchild.objects.filter(account_master=sales_acc).first()
                cashbook_master = Table_Accountsmaster.objects.filter(category='Cashbook', user__company=company).first()
                cashbook = Table_Acntchild.objects.get(account_master=cashbook_master)
                customer_credit = Table_Acntchild.objects.get(account_master=bill_master.customer)
                cgst_master = Table_Accountsmaster.objects.filter(head='CGST', user__company=company).first()
                sgst_master = Table_Accountsmaster.objects.filter(head='SGST', user__company=company).first()
                igst_master = Table_Accountsmaster.objects.filter(head='IGST', user__company=company).first()
                cgst_account = Table_Acntchild.objects.get(account_master=cgst_master)
                sgst_account = Table_Acntchild.objects.get(account_master=sgst_master)
                igst_account = Table_Acntchild.objects.get(account_master=igst_master)
                round_off_master = Table_Accountsmaster.objects.filter(head='ROUND OFF', user__company=company).first()
                round_off_acc = Table_Acntchild.objects.get(account_master=round_off_master)
                discount_master = Table_Accountsmaster.objects.filter(head='DISCOUNT ALLOWED', user__company=company).first()
                discount_acc = Table_Acntchild.objects.get(account_master=discount_master)

                round_off_acc.current_balance = float(round_off_acc.current_balance) - float(bill_master.round_off)
                round_off_acc.save()
                discount_acc.current_balance = float(discount_acc.current_balance) - float(bill_master.total_discounts)
                discount_acc.save()

                if bill_master.bill_type == 'Cash':
                    cashbook.current_balance = float(cashbook.current_balance) - float(bill_master.grand_total)
                    cashbook.save()
                    print('cashbook amount deducted')
                elif bill_master.bill_type == 'Credit':
                    customer_credit.current_balance = float(customer_credit.current_balance) - float(bill_master.grand_total)
                    customer_credit.save()
                    print('customer credit amount deducted')

                if bill_master.gst_type == 'gst':
                    cgst_account.current_balance = float(cgst_account.current_balance) - float(bill_master.cgst)
                    sgst_account.current_balance = float(sgst_account.current_balance) - float(bill_master.sgst)
                    cgst_account.save()
                    sgst_account.save()
                elif bill_master.gst_type == 'igst':
                    igst_account.current_balance = float(igst_account.current_balance) - float(bill_master.igst)
                    igst_account.save()

                sales_account.current_balance = float(sales_account.current_balance) - float(bill_master.amt_before_tax)
                sales_account.save()
                bill_master.delete()
                return render(request, 'bill_details/bill_delete.html', {'status': 'success'})
            except Exception as e:
                print(e)
                return render(request, 'bill_details/bill_delete.html', {'status': 'error'})

    context = {
        'bill_master': bill_master, 
        'trips': trips, 
        'company': company
    }
    return render(request, 'bill_details/bill_delete.html', context)









# ------------------------       Reports       ----------------------------

from urllib.parse import urlencode
from django.urls import reverse
from django.db.models import Sum

def bill_report_search(request):
    customers = Table_BillMaster.objects.filter(customer__isnull=False).values('customer_id', 'customer__head').distinct()
    today = date.today().isoformat()

    if request.method == 'POST':
        customer = request.POST.get('customer')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')

        # Only redirect if at least one field is filled
        if customer or (date_from and date_to):
            params = {}
            if customer:
                params['customer'] = customer
            if date_from:
                params['date_from'] = date_from
            if date_to:
                params['date_to'] = date_to

            return redirect(f"{reverse('main:bill_wise_report')}?{urlencode(params)}")

        else:
            return render(request, 'reports/bill_wise_report/bill_report_search.html', {
                'customers': customers,
                'today': today,
                'error': 'Please input any field'
            })

    return render(request, 'reports/bill_wise_report/bill_report_search.html', {
        'customers': customers,
        'today': today
    })

def bill_wise_report(request):
    co_id = request.session.get('co_id')
    customer = request.GET.get('customer')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    bills = Table_BillMaster.objects.all()
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    customer = Table_Accountsmaster.objects.filter(id=customer).first()

    if customer and date_from and date_to:
        bills = bills.filter(customer=customer, bill_date__range=[date_from, date_to])
    elif customer:
        bills = bills.filter(customer=customer)
    elif date_from and date_to:
        bills = bills.filter(bill_date__range=[date_from, date_to])

    gross_total = bills.aggregate(total=Sum('amt_before_tax'))['total'] or 0
    grand_value = bills.aggregate(total=Sum('grand_total'))['total'] or 0


    context = {
        'bills': bills, 
        'company':company, 
        'customer': customer, 
        'grand_value': grand_value, 
        'gross_total': gross_total
    }

    return render(request, 'reports/bill_wise_report/bill_wise_report.html', context)




#report
def trip_sheet_date_wise(request):
    return render(request,'reports/trip_sheet_report/date_wise_tripsheet.html')

from datetime import datetime

def trip_sheets_by_loading_date(request):
    from_date = request.GET.get('trip_date_from')
    to_date = request.GET.get('trip_date_to')
    trip_sheets = []

    co_id = request.session.get('co_id')  # Get logged-in company ID
    company_name = None
    if co_id:
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=co_id)
            print(company)
            company_name = company.companyname 
        except Table_Companydetailsmaster.DoesNotExist:
            company_name = "Unknown Company"

    if from_date and to_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            trip_sheets = Trip_sheet.objects.filter(
                loading_date__range=(from_date_obj, to_date_obj)
            ).order_by('loading_date')
            print(trip_sheets)
        except ValueError:
            pass  # Optional: handle invalid date input
    total_freight = sum(sheet.total_freight_charges for sheet in trip_sheets)
    total_driver_bata = sum(sheet.driver_bata for sheet in trip_sheets)


    return render(request, 'reports/trip_sheet_report/date_wise_report.html', {
        'trip_sheets': trip_sheets,
        'from_date': from_date,
        'to_date': to_date,
        'company_name':company_name,
        'total_freight': total_freight,
        'total_driver_bata': total_driver_bata,
    })
from datetime import date
def trip_sheet_driver_wise(request):
    drivers = Employee_master.objects.all()
    today = date.today().isoformat()
    return render(request,'reports/trip_sheet_report/driver_wise_tripsheet.html',{'drivers':drivers,'today': today,})


def trip_sheets_driver_loading_date(request):
    trip_date_from = request.GET.get('trip_date_from')
    trip_date_to = request.GET.get('trip_date_to')
    driver_id = request.GET.get('driver_id')
    trip_sheets = []
   
    co_id=request.session.get('co_id')
    company_name=None
    if co_id:
        company= Table_Companydetailsmaster.objects.get(company_id=co_id)
        company_name= company.companyname
    if driver_id:
        trip_sheet = Trip_sheet.objects.filter(driver_name_id=driver_id).first()
        # if trip_sheet and trip_sheet.driver_name_id:
        driver_name = trip_sheet.driver_name_id.employee_name
   
    if driver_id and trip_date_from and trip_date_to:
        trip_sheets = Trip_sheet.objects.filter(
            driver_name_id=driver_id,
            loading_date__range=[trip_date_from, trip_date_to]
        ).order_by('loading_date')  # Optional: sort by date
    
    driver_advance_total=sum(sheet.advance_driver for sheet in trip_sheets)
    driver_bata_total=sum(sheet.driver_bata  for sheet in trip_sheets)
    total_freight_charges = sum(sheet.total_freight_charges for sheet in trip_sheets)
    balance_amount = driver_bata_total - driver_advance_total
    context = {
       

        'trip_sheets': trip_sheets, 'company_name':company_name,'driver_name':driver_name,'driver_advance_total':driver_advance_total,'driver_bata_total':driver_bata_total,'total_freight_charges':total_freight_charges,'balance_amount': balance_amount,
    }


    return render(request, 'reports/trip_sheet_report/driver_wise_report.html',context)

def trip_sheet_vehicle_wise(request):
    vehicles = Vehicle_master.objects.all()
    today = date.today().isoformat()
    return render(request,'reports/trip_sheet_report/vehicle_wise_tripsheet.html',{'today':today,'vehicles':vehicles,})

def trip_sheets_vehicle_loading_date(request):
    trip_date_from = request.GET.get('trip_date_from')
    trip_date_to = request.GET.get('trip_date_to')
    vehicle_id = request.GET.get('vehicle_id')
    trip_sheets = []

    co_id=request.session.get('co_id')
    company_name=None

    if co_id:
        company=Table_Companydetailsmaster.objects.get(company_id=co_id)
        company_name=company.companyname
    if vehicle_id:
        tripsheet = Trip_sheet.objects.filter(vehicle_number_id=vehicle_id).first()
        vehicle = tripsheet.vehicle_number_id.registration_number

    if vehicle_id and trip_date_from and trip_date_to:
        trip_sheets=Trip_sheet.objects.filter(vehicle_number_id=vehicle_id,
            loading_date__range=[trip_date_from, trip_date_to]
        ).order_by('loading_date')

    total_km = sum(sheet.total_km for sheet in trip_sheets)
    diesel_ltr = sum(sheet.diesel_ltr for sheet in trip_sheets)
    diesel_charges = sum(sheet.diesel_charges for sheet in trip_sheets)
    statutory_charge = sum(sheet.statutory_charge for sheet in trip_sheets)
    tyre_work = sum(sheet.tyre_work for sheet in trip_sheets)
    mech_electric = sum(sheet.mech_electric for sheet in trip_sheets)
    driver_bata = sum(sheet.driver_bata for sheet in trip_sheets)
    total_freight = sum(sheet.total_freight_charges for sheet in trip_sheets)


    return render(request,'reports/trip_sheet_report/vehicle_wise_report.html',{'trip_sheets': trip_sheets,'company_name':company_name,'vehicle':vehicle,'total_km': total_km,
    'diesel_ltr': diesel_ltr,
    'diesel_charges': diesel_charges,
    'statutory_charge': statutory_charge,
    'tyre_work': tyre_work,
    'mech_electric': mech_electric,
    'driver_bata': driver_bata,
    'total_freight': total_freight,
    'from_date': trip_date_from,
     'to_date': trip_date_to,})

def trip_sheet_customer_wise(request):
    today = date.today().isoformat()
    return render(request,'reports/trip_sheet_report/customer_wise_tripsheet.html',{'today':today,})

from django.http import JsonResponse
from .models import Table_Accountsmaster

def get_customers(request):
    q = request.GET.get('q', '')
    results = Table_Accountsmaster.objects.filter(head__icontains=q).values('head', 'account_code')[:10]
    data = [{'name': item['head'], 'account_code': item['account_code']} for item in results]
    return JsonResponse(data, safe=False)

def trip_sheets_customer_loading_date(request):
    trip_date_from = request.GET.get('trip_date_from')
    trip_date_to = request.GET.get('trip_date_to')
    customer_name = request. GET.get('customer')
    trip_sheets = []

    co_id = request.session.get('co_id')
    company=Table_Companydetailsmaster.objects.get(company_id=co_id)
    company_name = company.companyname

    if customer_name and trip_date_from and trip_date_to:
        trip_sheets = Trip_sheet.objects.filter(loading_date__range=[trip_date_from,trip_date_to],customer_name__head__icontains=customer_name)

    # print('trip:', trip_sheets)

    total_km = sum(sheet.total_km for sheet in trip_sheets)
    toll_parking_total = sum(sheet.toll_parking_total for sheet in trip_sheets)
    km_charge_total = sum(sheet.km_charge_total for sheet in trip_sheets)
    haulting_charge_total = sum(sheet.haulting_charge_total for sheet in trip_sheets)
    extra_hour_charge_total = sum(sheet.extra_hour_charge_total for sheet in trip_sheets)
    fixed_charge_total = sum(sheet.fixed_charge_total for sheet in trip_sheets)
    total_freight_charges = sum(sheet.total_freight_charges for sheet in trip_sheets )

    context = {'trip_sheets':trip_sheets,'trip_date_from':trip_date_from,'trip_date_to':trip_date_to,'customer_name':customer_name,
    'company_name':company_name,'total_km':total_km,'toll_parking_total':toll_parking_total,'km_charge_total':km_charge_total,
    'haulting_charge_total':haulting_charge_total,'extra_hour_charge_total':extra_hour_charge_total,'fixed_charge_total':fixed_charge_total,
    'total_freight_charges':total_freight_charges}

    return render(request,'reports/trip_sheet_report/customer_wise_report.html',context)


# ------------------------------------- ACCOUNTS MAPPING ----------------------------------

from .models import Table_FormattedConfig, Table_Mapping

def formatted_config(request):
    co_id = request.session.get('co_id')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    head = ['CASH', 'DISCOUNT ALLOWED', 'ROUND OFF', 'SALES', 'CGST', 'SGST', 'IGST']
    sales_datas = Table_Accountsmaster.objects.filter(user__company__company_id=co_id, head__in=head)
    vdb_fields = {
        'CASH': 'amt_before_tax', 
        'DISCOUNT ALLOWED': 'total_discounts', 
        'ROUND OFF': 'round_off', 
        'SALES': 'grand_total', 
        'CGST': 'cgst',
        'SGST': 'sgst',
        'IGST': 'igst'
    }
    try:

        # ------------------------- SALES -------------------------

        for data in sales_datas:
            if not Table_FormattedConfig.objects.filter(
                company=company, 
                account_master=data, 
                vconfiq_value=data.head,
                vdb_field=vdb_fields.get(data.head, ''),
                form_name='SALES'
            ).exists():
                sales_master = Table_FormattedConfig.objects.create(
                    company=company, 
                    account_master=data, 
                    iform_id=1,
                    form_name='SALES', 
                    vconfiq_value=data.head,
                    vdb_field=vdb_fields.get(data.head, '')
                )
                if not Table_Mapping.objects.filter(
                    iconfiq_id=sales_master.id,
                    iacc_id=data.account_code,
                    drcr=data.debitcredit
                ).exists():
                    Table_Mapping.objects.create(
                        master=sales_master, 
                        iconfiq_id=sales_master.id,
                        iacc_id=data.account_code,
                        drcr=data.debitcredit
                    )
        print('sales data created succesfully')

        # ------------------------------ SALES RETURN -------------------------

        for data in sales_datas:
            if not Table_FormattedConfig.objects.filter(
                company=company, 
                account_master=data, 
                vconfiq_value=data.head,
                vdb_field=vdb_fields.get(data.head, ''),
                form_name='SALES RETURN'
            ).exists():
                sales_return_master = Table_FormattedConfig.objects.create(
                    company=company, 
                    account_master=data, 
                    iform_id=2,
                    form_name='SALES RETURN', 
                    vconfiq_value=data.head,
                    vdb_field=vdb_fields.get(data.head, '')
                )
                if not Table_Mapping.objects.filter(
                    iconfiq_id=sales_return_master.id,
                    iacc_id=data.account_code,
                    drcr=data.debitcredit
                ).exists():
                    Table_Mapping.objects.create(
                        master=sales_return_master, 
                        iconfiq_id=sales_return_master.id,
                        iacc_id=data.account_code,
                        drcr=data.debitcredit
                    )
        print('sales return data created succesfully...!!!')
    except Exception as e:
        print(e)

    datas = Table_FormattedConfig.objects.filter(company=company)
    context = {
        'datas': datas
    }
    return render(request, 'accounts/mapping/formatted_config.html', context)


def mapping(request):
    co_id = request.session.get('co_id')
    datas = Table_Mapping.objects.filter(master__company__company_id=co_id)
    return render(request, 'accounts/mapping/mapping.html', {'datas': datas})






# ------------------------------------ ACCOUNTS TAX MASTER  ----------------------------------------------
from .models import TaxMaster

def add_tax(request):
    if request.method == "POST":
        co_id = request.session.get('co_id')
        branch = request.session.get('branch')
        category = request.POST.get('category')
        tax_category = request.POST.get('tax_category')
        tax_type = request.POST.get('tax_type')
        tax_perc = request.POST.get('tax_perc')
        account_head = request.POST.get('account_head')
        group_under = request.POST.get('group_under')

        company = Table_Companydetailsmaster.objects.get(company_id=co_id)
        company_child = Table_companyDetailschild.objects.get(company_id=company)
        account_code = Table_Accountsmaster.objects.filter(user__company__company_id=co_id).aggregate(Max('account_code'))['account_code__max']

        try:
            account_master = Table_Accountsmaster(
                company=company,
                branch=Branch_master.objects.get(branch_name=request.session.get('branch')),
                user=request.user,
                account_code=account_code + 1,
                head=account_head,
                category='Accounts',
                group=group_under,
                debitcredit='Debit'
            )
            account_master._fycode = request.session.get('fycode')
            account_master.save()

            TaxMaster.objects.create(
                company=company,
                master=account_master,
                category=category,
                tax_type=tax_type,
                tax_perc=tax_perc, 
                account_head=account_head,
                account_code=account_code + 1,
                tax_category=tax_category,
                co_id=co_id,
                fy_code=company_child.fycode,
                status='Y'
            )

            return render(request, 'accounts/tax/add_tax.html', {'success': 'success'})
        except Exception as error:
            print(error)
            return render(request, 'accounts/tax/add_tax.html', {'error': error})

    return render(request, 'accounts/tax/add_tax.html')

def tax_list(request):
    co_id = request.session.get('co_id')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)

    tax_master = TaxMaster.objects.filter(company=company)
    return render(request, 'accounts/tax/tax_list.html', {'tax_master': tax_master})







# --------------------------------------------GODOWN MASTER-----------------------------------------

from .models import GodownMaster

def new_godown(request):
    if request.method == 'POST':
        co_id = request.session.get('co_id')
        godown = request.POST.get('godown')

        company = Table_Companydetailsmaster.objects.get(company_id=co_id)

        if GodownMaster.objects.filter(company=company, godown=godown).exists():
            return render(request, 'accounts/godown_master/new_godown.html', {'error': 'godown already exist'})

        try:
            GodownMaster.objects.create(
                company=company, 
                godown=godown
            )
            return render(request, 'accounts/godown_master/new_godown.html', {'success': 'success'})
        except Exception as error:
            print(error)
            return render(request, 'accounts/godown_master/new_godown.html', {'error': error})
    return render(request, 'accounts/godown_master/new_godown.html')


def godown_list(request):
    co_id = request.session.get('co_id')
    godowns = GodownMaster.objects.filter(company__company_id=co_id)
    return render(request, 'accounts/godown_master/godown_list.html', {'godowns': godowns})

def edit_godown(request, godown_id):
    godown = GodownMaster.objects.get(id=godown_id)
    if request.method == 'POST':
        godown_name = request.POST.get('godown_name')
        godown.godown = godown_name
        godown.save()
        return render(request, 'accounts/godown_master/edit_godown.html', {'success': 'success', 'godown': godown})
    return render(request, 'accounts/godown_master/edit_godown.html', {'godown': godown})

def delete_godown(request, godown_id):
    godown = GodownMaster.objects.get(id=godown_id)
    godown.delete()
    return redirect('main:godown_list')




# --------------------------------------------GROUP MASTER-----------------------------------------

from .models import GroupMaster

def new_group(request):
    co_id = request.session.get('co_id')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    primary_groups = GroupMaster.objects.filter(company__company_id=co_id, primary_group='Y')

    if request.method == 'POST':
        group = request.POST.get('group')
        primary_group = request.POST.get('primary_group')
        group_under = request.POST.get('group_under')

        try:
            GroupMaster.objects.create(company=company, 
                                       item_group=group, 
                                       item_subgroup=group_under, 
                                       primary_group=primary_group)
            return render(request, 'accounts/group_master/new_group.html', {'primary_groups': primary_groups, 'success': 'success'})
        except Exception as e:
            print(e)
            return render(request, 'accounts/group_master/new_group.html', {'primary_groups': primary_groups, 'error': e})
        
    return render(request, 'accounts/group_master/new_group.html', {'primary_groups': primary_groups})

def group_list(request):
    group = GroupMaster.objects.all()
    return render(request, 'accounts/group_master/group_list.html', {'group': group})

def group_edit(request, group_id):
    co_id = request.session.get('co_id')
    group = GroupMaster.objects.get(id=group_id)
    primary_groups = GroupMaster.objects.filter(company__company_id=co_id, primary_group='Y').exclude(id=group_id)

    if request.method == 'POST':
        group_item = request.POST.get('group')
        primary_group = request.POST.get('primary_group')
        group_under = request.POST.get('group_under')

        group.item_group = group_item
        group.primary_group = primary_group
        group.item_subgroup = group_under
        group.save()
        return render(request, 'accounts/group_master/group_edit.html', {'group': group, 'primary_groups': primary_groups, 'success': 'success'})


    return render(request, 'accounts/group_master/group_edit.html', {'group': group, 'primary_groups': primary_groups,})

def group_delete(request, group_id):
    group = GroupMaster.objects.get(id=group_id)
    group.delete()
    return redirect('main:group_list')




# --------------------------------------------UNIT MASTER-----------------------------------------


from .models import UnitMaster

def add_unit(request):
    co_id = request.session.get('co_id')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    if request.method == 'POST':
        unit = request.POST.get('unit')
        subunit = request.POST.get('subunit')
        conv_factor = request.POST.get('conv_factor')

        if UnitMaster.objects.filter(company=company, unit=unit).exists():
            return render(request, 'accounts/unit_master/add_unit.html', {'error': 'unit already exist'})
        
        try:
            UnitMaster.objects.create(company=company, unit=unit, subunit=subunit, conv_factor=conv_factor)
            return render(request, 'accounts/unit_master/add_unit.html', {'success': 'success'})
        except Exception as error:
            print(error)
            return render(request, 'accounts/unit_master/add_unit.html', {'error': error})
    return render(request, 'accounts/unit_master/add_unit.html')

def unit_list(request):
    co_id = request.session.get('co_id')
    company = Table_Companydetailsmaster.objects.get(company_id=co_id)
    units = UnitMaster.objects.filter(company=company)
    return render(request, 'accounts/unit_master/unit_list.html', {'units': units})

def unit_edit(request, unit_id):
    unit = UnitMaster.objects.get(id=unit_id)
    if request.method == 'POST':
        unit_name = request.POST.get('unit')
        subunit = request.POST.get('subunit')
        conv_factor = request.POST.get('conv_factor')

        unit.unit = unit_name
        unit.subunit = subunit
        unit.conv_factor = conv_factor
        unit.save()
        return render(request, 'accounts/unit_master/unit_edit.html', {'unit': unit, 'success': 'success'})
    return render(request, 'accounts/unit_master/unit_edit.html', {'unit': unit})

def unit_delete(request, unit_id):
    unit = UnitMaster.objects.get(id=unit_id)
    unit.delete()
    return redirect('main:unit_list')



















# - DEBIT NOTES

from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Table_DrCrNote, VoucherConfiguration, Table_Accountsmaster, Table_Voucher
import logging

logger = logging.getLogger(__name__)

class AccountDebitNoteView(TemplateView):
    template_name = 'accounts/debit-note/debit-note.html'
    success_url = reverse_lazy('main:account_debit_note')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series = self.kwargs.get('series')
        serial_no = self.kwargs.get('serial_no')
        co_id = self.request.session.get('co_id')
        company = Table_Companydetailsmaster.objects.get(company_id=co_id)
        
        logger.debug(f'Getting context data for series: {series}, serial_no: {serial_no}')

        context['series_options'] = VoucherConfiguration.objects.filter(category='Debit Note', company=company).values('series', 'serial_no')
        excluded_categories = ['Bank', 'Cashbook']
        head_options = Table_Accountsmaster.objects.exclude(category__in=excluded_categories).values('head', 'account_code').filter(user=self.request.user)
        context['head_options'] = head_options
        context['drcrnotes'] = Table_DrCrNote.objects.filter(ntype='D', user=self.request.user)
        context['series'] = series
        context['serial_no'] = serial_no
    
        if series and serial_no:
            matched_notes = Table_DrCrNote.objects.filter(series=series, noteno=serial_no, ntype='D', user=self.request.user)
            logger.debug(f'Matched notes: {matched_notes}')

            if matched_notes.exists():
                matched_note_dr = matched_notes.filter(dramount__gt=0).first()
                matched_note_cr = matched_notes.filter(cramount__gt=0).first()
    
                if matched_note_dr:
                    matched_note_dr_head = Table_Accountsmaster.objects.filter(user=self.request.user, account_code=matched_note_dr.accountcode).first()
                    if matched_note_dr_head:
                        matched_note_dr.head = matched_note_dr_head.head
                    matched_note_dr.ndate = matched_note_dr.ndate.strftime('%Y-%m-%d')
                    context['matched_note_dr'] = matched_note_dr
    
                if matched_note_cr:
                    matched_note_cr_head = Table_Accountsmaster.objects.filter(account_code=matched_note_cr.accountcode, user=self.request.user).first()
                    if matched_note_cr_head:
                        matched_note_cr.head = matched_note_cr_head.head
                    context['matched_note_cr'] = matched_note_cr
    
        company_details = Table_Companydetailsmaster.objects.last()
        if company_details:
            context['company_name'] = company_details.companyname
            context['address1'] = company_details.address1
            context['address2'] = company_details.address2
            context['phoneno'] = company_details.phoneno
    
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')
        date = request.POST.get('date')
        head1 = request.POST.get('head1')
        narration1 = request.POST.get('narration1')
        debit1_str = request.POST.get('debit1', '0')
        debit1 = float(debit1_str) if debit1_str else 0.0  # Convert to float with default value
        head2 = request.POST.get('head2')
        narration2 = request.POST.get('narration2')
        credit2_str = request.POST.get('credit2', '0')
        credit2 = float(credit2_str) if credit2_str else 0.0  # Convert to float with default value
    
        try:
            if series and serial_no:
                matched_notes = Table_DrCrNote.objects.filter(series=series, noteno=serial_no, user=self.request.user, ntype='D')
                if matched_notes.exists():
                    # Update existing debit and credit notes
                    dr_note = matched_notes.filter(dramount__gt=0).first()
                    cr_note = matched_notes.filter(cramount__gt=0).first()
    
                    # Update the current balance before updating the note
                    if dr_note:
                        self.update_account_balance(dr_note.accountcode, -float(dr_note.dramount))
                    if cr_note:
                        self.update_account_balance(cr_note.accountcode, float(cr_note.cramount))
    
                    # Update the note details
                    if dr_note:
                        dr_note.ndate = date
                        dr_note.accountcode = head1  # Debit account
                        dr_note.narration = narration1
                        dr_note.dramount = debit1
                        dr_note.save()
                        # Update the Account_Master table for debit
                        self.update_account_balance(head1, debit1)
                    if cr_note:
                        cr_note.ndate = date
                        cr_note.accountcode = head2  # Credit account
                        cr_note.narration = narration2
                        cr_note.cramount = credit2
                        cr_note.save()
                        # Update the Account_Master table for credit
                        self.update_account_balance(head2, -credit2)
    
                    messages.success(request, 'Debit note updated successfully.')
                else:
                    # Create new entries if no existing notes are matched
                    self.create_new_entries(request, series, date, head1, narration1, debit1, head2, narration2, credit2)
    
            else:
                # Create new entries if series and serial_no are not provided
                self.create_new_entries(request, series, date, head1, narration1, debit1, head2, narration2, credit2)
    
            return redirect(self.success_url)
    
        except Exception as e:
            messages.error(request, f'Failed to save debit note: {str(e)}')
            return redirect(self.success_url)
    

    def create_new_entries(self, request, series, date, head1, narration1, debit1, head2, narration2, credit2):
        co_id = self.request.session.get('co_id')
        company = Table_Companydetailsmaster.objects.get(company_id=co_id)
        voucher_config = VoucherConfiguration.objects.select_for_update().filter(series=series, category='Debit Note', company=company).first()

        if not voucher_config:
            messages.error(request, 'Invalid series for Debit Note.')
            return redirect(self.success_url)
        
        while Table_DrCrNote.objects.filter(user=self.request.user, series=series, noteno=voucher_config.serial_no, ntype='D').exists():
            voucher_config.serial_no += 1
    
        current_serial_no = voucher_config.serial_no
        voucher_config.serial_no += 1
        voucher_config.save()
    
        coid_entry = Table_companyDetailschild.objects.last()
        fycode_entry = Table_companyDetailschild.objects.last()
        coid = coid_entry.company_id if coid_entry else 'C'
        fycode = fycode_entry.fycode if fycode_entry else 'NON'
        user = request.user
        
        Table_DrCrNote.objects.create(
            user=user,
            company=company,
            series=series,
            ndate=date,
            noteno=current_serial_no,
            accountcode=head1,
            narration=narration1,
            dramount=debit1,
            cramount='0',
            ntype='D',
            userid=user.username,  # Correct field name
            coid=coid,
            fycode=fycode,
            brid='1'
        )
    
        Table_DrCrNote.objects.create(
            user=user,
            company=company,
            series=series,
            ndate=date,
            noteno=current_serial_no,
            accountcode=head2,
            narration=narration2,
            dramount='0',
            cramount=credit2,
            ntype='D',
            userid=user.username,  # Correct field name
            coid=coid,
            fycode=fycode,
            brid='1'
        )
    
        self.update_account_balance(head1, debit1)
        self.update_account_balance(head2, -credit2)
    
        messages.success(request, 'Debit note created successfully.')
    

    def update_account_balance(self, account_code, amount):
        accounts = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user)
    
        if accounts.exists():
            for account in accounts:
                current_balance = float(account.currentbalance or 0)
                account.currentbalance = current_balance + amount
                account.company_id = self.request.session.get("co_id")
                account.branch_id = self.request.session.get("branch")
                account.save()
        else:
            raise ValueError(f"No accounts found with account code: {account_code}")

class DeleteDebitNoteView(DeleteView):
    model = Table_DrCrNote
    success_url = reverse_lazy("main:account_debit_note")

    def get_object(self, queryset=None):
        pk1 = self.kwargs.get('pk1')
        pk2 = self.kwargs.get('pk2')

        # Fetch the object
        obj = Table_DrCrNote.objects.filter(id=pk1, noteno=pk2, user=self.request.user, ntype='D').first()
        if not obj:
            raise Http404("No Table_DrCrNote matches the given query.")
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Convert dramount and cramount to float before comparison
        dramount = float(self.object.dramount) if self.object.dramount else 0
        cramount = float(self.object.cramount) if self.object.cramount else 0

        # Update the account balance before deleting
        if dramount > 0:
            self.update_account_balance(self.object.accountcode, -dramount)
        elif cramount > 0:
            self.update_account_balance(self.object.accountcode, cramount)

        # Delete the object
        self.object.delete()

        # Optionally, handle the second object if needed
        obj2 = Table_DrCrNote.objects.filter(noteno=self.object.noteno, user=self.request.user, ntype='D').exclude(id=self.object.id).first()
        if obj2:
            dramount2 = float(obj2.dramount) if obj2.dramount else 0
            cramount2 = float(obj2.cramount) if obj2.cramount else 0
            
            if dramount2 > 0:
                self.update_account_balance(obj2.accountcode, -dramount2)
            elif cramount2 > 0:
                self.update_account_balance(obj2.accountcode, cramount2)
            obj2.delete()

        messages.success(request, "Debit note entry deleted successfully.")
        return redirect(success_url)

    def update_account_balance(self, account_code, amount):
        """Updates the current balance of the account(s) in Table_Accountsmaster."""
        accounts = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user)
    
        if accounts.exists():
            for account in accounts:
                current_balance = float(account.currentbalance or 0)
                account.currentbalance = current_balance + amount
                account.company_id = self.request.session.get("co_id")
                account.branch_id = self.request.session.get("branch")
                account.save()
        else:
            raise ValueError(f"No accounts found with account code: {account_code}")










from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .models import Table_DrCrNote

class AccountDebitTableView(LoginRequiredMixin, ListView):
    model = Table_DrCrNote
    template_name = 'accounts/debit-note/debit-table.html'
    context_object_name = 'drcrnotes'

    def get_queryset(self):
        return Table_DrCrNote.objects.filter(ntype='D', userid=self.request.user.username)

          


class SearchDebitTableView(TemplateView):
    template_name = 'accounts/debit-note/debit-search-box.html'

    def get_context_data(self, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(self.request.session.get('co_id')))
        context = super().get_context_data(**kwargs)
        context['series_options'] = VoucherConfiguration.objects.filter(category='Debit Note', company=company).values('series')
        return context

    def post(self, request, *args, **kwargs):
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')

        if series and serial_no:
            # Check if the serial number exists
            if Table_DrCrNote.objects.filter(series=series, noteno=serial_no, ntype='D', user=self.request.user).exists():
                return redirect(reverse('main:account_debit_note', kwargs={'series': series, 'serial_no': serial_no}))
            else:
                context = self.get_context_data(**kwargs)
                context['error'] = 'This serial number does not exist.'
                return render(request, self.template_name, context)
        
        context = self.get_context_data(**kwargs)
        context['error'] = 'Please enter both series and serial number.'
        return render(request, self.template_name, context)
    

class EditDebitTableView(LoginRequiredMixin, View):
    template_name = 'accounts/debit-note/edit-debit-note.html'





# - CREDIT NOTES

from django.shortcuts import redirect
from django.db import transaction
from django.contrib import messages
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .models import Table_DrCrNote, Table_Accountsmaster, VoucherConfiguration, Table_companyDetailschild

import logging
from django.utils import timezone
from django.db import transaction


class AccountCreditNoteView(TemplateView):
    template_name = 'accounts/credit-note/credit-note.html'
    success_url = reverse_lazy('main:account_credit_note')

    def get_context_data(self, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=self.request.session.get('co_id'))
        context = super().get_context_data(**kwargs)
        series = self.kwargs.get('series')
        serial_no = self.kwargs.get('serial_no')
        
        logger.debug(f'Getting context data for series: {series}, serial_no: {serial_no}')

        context['series_options'] = VoucherConfiguration.objects.filter(category='Credit Note', company=company).values('series', 'serial_no')
        excluded_categories = ['Bank', 'Cashbook']
        head_options = Table_Accountsmaster.objects.exclude(category__in=excluded_categories).values('head', 'account_code').filter(user=self.request.user)
        context['head_options'] = head_options
        context['drcrnotes'] = Table_DrCrNote.objects.filter(ntype='C', user=self.request.user)
        context['series'] = series
        context['serial_no'] = serial_no
    
        if series and serial_no:
            matched_notes = Table_DrCrNote.objects.filter(series=series, noteno=serial_no, ntype='C', user=self.request.user)
            logger.debug(f'Matched notes: {matched_notes}')

            if matched_notes.exists():
                matched_note_dr = matched_notes.filter(dramount__gt=0).first()
                matched_note_cr = matched_notes.filter(cramount__gt=0).first()
    
                if matched_note_dr:
                    matched_note_dr_head = Table_Accountsmaster.objects.filter(account_code=matched_note_dr.accountcode, user=self.request.user).first()
                    if matched_note_dr_head:
                        matched_note_dr.head = matched_note_dr_head.head
                    matched_note_dr.ndate = matched_note_dr.ndate.strftime('%Y-%m-%d')
                    context['matched_note_dr'] = matched_note_dr
    
                if matched_note_cr:
                    matched_note_cr_head = Table_Accountsmaster.objects.filter(user=self.request.user, account_code=matched_note_cr.accountcode).first()
                    if matched_note_cr_head:
                        matched_note_cr.head = matched_note_cr_head.head
                    context['matched_note_cr'] = matched_note_cr
    
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context['company_name'] = company_details.companyname
            context['address1'] = company_details.address1
            context['address2'] = company_details.address2
            context['phoneno'] = company_details.phoneno
    
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')
        date = request.POST.get('date')
        head1 = request.POST.get('head1')
        narration1 = request.POST.get('narration1')
        credit1_str = request.POST.get('credit1', '0')
        credit1 = float(credit1_str) if credit1_str else 0.0  # Convert to float with default value
        head2 = request.POST.get('head2')
        narration2 = request.POST.get('narration2')
        debit2_str = request.POST.get('debit2', '0')
        debit2 = float(debit2_str) if debit2_str else 0.0  # Convert to float with default value
    
        try:
            if series and serial_no:
                matched_notes = Table_DrCrNote.objects.filter(user=self.request.user, series=series, noteno=serial_no, ntype='C')
                if matched_notes.exists():
                    # Update existing debit and credit notes
                    dr_note = matched_notes.filter(dramount__gt=0).first()
                    cr_note = matched_notes.filter(cramount__gt=0).first()
    
                    # Update the current balance before updating the note
                    if dr_note:
                        self.update_account_balance(dr_note.accountcode, float(dr_note.dramount))
                    if cr_note:
                        self.update_account_balance(cr_note.accountcode, -float(cr_note.cramount))
    
                    # Update the note details
                    if dr_note:
                        dr_note.ndate = date
                        dr_note.accountcode = head1  # Updated to head2 for debit2
                        dr_note.narration = narration1
                        dr_note.dramount = credit1
                        dr_note.save()
                        # Update the Account_Master table for debit
                        self.update_account_balance(head1, -credit1)
                    if cr_note:
                        cr_note.ndate = date
                        cr_note.accountcode = head2  # Updated to head1 for credit1
                        cr_note.narration = narration2
                        cr_note.cramount = debit2
                        cr_note.save()
                        # Update the Account_Master table for credit
                        self.update_account_balance(head2, debit2)
    
                    messages.success(request, 'Credit note updated successfully.')
                else:
                    # Create new entries if no existing notes are matched
                    self.create_new_entries(request, series, date, head1, narration1, credit1, head2, narration2, debit2)
    
            else:
                # Create new entries if series and serial_no are not provided
                self.create_new_entries(request, series, date, head1, narration1, credit1, head2, narration2, debit2)
    
            return redirect(self.success_url)
    
        except Exception as e:
            messages.error(request, f'Failed to save credit note: {str(e)}')
            return redirect(self.success_url)
    

    def create_new_entries(self, request, series, date, head1, narration1, credit1, head2, narration2, debit2):
        company = Table_Companydetailsmaster.objects.get(company_id=self.request.session.get('co_id'))
        voucher_config = VoucherConfiguration.objects.filter(series=series, category='Credit Note', company=company).first()
    
        if not voucher_config:
            messages.error(request, 'Invalid series for Credit Note.')
            return redirect(self.success_url)
    
        current_serial_no = voucher_config.serial_no
        next_serial_no = current_serial_no + 1
    
        voucher_config.serial_no = next_serial_no
        voucher_config.save()
    
        coid_entry = Table_companyDetailschild.objects.first()
        fycode_entry = Table_companyDetailschild.objects.first()
        coid = coid_entry.company_id if coid_entry else 'C'
        fycode = fycode_entry.fycode if fycode_entry else 'NON'
        user = request.user

        if Table_DrCrNote.objects.filter(
            user=user,
            series=series,
            noteno=current_serial_no,
            ntype='C'
        ).exists():
            messages.error(request, f"A Credit Note with Series '{series}' and Serial No '{current_serial_no}' already exists.")
            return redirect(self.success_url)
    
        Table_DrCrNote.objects.create(
            user=user,
            company=company,
            series=series,
            ndate=date,
            noteno=current_serial_no,
            accountcode=head1,
            narration=narration1,
            dramount=debit2,
            cramount='0',
            ntype='C',
            userid=user.username,  # Correct field name
            coid=coid,
            fycode=fycode,
            brid='1'
        )
    
        Table_DrCrNote.objects.create(
            user=user,
            company=company,
            series=series,
            ndate=date,
            noteno=current_serial_no,
            accountcode=head2,
            narration=narration2,
            dramount='0',
            cramount=credit1,
            ntype='C',
            userid=user.username,  # Correct field name
            coid=coid,
            fycode=fycode,
            brid='1'
        )
    
        self.update_account_balance(head1, -credit1)
        self.update_account_balance(head2, debit2)
    
        messages.success(request, 'Credit note created successfully.')
    

    def update_account_balance(self, account_code, amount):
        accounts = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user)
    
        if accounts.exists():
            for account in accounts:
                current_balance = float(account.currentbalance or 0)
                account.currentbalance = current_balance + amount
                account.company_id = self.request.session.get("co_id")
                account.branch_id = self.request.session.get("branch")
                account.save()
        else:
            raise ValueError(f"No accounts found with account code: {account_code}")





class AccountCreditTableView(ListView):
    model = Table_DrCrNote
    template_name = 'accounts/credit-note/credit-table.html'
    context_object_name = "drcrnotesss"

    def get_queryset(self):
        return super().get_queryset().filter(ntype='C', user=self.request.user)    

class SearchCreditTableView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/credit-note/credit-search-box.html'

    def get_context_data(self, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=self.request.session.get('co_id'))
        context = super().get_context_data(**kwargs)
        context['series_options'] = VoucherConfiguration.objects.filter(category='Credit Note', company=company).values('series')
        return context

    def post(self, request, *args, **kwargs):
        series = request.POST.get('series')
        serial_no = request.POST.get('serial_no')

        if series and serial_no:

            if Table_DrCrNote.objects.filter(series=series, noteno=serial_no, ntype='C', user=self.request.user).exists():
                return redirect(reverse('main:account_credit_note', kwargs={'series': series, 'serial_no': serial_no}))
            else:
                context = self.get_context_data(**kwargs)
                context['error'] = 'This serial number does not exist.'
                return render(request, self.template_name, context)
        
        context = self.get_context_data(**kwargs)
        context['error'] = 'Please enter both series and serial number.'
        return render(request, self.template_name, context)


class DeleteCreditNoteView(LoginRequiredMixin, DeleteView):
    model = Table_DrCrNote
    success_url = reverse_lazy("main:account_credit_note")

    def get_object(self, queryset=None):
        pk1 = self.kwargs.get('pk1')
        pk2 = self.kwargs.get('pk2')

        # Fetch the object
        obj = Table_DrCrNote.objects.filter(id=pk1, noteno=pk2, user=self.request.user, ntype='C').first()
        if not obj:
            raise Http404("No Table_DrCrNote matches the given query.")
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # Convert dramount and cramount to float before comparison
        dramount = float(self.object.dramount) if self.object.dramount else 0
        cramount = float(self.object.cramount) if self.object.cramount else 0

        # Update the account balance before deleting
        if dramount > 0:
            self.update_account_balance(self.object.accountcode, dramount)
        elif cramount > 0:
            self.update_account_balance(self.object.accountcode, -cramount)

        # Delete the object
        self.object.delete()

        # Optionally, handle the second object if needed
        obj2 = Table_DrCrNote.objects.filter(noteno=self.object.noteno, user=self.request.user, ntype='C').exclude(id=self.object.id).first()
        if obj2:
            dramount2 = float(obj2.dramount) if obj2.dramount else 0
            cramount1 = float(obj2.cramount) if obj2.cramount else 0
            
            if dramount2 > 0:
                self.update_account_balance(obj2.accountcode, dramount2)
            elif cramount1 > 0:
                self.update_account_balance(obj2.accountcode, -cramount1)
            obj2.delete()

        messages.success(request, "credit note entry deleted successfully.")
        return redirect(success_url)

    def update_account_balance(self, account_code, amount):
        """Updates the current balance of the account(s) in Table_Accountsmaster."""
        accounts = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user)
    
        if accounts.exists():
            for account in accounts:
                current_balance = float(account.currentbalance or 0)
                account.currentbalance = current_balance + amount
                account.company_id = self.request.session.get("co_id")
                account.branch_id = self.request.session.get("branch")
                account.save()
        else:
            raise ValueError(f"No accounts found with account code: {account_code}")
 




# - RECEIPT 


class EnterAmountView(LoginRequiredMixin, View):
    template_name = 'accounts/receipt/receipt.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))
        vouchers = VoucherConfiguration.objects.filter(category='receipt', company=company)
        next_serial_numbers = {voucher.series: voucher.serial_no for voucher in vouchers}

        account_masters = Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'])
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user)

        table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
            account_master__category__in=['Bank', 'Cashbook'], account_master__user=request.user
        )

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': account_masters,
            'wallet': Wallet.objects.first(),
            'head_accounts': head_accounts,
            'next_serial_numbers': next_serial_numbers,
            'selected_series': None,
            'next_voucher_no': None,
            'table_acntchildren': table_acntchildren,
            'user_id': request.user.id,
        })

    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))
            series = request.POST.get('Series')
            vdate = request.POST.get('Vdate')
            headcode = request.POST.get('Headcode')
            user_id = request.user.id
            fy_code = '2024-2025'
            coid = 'C'
            branch_id = '1'
    
            accountcodes = request.POST.getlist('Accountcode[]')
            narrations = request.POST.getlist('Narration[]')
            vtypes = request.POST.getlist('VType[]')
            payments = request.POST.getlist('payment[]')
    
            if not (len(accountcodes) == len(narrations) == len(vtypes) == len(payments)):
                raise ValueError("Mismatched input lengths in form data.")
    
            total_amount = sum(float(payment) for payment in payments)
    
            voucher_config = VoucherConfiguration.objects.get(series=series, category='receipt', company=company)
            current_serial_no = int(voucher_config.serial_no)
            voucher_no = current_serial_no
    
            with transaction.atomic():
                for accountcode, narration, vtype, payment in zip(accountcodes, narrations, vtypes, payments):
                    # Create voucher entry
                    Table_Voucher.objects.create(
                        user=request.user,
                        company=company,
                        Series=series,
                        VoucherNo=voucher_no,
                        Vdate=vdate,
                        Accountcode=accountcode,
                        Headcode=headcode,
                        payment=payment,
                        VAmount=total_amount,
                        VType=vtype,
                        Narration=narration,
                        CStatus='R',
                        UserID=user_id,
                        FYCode=fy_code,
                        Coid=coid,
                        Branch_ID=branch_id
                    )
    
                    # Update the current balance for Table_Acntchild
                    try:
                        account_master = Table_Accountsmaster.objects.filter(account_code=accountcode, user=self.request.user).first()
                        acnt_child = Table_Acntchild.objects.get(account_code=accountcode, account_master=account_master)
                        if acnt_child:
                            current_balance = float(acnt_child.current_balance or 0)
                            payment_amount = float(payment)
                            new_balance = current_balance - payment_amount
                            acnt_child.current_balance = str(new_balance)
                            acnt_child.save()
                        else:
                            print('no acnt child 1')
                    except Table_Acntchild.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Acntchild.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode}: {e} 1")
    
                    # Update the current balance for Table_Accountsmaster
                    try:
                        account_master = Table_Accountsmaster.objects.filter(account_code=accountcode, user=self.request.user).first()
                        if account_master:
                            current_balance_master = float(account_master.currentbalance or 0)
                            new_balance_master = current_balance_master - float(payment)
                            account_master.currentbalance = str(new_balance_master)
                            account_master.save()
                        else:
                            print('no account_master 1')
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode} in Table_Accountsmaster: {e} 2")
    
                # Only update the selected account
                selected_account_code = request.POST.get('Headcode')
                # In the EnterAmountView post method

                # Update the current balance for Table_Accountsmaster (Head accounts)
                if selected_account_code:
                    try:
                        selected_account_master = Table_Accountsmaster.objects.filter(account_code=selected_account_code, user=self.request.user).first()
                        current_balance_master = float(selected_account_master.currentbalance or 0)
                        new_balance_master = current_balance_master + total_amount
                        selected_account_master.currentbalance = str(new_balance_master)
                        selected_account_master.save()
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Selected account code {selected_account_code} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for selected account code {selected_account_code}: {e} 2")

    
                voucher_config.serial_no = voucher_no + 1
                voucher_config.save()
    
            next_serial_numbers = {
                voucher.series: str(voucher_config.serial_no)
                for voucher in VoucherConfiguration.objects.filter(category='receipt')
            }
    
            return render(request, self.template_name, {
                'success': "Voucher saved successfully!",
                'vouchers': VoucherConfiguration.objects.filter(category='receipt', company=company),
                'accountmas': Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user),
                'wallet': Wallet.objects.first(),
                'head_accounts': Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user),
                'next_serial_numbers': next_serial_numbers,
                'selected_series': series,
                'next_voucher_no': next_serial_numbers.get(series),
                'table_acntchildren': Table_Acntchild.objects.select_related('account_master').filter(
                    account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
                ),
                'user_id': request.user.id,
            })
        except Exception as e:
            print(f"Error: {e}")
            # If there's an error, still provide the necessary context
            next_serial_numbers = {
                voucher.series: str(voucher_config.serial_no)
                for voucher in VoucherConfiguration.objects.filter(category='receipt')
            }
            
            return render(request, self.template_name, {
                'error': str(e),
                'vouchers': VoucherConfiguration.objects.filter(category='receipt', company=company),
                'accountmas': Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user),
                'wallet': Wallet.objects.first(),
                'head_accounts': Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user),
                'next_serial_numbers': next_serial_numbers,
                'selected_series': series,
                'next_voucher_no': next_serial_numbers.get(series),
                'table_acntchildren': Table_Acntchild.objects.select_related('account_master').filter(
                    account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
                ),
                'user_id': request.user.id,
            })
        
        
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.urls import reverse

class EditReceiptView(LoginRequiredMixin, View):
    template_name = 'accounts/receipt/edit_receipt.html'

    def get(self, request, *args, **kwargs):
        series = request.GET.get('Series')
        voucher_no = request.GET.get('VoucherNo')
        company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))

        # Fetch necessary data
        vouchers = VoucherConfiguration.objects.filter(category='receipt', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user)
        wallet = Wallet.objects.first()
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank'], user=self.request.user)
        table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
            account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
        )

        # Fetch voucher entries for the given series and voucher number
        voucher_entries = Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='R', user=self.request.user)

        if not voucher_entries:
            return render(request, 'accounts/receipt/receipt_modify.html', {
                'vouchers': vouchers,
                'accountmas': accountmas,
                'wallet': wallet,
                'head_accounts': head_accounts,
                'table_acntchildren': table_acntchildren,
                'voucher_entries': [],
                'user_id': request.user.id,
                'error_message': 'This combination of Series and Voucher No does not exist.',
                'redirect_url': reverse('main:receipt_modify')  # Replace with the correct URL name
            })

        # Assuming you want to fetch the first entry for the book head
        first_voucher = voucher_entries.first()
        headcode = first_voucher.Headcode

        try:
            # Retrieve the account master entry for the selected head code
            head_account = Table_Accountsmaster.objects.filter(account_code=headcode, user=self.request.user).first()
            head_name = head_account.head  # Assuming 'head' is the field name for the head name
            current_balance = head_account.currentbalance  # Retrieve the current balance
        except Table_Accountsmaster.DoesNotExist:
            head_name = None  # Handle this as appropriate
            current_balance = None

        # Pass the head name and current balance to the template
        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'wallet': wallet,
            'head_accounts': head_accounts,
            'table_acntchildren': table_acntchildren,
            'voucher_entries': voucher_entries,
            'user_id': request.user.id,
            'headcode': headcode,  # Pass the head code to the template
            'head_name': head_name,  # Pass the head name to the template
            'current_balance': current_balance  # Pass current balance to the template
        })

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')  # Hidden input to determine the action
        series = request.POST.get('Series')
        voucher_no = request.POST.get('VoucherNo')
        company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))

        try:
            if action == 'delete':
                # Fetch voucher entries for deletion
                voucher_entries = Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='R', user=self.request.user)

                if not voucher_entries:
                    return render(request, self.template_name, {
                        'error': 'No voucher entries found for deletion.',
                        'user_id': request.user.id,
                        'redirect_url': reverse('web:receipt_modify')
                    })

                # Get the Headcode and old total amount for adjustment
                headcode = voucher_entries.first().Headcode
                old_total_amount = sum(float(entry.payment) for entry in voucher_entries)

                # Update the current balance of the head account
                try:
                    head_account = Table_Accountsmaster.objects.get(account_code=headcode, user=self.request.user)
                    current_balance = float(head_account.currentbalance or 0)
                    new_balance = current_balance - old_total_amount  # Add back the old amount
                    head_account.currentbalance = str(new_balance)
                    head_account.save()
                except Table_Accountsmaster.DoesNotExist:
                    print(f"Head account code {headcode} not found in Table_Accountsmaster.")

                # Delete the voucher entries
                voucher_entries.delete()

                return render(request, self.template_name, {
                    'success': "Receipt deleted successfully!",
                    'user_id': request.user.id,
                    'redirect_url': reverse('web:receipt_modify')
                })

            # Update logic for editing the receipt (if not delete)
            accountcodes = request.POST.getlist('Accountcode[]')
            narrations = request.POST.getlist('Narration[]')
            vtypes = request.POST.getlist('VType[]')
            payments = request.POST.getlist('payment[]')

            if not (len(accountcodes) == len(narrations) == len(vtypes) == len(payments)):
                raise ValueError("Mismatched input lengths in form data.")

            total_amount = sum(float(payment) for payment in payments)

            # Use a transaction to ensure atomic operations
            with transaction.atomic():
                # Fetch and revert existing voucher entries
                voucher_entries = Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='R', user=self.request.user)
                old_total_amount = 0
                for entry in voucher_entries:
                    account_code = entry.Accountcode
                    payment_amount = float(entry.payment)
                    old_total_amount += payment_amount

                    # Revert the old payment amount from Table_Acntchild
                    try:
                        acnt_child = Table_Acntchild.objects.get(account_code=account_code, account_master__user=self.request.user)
                        current_balance = float(acnt_child.current_balance or 0)
                        new_balance = current_balance + payment_amount  # Add back the old amount
                        acnt_child.current_balance = str(new_balance)
                        acnt_child.save()
                    except Table_Acntchild.DoesNotExist:
                        print(f"Account code {account_code} not found in Table_Acntchild.")
                    except Exception as e:
                        print(f"Error reverting balance for account code {account_code}: {e}")

                    # Revert the old payment amount from Table_Accountsmaster
                    try:
                        account_master = Table_Accountsmaster.objects.get(account_code=account_code, user=self.request.user)
                        current_balance_master = float(account_master.currentbalance or 0)
                        new_balance_master = current_balance_master + payment_amount  # Add back the old amount
                        account_master.currentbalance = str(new_balance_master)
                        account_master.save()
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account code {account_code} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error reverting balance for account code {account_code} in Table_Accountsmaster: {e}")

                # Delete old voucher entries after reverting balances
                voucher_entries.delete()

                # Create new voucher entries with updated balances
                for accountcode, narration, vtype, payment in zip(accountcodes, narrations, vtypes, payments):
                    Table_Voucher.objects.create(
                        user=request.user,
                        company=company,
                        Series=series,
                        VoucherNo=voucher_no,
                        Vdate=request.POST.get('Vdate'),
                        Accountcode=accountcode,
                        Headcode=request.POST.get('Headcode'),
                        payment=payment,
                        VAmount=total_amount,
                        VType=vtype,
                        Narration=narration,
                        CStatus='R',
                        UserID=request.user.id,
                        FYCode='2024-2025',
                        Coid='C',
                        Branch_ID='1'
                    )

                    # Update the current balance for Table_Acntchild
                    try:
                        acnt_child = Table_Acntchild.objects.get(account_code=accountcode, account_master__user=self.request.user)
                        if acnt_child:
                            current_balance = float(acnt_child.current_balance or 0)
                            new_balance = current_balance - float(payment)  # Subtract the new amount
                            acnt_child.current_balance = str(new_balance)
                            acnt_child.save()
                        else:
                            print('no acnt child 2')
                    except Table_Acntchild.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Acntchild.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode}: {e} 3")

                    # Update the current balance for Table_Accountsmaster
                    try:
                        account_master = Table_Accountsmaster.objects.get(account_code=accountcode, user=self.request.user)
                        if account_master:
                            current_balance_master = float(account_master.currentbalance or 0)
                            new_balance_master = current_balance_master - float(payment)  # Subtract the new amount
                            account_master.currentbalance = str(new_balance_master)
                            account_master.save()
                        else:
                            print('no account master 2')
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode} in Table_Accountsmaster: {e} 4")

                # Update the balance of the selected head account
                headcode = request.POST.get('Headcode')
                if headcode:
                    try:
                        selected_account_master = Table_Accountsmaster.objects.get(account_code=headcode, user=self.request.user)
                        current_balance_master = float(selected_account_master.currentbalance or 0)
                        new_balance_master = current_balance_master + total_amount - old_total_amount

                        selected_account_master.currentbalance = str(new_balance_master)
                        selected_account_master.save()
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Selected head account code {headcode} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for selected head account code {headcode}: {e}")

                return render(request, self.template_name, {
                    'success': "Receipt updated successfully!",
                    'user_id': request.user.id,
                    'redirect_url': reverse('main:receipt_modify')
                })

        except Exception as e:
            print(f"Error: {e}")
            return render(request, self.template_name, {
                'error': str(e),
                'user_id': request.user.id,
                'redirect_url': reverse('main:receipt_modify')
            })



   

class SearchReceiptView(LoginRequiredMixin, View):
    template_name = 'accounts/receipt/receipt_modify.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))
        vouchers = VoucherConfiguration.objects.filter(category='receipt', company=company)
        return render(request, self.template_name, {'vouchers': vouchers})
    
    
class ReceiptDetailView(View):
    template_name = 'accounts/receipt/table-details.html'

    def get(self, request, voucher_id, *args, **kwargs):
        voucher = get_object_or_404(Table_Voucher, id=voucher_id)
        return render(request, self.template_name, {
            'voucher': voucher,
        })


class ReceiptListTable(LoginRequiredMixin, ListView):
    model = Table_Voucher
    template_name = 'accounts/receipt/receipt_list.html'
    context_object_name = "vouchers"

    def get_queryset(self):
        company = Table_Companydetailsmaster.objects.get(company_id=self.request.session.get('co_id'))
        receipt_series = VoucherConfiguration.objects.filter(category='receipt', company=company).values_list('series', flat=True)

        # Filter Table_Voucher based on the series related to the receipt category and CStatus being 'R'
        return Table_Voucher.objects.filter(Series__in=receipt_series, CStatus='R', user=self.request.user)
        



# - PAYMENT

from django.db import transaction
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import VoucherConfiguration, Table_Acntchild, Table_Accountsmaster, Table_Voucher

class PaymentEnterAmountView(LoginRequiredMixin, View):
    template_name = 'accounts/payment/payment.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        vouchers = VoucherConfiguration.objects.filter(category='payment', company=company)
        next_serial_numbers = {voucher.series: voucher.serial_no for voucher in vouchers}

        account_masters = Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user)
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user)

        table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
            account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
        )

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': account_masters,
            'head_accounts': head_accounts,
            'next_serial_numbers': next_serial_numbers,
            'table_acntchildren': table_acntchildren,
            'user_id': request.user.id,
        })

    def update_current_balance(self, account_code, payment, increase=True):
        try:
            acnt_child = Table_Acntchild.objects.filter(account_code=account_code,  account_master__user=self.request.user).first()
            current_balance = float(acnt_child.current_balance or 0)
            payment_amount = float(payment)
            new_balance = current_balance + payment_amount if increase else current_balance - payment_amount
            acnt_child.current_balance = str(new_balance)
            acnt_child.save()
        except Table_Acntchild.DoesNotExist:
            print(f"Account code {account_code} not found in Table_Acntchild.")
        except Exception as e:
            print(f"Error updating balance for account code {account_code}: {e} 5")

        try:
            account_master = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user).first()
            current_balance_master = float(account_master.currentbalance or 0)
            # Update balance with appropriate adjustment for head accounts
            if account_master.category in ['Cashbook', 'Bank']:
                new_balance_master = current_balance_master - payment_amount if increase else current_balance_master - payment_amount
            else:
                new_balance_master = current_balance_master - payment_amount if not increase else current_balance_master + payment_amount
            account_master.currentbalance = str(new_balance_master)
            account_master.save()
        except Table_Accountsmaster.DoesNotExist:
            print(f"Account code {account_code} not found in Table_Accountsmaster.")
        except Exception as e:
            print(f"Error updating balance for account code {account_code} in Table_Accountsmaster: {e} 6")


    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('Series')
            vdate = request.POST.get('Vdate')
            headcode = request.POST.get('Headcode')
            user_id = request.user.id
            fy_code = '2024-2025'
            coid = 'C'
            branch_id = '1'

            accountcodes = request.POST.getlist('Accountcode[]')
            narrations = request.POST.getlist('Narration[]')
            vtypes = request.POST.getlist('VType[]')
            payments = request.POST.getlist('payment[]')

            if not (len(accountcodes) == len(narrations) == len(vtypes) == len(payments)):
                raise ValueError("Mismatched input lengths in form data.")

            total_amount = sum(float(payment) for payment in payments)

            voucher_config = VoucherConfiguration.objects.get(series=series, category='payment', company=company)
            current_serial_no = int(voucher_config.serial_no)
            voucher_no = current_serial_no

            with transaction.atomic():
                for accountcode, narration, vtype, payment in zip(accountcodes, narrations, vtypes, payments):
                    # Create voucher entry
                    Table_Voucher.objects.create(
                        user=request.user,
                        company=company,
                        Series=series,
                        VoucherNo=voucher_no,
                        Vdate=vdate,
                        Accountcode=accountcode,
                        Headcode=headcode,
                        payment=payment,
                        VAmount=total_amount,
                        VType=vtype,
                        Narration=narration,
                        CStatus='P',
                        UserID=user_id,
                        FYCode=fy_code,
                        Coid=coid,
                        Branch_ID=branch_id
                    )

                    # Update the current balance for each account
                    self.update_current_balance(accountcode, payment)

                # Only update the selected account
                selected_account_code = request.POST.get('Headcode')
                if selected_account_code:
                    self.update_current_balance(selected_account_code, total_amount)

                voucher_config.serial_no = voucher_no + 1
                voucher_config.save()

            next_serial_numbers = {
                voucher.series: str(voucher_config.serial_no)
                for voucher in VoucherConfiguration.objects.filter(category='payment')
            }

            return render(request, self.template_name, {
                'success': "Payment voucher saved successfully!",
                'vouchers': VoucherConfiguration.objects.filter(category='payment', company=company),
                'accountmas': Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user),
                'head_accounts': Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user),
                'next_serial_numbers': next_serial_numbers,
                'table_acntchildren': Table_Acntchild.objects.select_related('account_master').filter(
                    account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
                ),
                'user_id': request.user.id,
            })
        except Exception as e:
            print(f"Error: {e}")
            next_serial_numbers = {
                voucher.series: str(voucher_config.serial_no)
                for voucher in VoucherConfiguration.objects.filter(category='payment', company=company)
            }
            return render(request, self.template_name, {
                'error': str(e),
                'vouchers': VoucherConfiguration.objects.filter(category='payment', company=company),
                'accountmas': Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user),
                'head_accounts': Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user),
                'next_serial_numbers': next_serial_numbers,
                'table_acntchildren': Table_Acntchild.objects.select_related('account_master').filter(
                    account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
                ),
                'user_id': request.user.id,
            })








from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import VoucherConfiguration, Table_Voucher, Table_Accountsmaster, Table_Acntchild
from django.urls import reverse

class EditPaymentView(LoginRequiredMixin, View):
    template_name = 'accounts/payment/edit_payment.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        series = request.GET.get('Series')
        voucher_no = request.GET.get('VoucherNo')
    
        # Fetch necessary data
        vouchers = VoucherConfiguration.objects.filter(category='payment', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user)
        wallet = Wallet.objects.first()
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank'], user=self.request.user)
        table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
            account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user,
        )
    
        # Fetch voucher entries for the given series and voucher number
        voucher_entries = Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='P', user=self.request.user)
    
        if not voucher_entries:
            # If voucher entries do not exist, display SweetAlert error message
            return render(request, 'accounts/payment/payment_modify.html', {
                'vouchers': vouchers,
                'accountmas': accountmas,
                'wallet': wallet,
                'head_accounts': head_accounts,
                'table_acntchildren': table_acntchildren,
                'voucher_entries': [],
                'user_id': request.user.id,
                'error_message': 'This combination of Series and Voucher No does not exist.',
                'redirect_url': reverse('web:payment_modify')  # Replace with the correct URL name
            })
    
        # Get the head code from the first voucher entry
        head_code = voucher_entries[0].Headcode
    
        # Fetch the current balance of the head account
        try:
            head_account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
            current_balance_head = head_account.currentbalance or 0
            head_account_name = head_account.head  # Get the account name
        except Table_Accountsmaster.DoesNotExist:
            current_balance_head = None  # Handle case where head account does not exist
            head_account_name = None
    
        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'wallet': wallet,
            'head_accounts': head_accounts,
            'table_acntchildren': table_acntchildren,
            'voucher_entries': voucher_entries,
            'user_id': request.user.id,
            'current_balance_head': current_balance_head,  # Pass current balance to the template
            'head_account_name': head_account_name,  # Pass the head account name
        })
    

    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('Series')
            vdate = request.POST.get('Vdate')
            headcode = request.POST.get('Headcode')
            user_id = request.user.id
            fy_code = '2024-2025'
            coid = 'C'
            branch_id = '1'
    
            accountcodes = request.POST.getlist('Accountcode[]')
            narrations = request.POST.getlist('Narration[]')
            vtypes = request.POST.getlist('VType[]')
            payments = request.POST.getlist('payment[]')
            voucher_no = request.POST.get('VoucherNo')
    
            # Ensure all lists are of the same length
            if not (len(accountcodes) == len(narrations) == len(vtypes) == len(payments)):
                raise ValueError("Mismatched input lengths in form data.")
    
            # Validate that all payments except those related to head_accounts are positive
            for payment, accountcode in zip(payments, accountcodes):
                if Table_Accountsmaster.objects.filter(account_code=accountcode, user=self.request.user).exclude(category__in=['Cashbook', 'Bank']).exists():
                    if float(payment) < 0:
                        raise ValueError(f"Payment for account code {accountcode} must be positive.")
    
            # Calculate the new total amount
            new_total_amount = sum(float(payment) for payment in payments)
    
            with transaction.atomic():
                # Fetch existing entries to get old amounts and account codes
                old_entries = Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='P')
    
                # Calculate the old total amount
                old_total_amount = sum(float(entry.payment) for entry in old_entries)
    
                # Revert previous balances before updating
                for old_entry in old_entries:
                    accountcode = old_entry.Accountcode
                    old_payment = old_entry.payment
                    try:
                        account_master = Table_Accountsmaster.objects.get(account_code=accountcode, user=self.request.user)
                        if account_master:
                            current_balance_master = float(account_master.currentbalance or 0)
                            updated_balance_master = current_balance_master - float(old_payment)  # Revert balance
                            account_master.currentbalance = str(updated_balance_master)
                            account_master.save()
                        else:
                            print('no account master 3')
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode} in Table_Accountsmaster: {e} 7")
    
                # Delete old entries
                old_entries.delete()
    
                # Update or create new entries and adjust balances
                for accountcode, narration, vtype, payment in zip(accountcodes, narrations, vtypes, payments):
                    Table_Voucher.objects.create(
                        user=request.user,
                        company=company,
                        Series=series,
                        VoucherNo=voucher_no,
                        Vdate=vdate,
                        Accountcode=accountcode,
                        Headcode=headcode,
                        payment=payment,
                        VAmount=new_total_amount,  # Save the total amount
                        VType=vtype,
                        Narration=narration,
                        CStatus='P',
                        UserID=user_id,
                        FYCode=fy_code,
                        Coid=coid,
                        Branch_ID=branch_id
                    )
        
                    # Update the balance in Table_Accountsmaster
                    try:
                        account_master = Table_Accountsmaster.objects.get(account_code=accountcode, user=self.request.user)
                        if account_master:
                            current_balance_master = float(account_master.currentbalance or 0)
                            updated_balance_master = current_balance_master + float(payment)  # Add new payment
                            account_master.currentbalance = str(updated_balance_master)
                            account_master.save()
                        else:
                            print('no account master 4')
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account code {accountcode} not found in Table_Accountsmaster.")
                    except Exception as e:
                        print(f"Error updating balance for account code {accountcode} in Table_Accountsmaster: {e} 8")
    
                # Update the balance for head_accounts by adding the difference between the new and old total amount
                try:
                    head_account = Table_Accountsmaster.objects.filter(account_code=headcode, user=self.request.user).first()
                    current_balance_head = float(head_account.currentbalance or 0)
                    difference = new_total_amount - old_total_amount
                    updated_balance_head = current_balance_head - difference
                    head_account.currentbalance = str(updated_balance_head)
                    head_account.save()
    
                except Table_Accountsmaster.DoesNotExist:
                    print(f"Head account code {headcode} not found in Table_Accountsmaster.")
                except Exception as e:
                    print(f"Error updating balance for head account code {headcode} in Table_Accountsmaster: {e}")
    
                # Update the serial number in VoucherConfiguration for the next use if not editing
                if not voucher_no:
                    voucher_config = VoucherConfiguration.objects.get(series=series, category='payment', company=company)
                    voucher_config.serial_no += 1
                    voucher_config.save()
    
            print("Payment saved successfully!")
            return redirect('main:payment')  # Redirect to payment modify page after saving
    
        except Exception as e:
            print("Error saving payment: ", e)
    
            # Fetch necessary data to repopulate the form
            vouchers = VoucherConfiguration.objects.filter(category='payment', company=company)
            accountmas = Table_Accountsmaster.objects.filter(category__in=['Cashbook', 'Bank'], user=self.request.user)
            wallet = Wallet.objects.first()
            head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Cashbook', 'Bank']).filter(user=self.request.user)
            table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
                account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
            )
    
            return render(request, self.template_name, {
                'error_message': str(e),
                'vouchers': vouchers,
                'accountmas': accountmas,
                'wallet': wallet,
                'head_accounts': head_accounts,
                'table_acntchildren': table_acntchildren,
                'voucher_entries': Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='P', user=self.request.user),
                'user_id': request.user.id,
            })








        
    
class SearchPaymentView(LoginRequiredMixin, View):
    template_name = 'accounts/payment/payment_modify.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        vouchers = VoucherConfiguration.objects.filter(category='payment', company=company)
        return render(request, self.template_name, {'vouchers': vouchers})
    

# class ModifyPaymentTableView(TemplateView):
#     template_name = 'accounts/payment/payment_modify.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['series_options'] = VoucherConfiguration.objects.filter(category='payment').values('series')
#         return context

#     def post(self, request, *args, **kwargs):
#         series = request.POST.get('series')
#         voucher_no = request.POST.get('voucher_no')  # Change from serial_no to VoucherNo

#         if series and voucher_no:
#             # Check if the voucher number exists
#             if Table_Voucher.objects.filter(Series=series, VoucherNo=voucher_no, CStatus='P').exists():
#                 return redirect(reverse('web:account_debit_note', kwargs={'series': series, 'voucher_no': voucher_no}))
#             else:
#                 context = self.get_context_data(**kwargs)
#                 context['error'] = 'This voucher number does not exist or does not match the criteria.'
#                 return render(request, self.template_name, context)
        
#         context = self.get_context_data(**kwargs)
#         context['error'] = 'Please enter both series and voucher number.'
#         return render(request, self.template_name, context)


class PaymentListTable(LoginRequiredMixin, ListView):
    model = Table_Voucher
    template_name = 'accounts/payment/payment_list.html'
    context_object_name = "vouchers"

    def get_queryset(self):
        company = Table_Companydetailsmaster.objects.get(company_id=(self.request.session.get('co_id')))
        payment_series = VoucherConfiguration.objects.filter(category='payment', company=company).values_list('series', flat=True)
        
        # Filter Table_Voucher based on the series related to the payment category and CStatus being 'R'
        return Table_Voucher.objects.filter(Series__in=payment_series, CStatus='P', user=self.request.user)


# - Journal Entry

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Table_Journal_Entry, Table_Accountsmaster, VoucherConfiguration, Table_companyDetailschild
from decimal import Decimal

class JournalEntryView(View):
    template_name = 'accounts/journal-entry/journal-entry.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        vouchers = VoucherConfiguration.objects.filter(category='Journal Entry', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Bank', 'Cashbook'], user=self.request.user)
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Bank', 'Cashbook']).filter(user=self.request.user)

        next_serial_numbers = {}
        for voucher in vouchers:
            last_serial = Table_Journal_Entry.objects.filter(series=voucher.series, auth_user=self.request.user).order_by('-voucher_no').first()
            next_serial_numbers[voucher.series] = str(int(last_serial.voucher_no) + 1) if last_serial else voucher.serial_no

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'head_accounts': head_accounts,
            'next_serial_numbers': next_serial_numbers,
            'user_id': request.user.id,
        })

    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('series')
            voucher_no = request.POST.get('voucher_no')
            vdate = request.POST.get('vdate')
            user_id = request.user.id
            branch_id = '1'
            heads = request.POST.getlist('head')
            head_codes = request.POST.getlist('head_code')
            narrations = request.POST.getlist('narration[]')
            debit = request.POST.getlist('dramount[]')
            credit = request.POST.getlist('cramount[]')

            if not (len(heads) == len(narrations) == len(debit) == len(credit) == len(head_codes)):
                raise ValueError("Mismatched input lengths in form data.")

            total_amount = sum(float(amount) for amount in debit if amount)

            company_details = Table_companyDetailschild.objects.first()
            coid = company_details.company_id if company_details else ''
            fycode = company_details.fycode if company_details else ''

            with transaction.atomic():
                # Fetch existing entries and compute old debit and credit totals
                existing_entries = Table_Journal_Entry.objects.filter(series=series, voucher_no=voucher_no, auth_user=self.request.user)
                old_account_updates = {}
                for entry in existing_entries:
                    if entry.accountcode not in old_account_updates:
                        old_account_updates[entry.accountcode] = Decimal('0')
                    old_account_updates[entry.accountcode] += (Decimal(entry.dramount) - Decimal(entry.cramount))

                # Delete existing entries
                existing_entries.delete()

                # Create new entries
                for head, head_code, narration, debit_amount, credit_amount in zip(heads, head_codes, narrations, debit, credit):
                    if not head_code or not head_code.isdigit():  # Skip if head_code is empty or not a number
                        continue

                    Table_Journal_Entry.objects.create(
                        auth_user=self.request.user,
                        company=company,
                        series=series,
                        voucher_no=voucher_no,
                        vdate=vdate,
                        accountcode=head_code,
                        narration=narration,
                        dramount=float(debit_amount) if debit_amount else 0,
                        cramount=float(credit_amount) if credit_amount else 0,
                        user_id=user_id,
                        fycode=fycode,
                        coid=coid,
                        brid=branch_id
                    )

                # Compute new debit and credit totals
                new_account_updates = {}
                for head, head_code, debit_amount, credit_amount in zip(heads, head_codes, debit, credit):
                    if not head_code or not head_code.isdigit():  # Skip if head_code is empty or not a number
                        continue

                    if debit_amount:
                        if head_code not in new_account_updates:
                            new_account_updates[head_code] = Decimal('0')
                        new_account_updates[head_code] += Decimal(debit_amount)
                    if credit_amount:
                        if head_code not in new_account_updates:
                            new_account_updates[head_code] = Decimal('0')
                        new_account_updates[head_code] -= Decimal(credit_amount)

                # Update account balances
                accounts_to_update = []
                for head_code, new_amount in new_account_updates.items():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
                        old_amount = old_account_updates.get(head_code, Decimal('0'))
                        account.currentbalance = (Decimal(account.currentbalance or '0') - old_amount + new_amount)
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account with code {head_code} does not exist. Skipping update.")

                Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])

                # Update the voucher configuration with the new serial number if needed
                voucher_no_int = int(voucher_no)
                voucher_config = VoucherConfiguration.objects.get(series=series, category='Journal Entry', company=company)
                if voucher_no_int > voucher_config.serial_no:
                    voucher_config.serial_no = voucher_no_int
                    voucher_config.save()

            messages.success(request, "Journal saved successfully!")
            return redirect('main:account_journal_entry')
        except Exception as e:
            print("Error saving Journal Entry: ", e)
            messages.error(request, f"Error saving Journal Entry: {str(e)}")
            return self.get(request)




class JournalEntryTable(LoginRequiredMixin, ListView):
    model = Table_Journal_Entry
    template_name = 'accounts/journal-entry/journal-entry-table.html'
    context_object_name = "journalentrys"
    
    def get_queryset(self):
        return self.model.objects.filter(auth_user=self.request.user)


class SearchJournalEntryView(LoginRequiredMixin, View):
    template_name = 'accounts/journal-entry/search-journal-entry.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        series = request.GET.get('Series', '')
        voucher_no = request.GET.get('VoucherNo', '')

        error_message = None
        if not series or not voucher_no:
            error_message = "Please provide both series and voucher number."

        vouchers = VoucherConfiguration.objects.filter(category='Journal Entry', company=company)
        return render(request, self.template_name, {'vouchers': vouchers, 'error_message': error_message})


class EditJournalEntry(LoginRequiredMixin, View):
    template_name = 'accounts/journal-entry/edit-journal-entry.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        series = request.GET.get('Series')
        voucher_no = request.GET.get('VoucherNo')

        vouchers = VoucherConfiguration.objects.filter(category='Journal Entry', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Bank', 'Cashbook'], user=self.request.user)
        wallet = Wallet.objects.first()
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Bank', 'Cashbook']).filter(user=self.request.user)
        table_acntchildren = Table_Acntchild.objects.select_related('account_master').filter(
            account_master__category__in=['Bank', 'Cashbook'], account_master__user=self.request.user
        )

        voucher_entries = Table_Journal_Entry.objects.filter(series=series, voucher_no=voucher_no, auth_user=self.request.user)

        if not voucher_entries:
            return redirect('main:search_journal_entry')  # Ensure this matches the name in urls.py

        valid_account_codes = head_accounts.values_list('account_code', flat=True)

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'wallet': wallet,
            'head_accounts': head_accounts,
            'table_acntchildren': table_acntchildren,
            'voucher_entries': voucher_entries,
            'user_id': request.user.id,
            'valid_account_codes': valid_account_codes
        })

    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('series')
            vdate = request.POST.get('vdate')
            voucher_no = request.POST.get('voucher_no')
            if not voucher_no:
                raise ValueError("Voucher number is required.")
            user_id = request.user.id

            company_details = Table_companyDetailschild.objects.first()
            if not company_details:
                raise ValueError("Company details not found.")

            fycode = company_details.fycode
            coid = company_details.company_id  # Assuming `company_id` is the ID for coid
            branch_id = '1'  # Adjust as needed

            heads = request.POST.getlist('head')
            narrations = request.POST.getlist('narration[]')
            debit = request.POST.getlist('dramount[]')
            credit = request.POST.getlist('cramount[]')

            if not (len(heads) == len(narrations) == len(debit) == len(credit)):
                raise ValueError("Mismatched input lengths in form data.")

            # Convert to Decimal for consistency
            debit = [Decimal(d) if d else Decimal('0') for d in debit]
            credit = [Decimal(c) if c else Decimal('0') for c in credit]

            total_amount = sum(debit)

            voucher_config = VoucherConfiguration.objects.get(series=series, category='Journal Entry', company=company)

            with transaction.atomic():
                # Fetch existing entries and compute old debit and credit totals
                existing_entries = Table_Journal_Entry.objects.filter(series=series, voucher_no=voucher_no, auth_user=self.request.user)
                old_account_updates = {}
                for entry in existing_entries:
                    if entry.accountcode not in old_account_updates:
                        old_account_updates[entry.accountcode] = Decimal('0')
                    old_account_updates[entry.accountcode] += (Decimal(entry.dramount) - Decimal(entry.cramount))

                # Delete existing entries
                existing_entries.delete()

                # Create new entries
                for head, narration, debit_amount, credit_amount in zip(heads, narrations, debit, credit):
                    Table_Journal_Entry.objects.create(
                        auth_user=self.request.user,
                        company=company,
                        series=series,
                        voucher_no=voucher_no,
                        vdate=vdate,
                        accountcode=head,
                        narration=narration,
                        dramount=debit_amount,
                        cramount=credit_amount,
                        user_id=user_id,
                        fycode=fycode,
                        coid=coid,
                        brid=branch_id
                    )

                # Compute new debit and credit totals
                new_account_updates = {}
                for head, debit_amount, credit_amount in zip(heads, debit, credit):
                    if debit_amount:
                        if head not in new_account_updates:
                            new_account_updates[head] = Decimal('0')
                        new_account_updates[head] += debit_amount
                    if credit_amount:
                        if head not in new_account_updates:
                            new_account_updates[head] = Decimal('0')
                        new_account_updates[head] -= credit_amount

                # Update account balances
                accounts_to_update = []
                for head_code, new_amount in new_account_updates.items():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
                        old_amount = old_account_updates.get(head_code, Decimal('0'))
                        account.currentbalance = (Decimal(account.currentbalance or '0') - old_amount + new_amount)
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account with code {head_code} does not exist. Skipping update.")

                Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])

                # Update the voucher configuration with the new serial number if needed
                voucher_no_int = int(voucher_no)
                if voucher_no_int > voucher_config.serial_no:
                    voucher_config.serial_no = voucher_no_int
                    voucher_config.save()

            messages.success(request, "Journal entry updated successfully!")
            return redirect('main:account_journal_entry')
        except Exception as e:
            print("Error updating Journal Entry: ", e)
            messages.error(request, f"Error updating Journal Entry: {str(e)}")
            return self.get(request)


class DeleteJournalEntryView(LoginRequiredMixin, View):
    def delete(self, request, voucher_no, *args, **kwargs):
        try:
            # Fetch the journal entries to be deleted
            entries = Table_Journal_Entry.objects.filter(voucher_no=voucher_no, auth_user=self.request.user)
            
            if entries.exists():
                # Compute the totals to be removed
                debit_totals = {}
                credit_totals = {}
                
                for entry in entries:
                    account_code = entry.accountcode
                    debit_amount = Decimal(entry.dramount)
                    credit_amount = Decimal(entry.cramount)
                    
                    if account_code not in debit_totals:
                        debit_totals[account_code] = Decimal('0')
                        credit_totals[account_code] = Decimal('0')
                    
                    debit_totals[account_code] += debit_amount
                    credit_totals[account_code] += credit_amount

                # Delete the entries
                entries.delete()

                # Update the balances
                accounts_to_update = []
                for account_code in debit_totals.keys():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=account_code, user=self.request.user)
                        old_balance = Decimal(account.currentbalance or '0')
                        debit_total = debit_totals.get(account_code, Decimal('0'))
                        credit_total = credit_totals.get(account_code, Decimal('0'))
                        new_balance = old_balance - debit_total + credit_total
                        account.currentbalance = new_balance
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account with code {account_code} does not exist. Skipping update.")

                Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])

                return JsonResponse({'success': True})
            return JsonResponse({'success': False})
        except Exception as e:
            print("Error deleting Journal Entry: ", e)
            return JsonResponse({'success': False, 'error': str(e)})






# CONTRA ENTRY

from decimal import Decimal
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import VoucherConfiguration, Table_Accountsmaster, Table_Contra_Entry, Table_Acntchild, Table_companyDetailschild

from decimal import Decimal
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import VoucherConfiguration, Table_Accountsmaster, Wallet, Table_Contra_Entry, Table_Acntchild, Table_companyDetailschild

class ContraEntryView(View):
    template_name = 'accounts/contra-entry/contra_entry.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        vouchers = VoucherConfiguration.objects.filter(category='Contra Entry', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Accounts', 'Customers', 'Suppliers'], user=self.request.user)
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Accounts', 'Customers', 'Suppliers']).filter(user=self.request.user)
        wallet = Wallet.objects.first()

        next_serial_numbers = {}
        for voucher in vouchers:
            last_serial = Table_Contra_Entry.objects.filter(series=voucher.series, auth_user=self.request.user,).order_by('-voucher_no').first()
            next_serial_numbers[voucher.series] = str(int(last_serial.voucher_no) + 1) if last_serial else voucher.serial_no

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'head_accounts': head_accounts,
            'next_serial_numbers': next_serial_numbers,
            'user_id': request.user.id,
        })

    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('series')
            voucher_no = request.POST.get('voucher_no')
            vdate = request.POST.get('vdate')
            user_id = request.user.id
            branch_id = '1'
            heads = request.POST.getlist('head')
            head_codes = request.POST.getlist('head_code')
            narrations = request.POST.getlist('narration[]')
            debit = request.POST.getlist('dramount[]')
            credit = request.POST.getlist('cramount[]')
    
            if not (len(heads) == len(narrations) == len(debit) == len(credit) == len(head_codes)):
                raise ValueError("Mismatched input lengths in form data.")
    
            total_debit = sum(float(d) for d in debit if d)
            total_credit = sum(float(c) for c in credit if c)
    
            company_details = Table_companyDetailschild.objects.first()
            coid = company_details.company_id if company_details else ''
            fycode = company_details.fycode if company_details else ''
    
            with transaction.atomic():
                entries = []
                for head, head_code, narration, debit_amount, credit_amount in zip(heads, head_codes, narrations, debit, credit):
                    entries.append(
                        Table_Contra_Entry(
                            auth_user=self.request.user,
                            company=company,
                            series=series,
                            voucher_no=voucher_no,
                            vdate=vdate,
                            accountcode=head_code,
                            narration=narration,
                            dramount=float(debit_amount) if debit_amount else 0,
                            cramount=float(credit_amount) if credit_amount else 0,
                            user_id=user_id,
                            fycode=fycode,
                            coid=coid,
                            brid=branch_id
                        )
                    )
                Table_Contra_Entry.objects.bulk_create(entries)
    
                account_updates = {}
                for head_code, debit_amount, credit_amount in zip(head_codes, debit, credit):
                    if debit_amount:
                        if head_code not in account_updates:
                            account_updates[head_code] = 0
                        account_updates[head_code] += float(debit_amount)
                    if credit_amount:
                        if head_code not in account_updates:
                            account_updates[head_code] = 0
                        account_updates[head_code] -= float(credit_amount)
                
                accounts_to_update = []
                for head_code, amount in account_updates.items():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
                        account.currentbalance = (float(account.currentbalance or 0) + amount)
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        pass
                Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])
    
                voucher_configs = VoucherConfiguration.objects.filter(series=series, category='Contra Entry', company=company)
                for voucher_config in voucher_configs:
                    voucher_config.serial_no = voucher_no
                    voucher_config.save()
    
            messages.success(request, "Contra saved successfully!")
            return redirect('main:account_contra_entry')
        except Exception as e:
            print("Error saving contra entry: ", e)
            messages.error(request, f"Error saving contra entry: {str(e)}")
            return self.get(request)
    


    




class ContraEntryTable(LoginRequiredMixin, ListView):
    model = Table_Contra_Entry
    template_name = 'accounts/contra-entry/contra-entry-table.html'
    context_object_name = "contraentrys"

    def get_queryset(self):
        return self.model.objects.filter(auth_user=self.request.user)


class SearchContraEntryView(LoginRequiredMixin, View):
    template_name = 'accounts/contra-entry/search-contra-entry.html'

    def get(self, request, *args, **kwargs):
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        series = request.GET.get('Series', '')
        voucher_no = request.GET.get('VoucherNo', '')

        error_message = None
        if not series or not voucher_no:
            error_message = "Please provide both series and voucher number."

        vouchers = VoucherConfiguration.objects.filter(category='Contra Entry', company=company)
        return render(request, self.template_name, {'vouchers': vouchers, 'error_message': error_message})


from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

class EditContraEntry(LoginRequiredMixin, View):
    template_name = 'accounts/contra-entry/edit-contra-entry.html'

    def get(self, request, *args, **kwargs):
        series = request.GET.get('Series')
        voucher_no = request.GET.get('VoucherNo')
        company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
        vouchers = VoucherConfiguration.objects.filter(category='Contra Entry', company=company)
        accountmas = Table_Accountsmaster.objects.filter(category__in=['Accounts', 'Customers', 'Suppliers'], user=self.request.user)
        head_accounts = Table_Accountsmaster.objects.exclude(category__in=['Accounts', 'Customers', 'Suppliers']).filter(user=self.request.user)
        table_acntchildren = Table_Acntchild.objects.filter(account_master__category__in=['Accounts', 'Customers', 'Suppliers'], account_master__user=self.request.user)

        voucher_entries = Table_Contra_Entry.objects.filter(series=series, voucher_no=voucher_no,  auth_user=self.request.user)

        if not voucher_entries:
            return redirect('main:search_contra_entry')

        valid_account_codes = head_accounts.values_list('account_code', flat=True)

        return render(request, self.template_name, {
            'vouchers': vouchers,
            'accountmas': accountmas,
            'head_accounts': head_accounts,
            'table_acntchildren': table_acntchildren,
            'voucher_entries': voucher_entries,
            'user_id': request.user.id,
            'valid_account_codes': valid_account_codes
        })


    def post(self, request, *args, **kwargs):
        try:
            company = Table_Companydetailsmaster.objects.get(company_id=(request.session.get('co_id')))
            series = request.POST.get('series')
            vdate = request.POST.get('vdate')
            voucher_no = request.POST.get('voucher_no')
            if not voucher_no:
                raise ValueError("Voucher number is required.")
            user_id = request.user.id

            company_details = Table_companyDetailschild.objects.first()
            if not company_details:
                raise ValueError("Company details not found.")

            fycode = company_details.fycode
            coid = company_details.company_id
            branch_id = '1'

            heads = request.POST.getlist('head')
            narrations = request.POST.getlist('narration[]')
            debit = request.POST.getlist('dramount[]')
            credit = request.POST.getlist('cramount[]')

            if not (len(heads) == len(narrations) == len(debit) == len(credit)):
                raise ValueError("Mismatched input lengths in form data.")

            # Convert to Decimal for consistency
            debit = [Decimal(d) if d else Decimal('0') for d in debit]
            credit = [Decimal(c) if c else Decimal('0') for c in credit]

            total_debit = sum(debit)
            total_credit = sum(credit)

            voucher_config = VoucherConfiguration.objects.get(series=series, category='Contra Entry', company=company)

            with transaction.atomic():
                # Fetch existing entries and compute old debit and credit totals
                existing_entries = Table_Contra_Entry.objects.filter(series=series, voucher_no=voucher_no, auth_user=self.request.user,)
                old_account_updates = {}
                for entry in existing_entries:
                    if entry.accountcode not in old_account_updates:
                        old_account_updates[entry.accountcode] = Decimal('0')
                    old_account_updates[entry.accountcode] += (Decimal(entry.dramount) - Decimal(entry.cramount))

                # Delete existing entries
                existing_entries.delete()

                # Create new entries
                for head, narration, debit_amount, credit_amount in zip(heads, narrations, debit, credit):
                    Table_Contra_Entry.objects.create(
                        auth_user=self.request.user,
                        company=company,
                        series=series,
                        voucher_no=voucher_no,
                        vdate=vdate,
                        accountcode=head,
                        narration=narration,
                        dramount=debit_amount,
                        cramount=credit_amount,
                        user_id=user_id,
                        fycode=fycode,
                        coid=coid,
                        brid=branch_id
                    )

                # Compute new debit and credit totals
                new_account_updates = {}
                for head, debit_amount, credit_amount in zip(heads, debit, credit):
                    if debit_amount:
                        if head not in new_account_updates:
                            new_account_updates[head] = Decimal('0')
                        new_account_updates[head] += debit_amount
                    if credit_amount:
                        if head not in new_account_updates:
                            new_account_updates[head] = Decimal('0')
                        new_account_updates[head] -= credit_amount

                # Update account balances
                accounts_to_update = []
                for head_code, new_amount in new_account_updates.items():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
                        # Adjust the balance by subtracting old amounts and adding new amounts
                        old_amount = old_account_updates.get(head_code, Decimal('0'))
                        account.currentbalance = (Decimal(account.currentbalance or '0') - old_amount + new_amount)
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account with code {head_code} does not exist. Skipping update.")

                Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])

                # Update the voucher configuration with the new serial number if needed
                voucher_no_int = int(voucher_no)
                if voucher_no_int > voucher_config.serial_no:
                    voucher_config.serial_no = voucher_no_int
                    voucher_config.save()

            messages.success(request, "Contra updated successfully!")
            return redirect('main:account_contra_entry')
        except Exception as e:
            print("Error saving contra entry: ", e)
            messages.error(request, f"Error saving contra entry: {str(e)}")
            return self.get(request, error=str(e))





from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal

class DeleteContraEntryView(LoginRequiredMixin, View):
    def delete(self, request, voucher_no, *args, **kwargs):
        try:
            with transaction.atomic():
                # Retrieve contra entries to delete
                contra_entries = Table_Contra_Entry.objects.filter(voucher_no=voucher_no, auth_user=self.request.user)
                
                if not contra_entries.exists():
                    return JsonResponse({'success': False, 'message': 'No entries found.'})
                
                # Prepare to accumulate amounts to adjust account balances
                account_updates = {}
                for entry in contra_entries:
                    head_code = entry.accountcode
                    dr_amount = Decimal(entry.dramount) if entry.dramount else Decimal('0')
                    cr_amount = Decimal(entry.cramount) if entry.cramount else Decimal('0')
                    
                    if head_code not in account_updates:
                        account_updates[head_code] = Decimal('0')
                    # Subtract the debit amount and add the credit amount
                    account_updates[head_code] -= dr_amount
                    account_updates[head_code] += cr_amount
                
                # Delete the contra entries
                contra_entries.delete()

                # Update the current balance for affected accounts
                accounts_to_update = []
                for head_code, amount_change in account_updates.items():
                    try:
                        account = Table_Accountsmaster.objects.get(account_code=head_code, user=self.request.user)
                        account.currentbalance = Decimal(account.currentbalance or '0') + amount_change
                        accounts_to_update.append(account)
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Account with code {head_code} does not exist. Skipping update.")
                
                if accounts_to_update:
                    Table_Accountsmaster.objects.bulk_update(accounts_to_update, ['currentbalance'])

                return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error deleting contra entry: {e}")
            return JsonResponse({'success': False, 'message': str(e)})








class LedgerSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/ledger/ledger_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the first (or specific) company details record for finyearfrom
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom
        context["head_accounts"] = Table_Accountsmaster.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        account_code = request.POST.get("Accountcode")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        
        if not account_code:
            messages.error(request, "No account head selected. Please select an account head.")
            return self.get(request, *args, **kwargs)  # Return to the form page with error message

        # If everything is valid, redirect to the ledger page
        return HttpResponseRedirect(
            reverse(
                "main:ledger",
                kwargs={
                    "account_code": account_code,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )





class LedgerView(LoginRequiredMixin, View):
    def get(self, request, account_code, start_date, end_date):
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Fetch account details
        account_master = Table_Accountsmaster.objects.filter(account_code=account_code, user=self.request.user).first()

        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()  # Assuming there's only one record

        # Initialize opening balance variables
        opening_balance = Decimal("0.00")
        
        # Fetch all entries prior to start_date to calculate opening balance
        previous_entries = (
            list(Table_Voucher.objects.filter(Accountcode=account_code, Vdate__lt=start_date)) +
            list(Table_DrCrNote.objects.filter(accountcode=account_code, ndate__lt=start_date)) +
            list(Table_Journal_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date)) +
            list(Table_Contra_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date))
        )

        # Calculate the opening balance based on previous entries
        if previous_entries:
            for entry in previous_entries:
                if hasattr(entry, "Vdate"):
                    if entry.CStatus == "P":
                        opening_balance += Decimal(entry.VAmount or "0.00")
                    elif entry.CStatus == "R":
                        opening_balance -= Decimal(entry.VAmount or "0.00")
                elif hasattr(entry, "ndate"):
                    if entry.ntype == 'C':  # Credit Note
                        opening_balance += Decimal(entry.cramount or "0.00")
                        opening_balance -= Decimal(entry.dramount or "0.00")
                    else:
                        opening_balance += Decimal(entry.dramount or "0.00")
                        opening_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Journal_Entry):
                    opening_balance += Decimal(entry.dramount or "0.00")
                    opening_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Contra_Entry):
                    opening_balance += Decimal(entry.dramount or "0.00")
                    opening_balance -= Decimal(entry.cramount or "0.00")

        # If no previous entries, use the initial opening balance from the account master
        if opening_balance == Decimal("0.00"):
            opening_balance = Decimal(account_master.opbalance)

        # Initialize opening balance debit and credit
        opening_balance_debit = Decimal("0.00")
        opening_balance_credit = Decimal("0.00")

        # Determine if the opening balance should be in Debit or Credit based on 'debitcredit' in account master
        if account_master.debitcredit == "debit":
            opening_balance_debit = max(opening_balance, Decimal("0.00"))  # Opening balance goes in debit column
        elif account_master.debitcredit == "credit":
            opening_balance_credit = abs(opening_balance)  # Opening balance goes in credit column
        else:
            opening_balance_debit = max(opening_balance, Decimal("0.00"))
            opening_balance_credit = -min(opening_balance, Decimal("0.00"))

        # Fetch entries within date range
        voucher_entries = Table_Voucher.objects.filter(
            Accountcode=account_code, Vdate__range=[start_date, end_date], user=self.request.user
        )

        drcr_entries = Table_DrCrNote.objects.filter(
            accountcode=account_code, ndate__range=[start_date, end_date], user=self.request.user
        )

        journal_entries = Table_Journal_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        )

        contra_entries = Table_Contra_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        )

        # Combine and sort entries by date
        combined_entries = sorted(
            list(voucher_entries) +
            list(drcr_entries) +
            list(journal_entries) +
            list(contra_entries),
            key=lambda x: (
                getattr(x, 'Vdate', None) or getattr(x, 'ndate', None) or getattr(x, 'vdate', None)
            )
        )

        total_debit = opening_balance_debit
        total_credit = opening_balance_credit
        closing_balance = opening_balance  # Start with the opening balance

        entry_list = []

        for entry in combined_entries:
            entry_dict = {}

            if hasattr(entry, "Vdate"):  # Table_Voucher entry
                debit_amount = (
                    Decimal(entry.VAmount or "0.00")
                    if entry.CStatus == "P"
                    else Decimal("0.00")
                )
                credit_amount = (
                    Decimal(entry.VAmount or "0.00")
                    if entry.CStatus == "R"
                    else Decimal("0.00")
                )
                entry_dict = {
                    "date": entry.Vdate,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "status": entry.CStatus,
                    "debit": debit_amount,
                    "credit": credit_amount,
                }

            elif hasattr(entry, "ndate"):  # Table_DrCrNote entry
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                if entry.ntype == 'C':  # Credit Note
                    debit_amount, credit_amount = credit_amount, debit_amount
                entry_dict = {
                    "date": entry.ndate,
                    "voucher_number": entry.noteno or entry.series,
                    "narration": entry.narration,
                    "type": entry.ntype,
                    "debit": debit_amount,
                    "credit": credit_amount,
                }

            elif isinstance(entry, Table_Journal_Entry):  # Table_Journal_Entry
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "is_journal_entry": True,  # Flag for journal entry
                }

            elif isinstance(entry, Table_Contra_Entry):  # Table_Contra_Entry
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "is_contra_entry": True,  # Flag for contra entry
                }

            # Update the running balance
            closing_balance += entry_dict.get("debit", Decimal("0.00"))
            closing_balance -= entry_dict.get("credit", Decimal("0.00"))

            # Add closing balance to the entry dictionary
            entry_dict["closing_balance"] = closing_balance

            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))

            entry_list.append(entry_dict)

        # Final closing balance at the end of the entries (Balance c/d)
        balance_cd = closing_balance

        context = {
            "account_master": account_master,
            "entries": entry_list,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance_cd": balance_cd,  # Final closing balance (carry down)
            "opening_balance": opening_balance,  # Starting opening balance
            "opening_balance_debit": opening_balance_debit,  # For display
            "opening_balance_credit": opening_balance_credit,  # For display
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
        }

        return render(request, "accounts/ledger/ledger.html", context)




class CashBookSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/cash-book/cashbook_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the first (or specific) company details record for finyearfrom
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom

        # Filter head accounts with category 'Cashbook'
        context["head_accounts"] = Table_Accountsmaster.objects.filter(category='Cashbook', user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        account_code = request.POST.get("Accountcode")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        
        if not account_code:
            messages.error(request, "No account head selected. Please select an account head.")
            return self.get(request, *args, **kwargs)  # Return to the form page with error message

        # If everything is valid, redirect to the ledger page
        return HttpResponseRedirect(
            reverse(
                "main:cashbook",
                kwargs={
                    "account_code": account_code,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )



from django.db.models import Q
class CashBookView(LoginRequiredMixin, View):
    def get(self, request, account_code, start_date, end_date):
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Fetch account details
        account_master = Table_Accountsmaster.objects.get(account_code=account_code, user=self.request.user)
        
        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()  # Assuming there's only one record

        # Convert initial balance to Decimal if it is not already
        opbalance = Decimal(account_master.opbalance)

        # Function to get last closing balance
        def get_last_closing_balance():
            entries = (
                list(Table_Voucher.objects.filter(Accountcode=account_code, Vdate__lt=start_date, user=self.request.user)) +
                list(Table_DrCrNote.objects.filter(accountcode=account_code, ndate__lt=start_date, user=self.request.user)) +
                list(Table_Journal_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date, auth_user=self.request.user)) +
                list(Table_Contra_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date, auth_user=self.request.user))
            )
            entries.sort(key=lambda x: (
                getattr(x, 'Vdate', None) or getattr(x, 'ndate', None) or datetime.min.date()
            ))

            last_closing_balance = opbalance
            for entry in entries:
                # Logic for each entry type
                if hasattr(entry, "Vdate"):
                    if entry.CStatus == "P":
                        last_closing_balance += Decimal(entry.payment or "0.00")  # Using payment
                    elif entry.CStatus == "R":
                        last_closing_balance -= Decimal(entry.payment or "0.00")  # Using payment
                elif hasattr(entry, "ndate"):
                    if entry.ntype == 'C':
                        last_closing_balance += Decimal(entry.cramount or "0.00")
                        last_closing_balance -= Decimal(entry.dramount or "0.00")
                    else:
                        last_closing_balance += Decimal(entry.dramount or "0.00")
                        last_closing_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Journal_Entry):
                    last_closing_balance += Decimal(entry.dramount or "0.00")
                    last_closing_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Contra_Entry):
                    last_closing_balance += Decimal(entry.dramount or "0.00")
                    last_closing_balance -= Decimal(entry.cramount or "0.00")

            return last_closing_balance

        opening_balance = get_last_closing_balance()

        # Updated query to filter by Accountcode or Headcode
        voucher_entries = Table_Voucher.objects.filter(
            Q(Accountcode=account_code) | Q(Headcode=account_code),
            Vdate__range=[start_date, end_date],
            user=self.request.user
        ).order_by("Vdate")

        # Fetch other entries as usual
        drcr_entries = Table_DrCrNote.objects.filter(
            accountcode=account_code, ndate__range=[start_date, end_date], user=self.request.user
        ).order_by("ndate")

        journal_entries = Table_Journal_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        ).order_by("vdate")

        contra_entries = Table_Contra_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        ).order_by("vdate")

        # Combine and sort entries as before
        combined_entries = (
            list(voucher_entries) +
            list(drcr_entries) +
            list(journal_entries) +
            list(contra_entries)
        )

        # Sort entries based on date for all types
        combined_entries.sort(
            key=lambda x: (
                getattr(x, 'Vdate', None) or
                getattr(x, 'ndate', None) or
                (getattr(x, 'vdate', None) if hasattr(x, 'vdate') else None) or
                datetime.date.min
            )
        )

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        closing_balance = opening_balance  # Start with the opening balance

        entry_list = []

        for entry in combined_entries:
            entry_dict = {}
            head = ""

            # Process each entry type
            if hasattr(entry, "Vdate"):  # Table_Voucher entry
                head = Table_Accountsmaster.objects.get(account_code=entry.Accountcode, user=self.request.user).head  # Get head using Accountcode instead of Headcode
                debit_amount = Decimal(entry.payment or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                credit_amount = Decimal(entry.payment or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                entry_dict = {
                    "date": entry.Vdate,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "status": entry.CStatus,
                    "debit": credit_amount,
                    "credit": debit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            elif hasattr(entry, "ndate"):  # Table_DrCrNote entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                if entry.ntype == 'C':  # Assuming 'C' stands for Credit Note
                    debit_amount, credit_amount = credit_amount, debit_amount
                entry_dict = {
                    "date": entry.ndate,
                    "voucher_number": entry.noteno or entry.series,
                    "narration": entry.narration,
                    "type": entry.ntype,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Journal_Entry):  # Table_Journal_Entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": True,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Contra_Entry):  # Table_Contra_Entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": True,
                }

            # Update the running balance
            closing_balance += entry_dict.get("debit", Decimal("0.00"))
            closing_balance -= entry_dict.get("credit", Decimal("0.00"))

            # Add closing balance to the entry dictionary
            entry_dict["closing_balance"] = closing_balance

            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))

            entry_list.append(entry_dict)

        balance_cd = closing_balance  # Final closing balance

        # Determine debit and credit values for the opening balance row
        opening_balance_debit = max(opening_balance, Decimal("0.00"))
        opening_balance_credit = max(-opening_balance, Decimal("0.00"))

        context = {
            "account_master": account_master,
            "entries": entry_list,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance_cd": balance_cd,
            "opening_balance": opening_balance,
            "opening_balance_debit": opening_balance_debit,
            "opening_balance_credit": opening_balance_credit,
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
        }

        return render(request, "accounts/cash-book/cashbook.html", context)








class BankBookSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/bank-book/bankbook_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the first (or specific) company details record for finyearfrom
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom

        # Filter head accounts with category 'Cashbook'
        context["head_accounts"] = Table_Accountsmaster.objects.filter(category='Bank', user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        account_code = request.POST.get("Accountcode")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not account_code:
            messages.error(request, "No account head selected. Please select an account head.")
            return self.get(request, *args, **kwargs)  # Return to the form page with error message

        # If everything is valid, redirect to the ledger page
        return HttpResponseRedirect(
            reverse(
                "main:bankbook",
                kwargs={
                    "account_code": account_code,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )


class BankBookView(LoginRequiredMixin, View):
    def get(self, request, account_code, start_date, end_date):
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Fetch account details
        account_master = Table_Accountsmaster.objects.get(account_code=account_code, user=self.request.user)
        
        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()  # Assuming there's only one record

        # Convert initial balance to Decimal if it is not already
        opbalance = Decimal(account_master.opbalance)

        # Function to get last closing balance
        def get_last_closing_balance():
            entries = (
                list(Table_Voucher.objects.filter(Accountcode=account_code, Vdate__lt=start_date, user=self.request.user)) +
                list(Table_DrCrNote.objects.filter(accountcode=account_code, ndate__lt=start_date, user=self.request.user)) +
                list(Table_Journal_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date, auth_user=self.request.user)) +
                list(Table_Contra_Entry.objects.filter(accountcode=account_code, vdate__lt=start_date, auth_user=self.request.user))
            )
            entries.sort(key=lambda x: (
                getattr(x, 'Vdate', None) or getattr(x, 'ndate', None) or datetime.min.date()
            ))

            last_closing_balance = opbalance
            for entry in entries:
                # Logic for each entry type
                if hasattr(entry, "Vdate"):
                    if entry.CStatus == "P":
                        last_closing_balance += Decimal(entry.payment or "0.00")  # Using payment
                    elif entry.CStatus == "R":
                        last_closing_balance -= Decimal(entry.payment or "0.00")  # Using payment
                elif hasattr(entry, "ndate"):
                    if entry.ntype == 'C':
                        last_closing_balance += Decimal(entry.cramount or "0.00")
                        last_closing_balance -= Decimal(entry.dramount or "0.00")
                    else:
                        last_closing_balance += Decimal(entry.dramount or "0.00")
                        last_closing_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Journal_Entry):
                    last_closing_balance += Decimal(entry.dramount or "0.00")
                    last_closing_balance -= Decimal(entry.cramount or "0.00")
                elif isinstance(entry, Table_Contra_Entry):
                    last_closing_balance += Decimal(entry.dramount or "0.00")
                    last_closing_balance -= Decimal(entry.cramount or "0.00")

            return last_closing_balance

        opening_balance = get_last_closing_balance()

        # Updated query to filter by Accountcode or Headcode
        voucher_entries = Table_Voucher.objects.filter(
            Q(Accountcode=account_code) | Q(Headcode=account_code),
            Vdate__range=[start_date, end_date], user=self.request.user
        ).order_by("Vdate")

        # Fetch other entries as usual
        drcr_entries = Table_DrCrNote.objects.filter(
            accountcode=account_code, ndate__range=[start_date, end_date], user=self.request.user
        ).order_by("ndate")

        journal_entries = Table_Journal_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        ).order_by("vdate")

        contra_entries = Table_Contra_Entry.objects.filter(
            accountcode=account_code, vdate__range=[start_date, end_date], auth_user=self.request.user
        ).order_by("vdate")

        # Combine and sort entries as before
        combined_entries = (
            list(voucher_entries) +
            list(drcr_entries) +
            list(journal_entries) +
            list(contra_entries)
        )

        # Sort entries based on date for all types
        combined_entries.sort(
            key=lambda x: (
                getattr(x, 'Vdate', None) or
                getattr(x, 'ndate', None) or
                (getattr(x, 'vdate', None) if hasattr(x, 'vdate') else None) or
                datetime.date.min
            )
        )

        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        closing_balance = opening_balance  # Start with the opening balance

        entry_list = []

        for entry in combined_entries:
            entry_dict = {}
            head = ""

            # Process each entry type
            if hasattr(entry, "Vdate"):  # Table_Voucher entry
                head = Table_Accountsmaster.objects.get(account_code=entry.Accountcode, user=self.request.user).head  # Get head using Accountcode instead of Headcode
                debit_amount = Decimal(entry.payment or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                credit_amount = Decimal(entry.payment or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                entry_dict = {
                    "date": entry.Vdate,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "status": entry.CStatus,
                    "debit": credit_amount,
                    "credit": debit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            elif hasattr(entry, "ndate"):  # Table_DrCrNote entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                if entry.ntype == 'C':  # Assuming 'C' stands for Credit Note
                    debit_amount, credit_amount = credit_amount, debit_amount
                entry_dict = {
                    "date": entry.ndate,
                    "voucher_number": entry.noteno or entry.series,
                    "narration": entry.narration,
                    "type": entry.ntype,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Journal_Entry):  # Table_Journal_Entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": True,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Contra_Entry):  # Table_Contra_Entry
                head = Table_Accountsmaster.objects.get(account_code=entry.accountcode, user=self.request.user).head
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                entry_dict = {
                    "date": entry.vdate,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "head": head,
                    "is_journal_entry": False,
                    "is_contra_entry": True,
                }

            # Update the running balance
            closing_balance += entry_dict.get("debit", Decimal("0.00"))
            closing_balance -= entry_dict.get("credit", Decimal("0.00"))

            # Add closing balance to the entry dictionary
            entry_dict["closing_balance"] = closing_balance

            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))

            entry_list.append(entry_dict)

        balance_cd = closing_balance  # Final closing balance

        # Determine debit and credit values for the opening balance row
        opening_balance_debit = max(opening_balance, Decimal("0.00"))
        opening_balance_credit = max(-opening_balance, Decimal("0.00"))

        context = {
            "account_master": account_master,
            "entries": entry_list,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance_cd": balance_cd,
            "opening_balance": opening_balance,
            "opening_balance_debit": opening_balance_debit,
            "opening_balance_credit": opening_balance_credit,
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
        }

        return render(request, "accounts/bank-book/bankbook.html", context)



class DayBookSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/day-book/daybook_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom
        return context

    def post(self, request, *args, **kwargs):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, "Please select both start and end dates.")
            return self.get(request, *args, **kwargs)

        return HttpResponseRedirect(
            reverse(
                "main:daybook",  # Adjust the URL name as per your URL configuration
                kwargs={
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )


from datetime import date
from django.utils.dateparse import parse_date


class DayBookView(LoginRequiredMixin, View):
    def get(self, request, start_date, end_date):
        # Parse start and end dates
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()

        # Fetch entries within the date range
        voucher_entries = Table_Voucher.objects.filter(Vdate__range=[start_date, end_date], user=self.request.user).order_by("Vdate")
        drcr_entries = Table_DrCrNote.objects.filter(ndate__range=[start_date, end_date], user=self.request.user).order_by("ndate")
        journal_entries = Table_Journal_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")
        contra_entries = Table_Contra_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")

        # Combine and sort all entries by date
        combined_entries = (
            list(voucher_entries) + list(drcr_entries) + list(journal_entries) + list(contra_entries)
        )
        combined_entries.sort(key=lambda x: getattr(x, 'Vdate', getattr(x, 'ndate', getattr(x, 'vdate', date.min))))

        # Process and calculate debit, credit, and balances for display
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        entry_list = []

        # Loop through the entries and process each one
        for entry in combined_entries:
            entry_dict = {}

            if hasattr(entry, "Vdate"):  # Table_Voucher entry
                debit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                credit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                account = Table_Accountsmaster.objects.filter(account_code=entry.Accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.Vdate,
                    "head": head,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": entry.CStatus,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }
                if entry.Headcode:
                    try:
                        head_account = Table_Accountsmaster.objects.get(account_code=entry.Headcode, user=self.request.user)
                
                        # Append 'Book Head' and current balance row only once
                        if entry.CStatus == 'P':
                            # Add 'Book Head' debit and credit to totals
                            total_debit += Decimal("0.00")  # For 'P' entries, we display in the credit column
                            total_credit += debit_amount  # Accumulate the correct amount for payments
                
                            # Show current balance in the credit column for payment entry
                            entry_list.append({
                                "date": entry.Vdate,
                                "head": head_account.head,
                                "voucher_number": entry.VoucherNo or entry.Series,
                                "narration": "",
                                "debit": Decimal("0.00"),  # No debit for payments
                                "credit": debit_amount,  # Show in credit for payments
                                "type": entry.CStatus,
                                "is_journal_entry": False,
                                "is_contra_entry": False,
                            })
                        elif entry.CStatus == 'R':
                            # Add 'Book Head' debit and credit to totals
                            total_debit += credit_amount  # Accumulate the correct amount for receipts
                            total_credit += Decimal("0.00")  # For 'R' entries, we display in the debit column
                
                            # Show current balance in the debit column for receipt entry
                            entry_list.append({
                                "date": entry.Vdate,
                                "head": head_account.head,
                                "voucher_number": entry.VoucherNo or entry.Series,
                                "narration": "",
                                "debit": credit_amount,  # Show in debit for receipts
                                "credit": Decimal("0.00"),  # No credit for receipts
                                "type": entry.CStatus,
                                "is_journal_entry": False,
                                "is_contra_entry": False,
                            })
                    except Table_Accountsmaster.DoesNotExist:
                        print(f"Headcode {entry.Headcode} not found in Table_Accountsmaster.")



            elif hasattr(entry, "ndate"):  # Table_DrCrNote entry
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                if entry.ntype == 'C':  # Credit Note
                    debit_amount, credit_amount = credit_amount, debit_amount
                account = Table_Accountsmaster.objects.filter(account_code=entry.accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.ndate,
                    "head": head,
                    "voucher_number": entry.noteno or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": entry.ntype,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Journal_Entry):
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                account = Table_Accountsmaster.objects.filter(account_code=entry.accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.vdate,
                    "head": head,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": 'Journal',
                    "is_journal_entry": True,
                    "is_contra_entry": False,
                }

            elif isinstance(entry, Table_Contra_Entry):
                debit_amount = Decimal(entry.dramount or "0.00")
                credit_amount = Decimal(entry.cramount or "0.00")
                account = Table_Accountsmaster.objects.filter(account_code=entry.accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.vdate,
                    "head": head,
                    "voucher_number": entry.voucher_no or entry.series,
                    "narration": entry.narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": 'Contra',
                    "is_journal_entry": False,
                    "is_contra_entry": True,
                }

            # Accumulate totals
            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))
            entry_list.append(entry_dict)

        # Context for rendering the template
        context = {
            "entries": entry_list,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
        }

        return render(request, "accounts/day-book/daybook.html", context)


from datetime import datetime


class TrialBalanceView(LoginRequiredMixin, View):
    def get(self, request):
        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()

        # Fetch all accounts grouped by their group in Table_Accountsmaster
        accounts = Table_Accountsmaster.objects.filter(user=self.request.user).order_by('group', 'head')

        # Fetch all entries without date filtering
        voucher_entries = Table_Voucher.objects.filter(user=self.request.user).order_by("Vdate")
        drcr_entries = Table_DrCrNote.objects.filter(user=self.request.user).order_by("ndate")
        journal_entries = Table_Journal_Entry.objects.filter(auth_user=self.request.user).order_by("vdate")
        contra_entries = Table_Contra_Entry.objects.filter(auth_user=self.request.user).order_by("vdate")

        # Combine and sort all entries by date
        combined_entries = (
            list(voucher_entries) + list(drcr_entries) + list(journal_entries) + list(contra_entries)
        )
        combined_entries.sort(key=lambda x: getattr(x, 'Vdate', getattr(x, 'ndate', getattr(x, 'vdate', datetime.min.date()))))

        # Initialize totals
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        entry_list = []
        group_totals = {}

        # Process and calculate debit, credit, and balances for display
        for account in accounts:
            # Ensure currentbalance is a Decimal
            current_balance = Decimal(account.currentbalance) if account.currentbalance not in [None, ''] else Decimal("0.00")
            
            # Initialize debit and credit for each account
            account_debit = Decimal("0.00")
            account_credit = Decimal("0.00")

            # Filter entries for this account and calculate debit/credit totals
            for entry in combined_entries:
                if hasattr(entry, "Accountcode") and entry.Accountcode == account.account_code:
                    debit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                    credit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                    account_debit += debit_amount
                    account_credit += credit_amount
                elif hasattr(entry, "accountcode") and entry.accountcode == account.account_code:
                    debit_amount = Decimal(entry.dramount or "0.00")
                    credit_amount = Decimal(entry.cramount or "0.00")
                    account_debit += debit_amount
                    account_credit += credit_amount

            # Update the totals
            total_debit += account_debit
            total_credit += account_credit

            # Add entry for this account with current balance
            entry_list.append({
                "group": account.group,
                "head": account.head,
                "current_balance": current_balance,
                "debit": account_debit,
                "credit": account_credit,
            })

            # Aggregate group totals
            if current_balance > 0:
                group_totals.setdefault(account.group, {'debit': Decimal("0.00"), 'credit': Decimal("0.00")})
                group_totals[account.group]['debit'] += current_balance
            elif current_balance < 0:
                group_totals.setdefault(account.group, {'debit': Decimal("0.00"), 'credit': Decimal("0.00")})
                group_totals[account.group]['credit'] += abs(current_balance)

        # Add group totals to entry list, updating the existing group entries
        for group, totals in group_totals.items():
            for entry in entry_list:
                if entry["group"] == group:
                    entry["debit"] += totals['debit']  # Add group total to debit column
                    entry["credit"] += totals['credit']  # Add group total to credit column
                    break

        # Context for rendering the template
        total_group_debit = sum(entry["debit"] for entry in entry_list)
        total_group_credit = sum(entry["credit"] for entry in entry_list)
        
        # Context for rendering the template
        context = {
            "entries": entry_list,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_group_debit": total_group_debit,
            "total_group_credit": total_group_credit,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
        }
        

        return render(request, "accounts/trial-balance/trialbalance.html", context)
    


class ProfitAndLossSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profit-and-loss/profit_and_loss_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom
        return context

    def post(self, request, *args, **kwargs):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, "Please select both start and end dates.")
            return self.get(request, *args, **kwargs)

        return HttpResponseRedirect(
            reverse(
                "main:profit_and_loss",  # Adjust the URL name as per your URL configuration
                kwargs={
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )

from collections import defaultdict

from datetime import date
from django.utils.dateparse import parse_date
from itertools import zip_longest


class ProfitAndLossView(LoginRequiredMixin, View):
    def get(self, request, start_date, end_date):
        
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        
        company_details = Table_Companydetailsmaster.objects.first()

        
        voucher_entries = Table_Voucher.objects.filter(Vdate__range=[start_date, end_date], user=self.request.user).order_by("Vdate")
        drcr_entries = Table_DrCrNote.objects.filter(ndate__range=[start_date, end_date], user=self.request.user).order_by("ndate")
        journal_entries = Table_Journal_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")
        contra_entries = Table_Contra_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")

        
        combined_entries = (
            list(voucher_entries) + list(drcr_entries) + list(journal_entries) + list(contra_entries)
        )
        combined_entries.sort(key=lambda x: getattr(x, 'Vdate', getattr(x, 'ndate', getattr(x, 'vdate', date.min))))

        
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        entry_list = []

        
        for entry in combined_entries:
            entry_dict = {}

            if hasattr(entry, "Vdate"):  
                debit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                credit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                account = Table_Accountsmaster.objects.filter(account_code=entry.Accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.Vdate,
                    "head": head,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": entry.CStatus,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            
            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))
            entry_list.append(entry_dict)

            
           
            income_totals = defaultdict(lambda: {"debit": Decimal("0.00"), "credit": Decimal("0.00")})

            for entry in entry_list:
                head = entry.get("head")
                if head:
                    account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT INCOME').first()
                    if account:
                        income_totals[head]["debit"] += entry.get("debit", Decimal("0.00"))
                        income_totals[head]["credit"] += entry.get("credit", Decimal("0.00"))

            indirect_income_entries = []
            for head, amounts in income_totals.items():
                account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT INCOME').first()
                currentbalance = account.currentbalance if account else "0.00"
                indirect_income_entries.append({
                    "head": head,
                    "debit": Decimal(currentbalance or "0.00"),  
                    "credit": amounts["credit"],  
                })

            # Aggregate INDIRECT EXPENSES
            expense_totals = defaultdict(lambda: {"debit": Decimal("0.00"), "credit": Decimal("0.00")})
            
            for entry in entry_list:
                head = entry.get("head")
                if head:
                    account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT EXPENSES').first()
                    if account:
                        expense_totals[head]["debit"] += entry.get("debit", Decimal("0.00"))
                        expense_totals[head]["credit"] += entry.get("credit", Decimal("0.00"))
            
            indirect_expense_entries = []
            for head, amounts in expense_totals.items():
                account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT EXPENSES').first()
                currentbalance = account.currentbalance if account else "0.00"
                indirect_expense_entries.append({
                    "head": head,
                    "debit": Decimal(currentbalance or "0.00"),
                    "credit": amounts["credit"],
                })

            


        # Calculate grand totals
        total_indirect_income = sum(entry["debit"] for entry in indirect_income_entries)
        total_indirect_expense = sum(entry["debit"] for entry in indirect_expense_entries)
        max_length = max(len(indirect_income_entries), len(indirect_expense_entries))


        income_expense_rows = list(zip_longest(indirect_income_entries, indirect_expense_entries, fillvalue={}))
        difference_amount = abs(total_indirect_income - total_indirect_expense)
        

        context = {
            "difference_amount": difference_amount,
            "entries": indirect_income_entries,
            "indirect_expense_entries": indirect_expense_entries,
            "total_indirect_income": total_indirect_income,  
            "total_indirect_expense": total_indirect_expense, 
            "total_debit": total_debit,
            "total_credit": total_credit,
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
            "max_length": max_length, 
            "income_expense_rows": income_expense_rows,
            "total_indirect_income": total_indirect_income,
            "total_indirect_expense": total_indirect_expense,


        }
        

        return render(request, "accounts/profit-and-loss/profit_and_loss.html", context)
    






class BalanceSheetSearchView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/balance-sheet/balance_sheet_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_details = Table_Companydetailsmaster.objects.first()
        if company_details:
            context["finyearfrom"] = company_details.finyearfrom
        return context

    def post(self, request, *args, **kwargs):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if not start_date or not end_date:
            messages.error(request, "Please select both start and end dates.")
            return self.get(request, *args, **kwargs)

        return HttpResponseRedirect(
            reverse(
                "main:balance_sheet",  # Adjust the URL name as per your URL configuration
                kwargs={
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )

from collections import defaultdict

from datetime import date
from django.utils.dateparse import parse_date
from itertools import zip_longest


class BalanceSheetView(LoginRequiredMixin, View):
    def get(self, request, start_date, end_date):
        # Parse start and end dates
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        # Fetch company details
        company_details = Table_Companydetailsmaster.objects.first()

        # Fetch entries within the date range
        voucher_entries = Table_Voucher.objects.filter(Vdate__range=[start_date, end_date], user=self.request.user).order_by("Vdate")
        drcr_entries = Table_DrCrNote.objects.filter(ndate__range=[start_date, end_date], user=self.request.user).order_by("ndate")
        journal_entries = Table_Journal_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")
        contra_entries = Table_Contra_Entry.objects.filter(vdate__range=[start_date, end_date], auth_user=self.request.user).order_by("vdate")

        # Combine and sort all entries by date
        combined_entries = (
            list(voucher_entries) + list(drcr_entries) + list(journal_entries) + list(contra_entries)
        )
        combined_entries.sort(key=lambda x: getattr(x, 'Vdate', getattr(x, 'ndate', getattr(x, 'vdate', date.min))))

        # Process and calculate debit, credit, and balances for display
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        entry_list = []

        # Loop through the entries and process each one
        for entry in combined_entries:
            entry_dict = {}

            if hasattr(entry, "Vdate"):  # Table_Voucher entry
                debit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "P" else Decimal("0.00")
                credit_amount = Decimal(entry.VAmount or "0.00") if entry.CStatus == "R" else Decimal("0.00")
                account = Table_Accountsmaster.objects.filter(account_code=entry.Accountcode, user=self.request.user).first()
                head = account.head if account else "Unknown"
                entry_dict = {
                    "date": entry.Vdate,
                    "head": head,
                    "voucher_number": entry.VoucherNo or entry.Series,
                    "narration": entry.Narration,
                    "debit": debit_amount,
                    "credit": credit_amount,
                    "type": entry.CStatus,
                    "is_journal_entry": False,
                    "is_contra_entry": False,
                }

            # Accumulate totals
            total_debit += entry_dict.get("debit", Decimal("0.00"))
            total_credit += entry_dict.get("credit", Decimal("0.00"))
            entry_list.append(entry_dict)


            income_totals = defaultdict(lambda: {"debit": Decimal("0.00"), "credit": Decimal("0.00")})

            for entry in entry_list:
                head = entry.get("head")
                if head:
                    account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT INCOME').first()
                    if account:
                        income_totals[head]["debit"] += entry.get("debit", Decimal("0.00"))
                        income_totals[head]["credit"] += entry.get("credit", Decimal("0.00"))

            indirect_income_entries = []
            for head, amounts in income_totals.items():
                account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT INCOME').first()
                currentbalance = account.currentbalance if account else "0.00"
                indirect_income_entries.append({
                    "head": head,
                    "debit": Decimal(currentbalance or "0.00"),  
                    "credit": amounts["credit"],  
                })

            # Aggregate INDIRECT EXPENSES
            expense_totals = defaultdict(lambda: {"debit": Decimal("0.00"), "credit": Decimal("0.00")})
            
            for entry in entry_list:
                head = entry.get("head")
                if head:
                    account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT EXPENSES').first()
                    if account:
                        expense_totals[head]["debit"] += entry.get("debit", Decimal("0.00"))
                        expense_totals[head]["credit"] += entry.get("credit", Decimal("0.00"))
            
            indirect_expense_entries = []
            for head, amounts in expense_totals.items():
                account = Table_Accountsmaster.objects.filter(user=request.user, head=head, group='INDIRECT EXPENSES').first()
                currentbalance = account.currentbalance if account else "0.00"
                indirect_expense_entries.append({
                    "head": head,
                    "debit": Decimal(currentbalance or "0.00"),
                    "credit": amounts["credit"],
                })    

    

        # Group mappings
        liability_groups = [
            'LIABILITIES', 'CURRENT LIABILITIES', 'SUNDRY CREDITORS', 'LOANS',
            'CAPITAL ACCOUNT', 'DUTIES AND TAXES', 'INCOME', 'TRADING INCOME',
            'INDIRECT INCOME', 'EXPENSES', 'TRADING EXPENSES', 'INDIRECT EXPENSES',
        ]

        asset_groups = [
            'CURRENT ASSET', 'FIXED ASSETS', 'SUNDRY DEBTORS', 'CASH AT BANK', 'CASH IN HAND',
        ]

        # Liabilities
        liabilities = Table_Accountsmaster.objects.filter(
            user=request.user, group__in=liability_groups
        ).values('head', 'group', 'currentbalance')

        # Assets
        assets = Table_Accountsmaster.objects.filter(
            user=request.user, group__in=asset_groups
        ).values('head', 'group', 'currentbalance')

        liability_entries = []
        asset_entries = []
        total_liability = Decimal("0.00")
        total_asset = Decimal("0.00")

        for item in liabilities:
            balance = Decimal(item["currentbalance"] or "0.00")
            liability_entries.append({
                "head": item["head"],
                "balance": balance
            })
            total_liability += balance

        for item in assets:
            balance = Decimal(item["currentbalance"] or "0.00")
            asset_entries.append({
                "head": item["head"],
                "balance": balance
            })
            total_asset += balance

        # Pad shorter list to match row count for table
        max_balance_rows = max(len(liability_entries), len(asset_entries))
        balance_sheet_rows = list(zip_longest(liability_entries, asset_entries, fillvalue={}))

        # Calculate grand totals
        total_indirect_income = sum(entry["debit"] for entry in indirect_income_entries)
        total_indirect_expense = sum(entry["debit"] for entry in indirect_expense_entries)
        max_length = max(len(indirect_income_entries), len(indirect_expense_entries))


        income_expense_rows = list(zip_longest(indirect_income_entries, indirect_expense_entries, fillvalue={}))
        difference_amount = abs(total_indirect_income - total_indirect_expense)

        context = {
            "difference_amount": difference_amount,
            "balance_sheet_rows": balance_sheet_rows,
            "total_liability": total_liability,
            "total_asset": total_asset,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_details.companyname,
            "company_phone": company_details.phoneno,
            "company_address": company_details.address1,
            "company_gst": company_details.gst,
            "entries": indirect_income_entries,
            "indirect_expense_entries": indirect_expense_entries,
            "total_indirect_income": total_indirect_income,  
            "total_indirect_expense": total_indirect_expense, 
        }
        

        return render(request, "accounts/balance-sheet/balance_sheet.html", context)
    




from datetime import datetime

class FinancialYearFormView(LoginRequiredMixin, CreateView):
    model = Table_companyDetailschild
    fields = ['company_id', 'finyearfrom', 'finyearto']
    template_name = 'accounts/fin-year-ending/fin_year_form.html'
    success_url = reverse_lazy('web:financial_year_form')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Table_Companydetailsmaster.objects.all()
        context['financial_years'] = Table_companyDetailschild.objects.all()

        return context

    def form_valid(self, form):
        finyearfrom_str = form.cleaned_data.get('finyearfrom')
        finyearto_str = form.cleaned_data.get('finyearto')

        try:
            # Convert string to date
            finyearfrom_date = datetime.strptime(finyearfrom_str, "%Y-%m-%d")
            finyearto_date = datetime.strptime(finyearto_str, "%Y-%m-%d")
        except ValueError:
            form.add_error(None, "Invalid date format.")
            return self.form_invalid(form)

        form.instance.fycode = f"{finyearfrom_date.year}_{finyearto_date.year}"
        form.instance.databasename1 = f"db_{form.instance.company_id}_{form.instance.fycode}"

        return super().form_valid(form)





# ------------------------------------ RATE MASTER ----------------------------------

from .models import RateMaster, RateChild


def rate_master(request):
    customers = Table_Accountsmaster.objects.filter(group='SUNDRY DEBTORS', user__company__company_id=request.session.get('co_id'))
    vehicles = Vehicle_type.objects.filter(co_id=request.session.get('co_id'))

    if request.method == 'POST':
        company = Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id'))
        customer_name = request.POST.get('customer_name')
        vehicles_list = request.POST.getlist('vehicle[]')
        rates_list = request.POST.getlist('rate[]')
        types_list = request.POST.getlist('type[]')
        fixed_km_list = request.POST.getlist('fixed_km[]')
        fixed_rate_list = request.POST.getlist('fixed_rate[]')
        additional_charge_list = request.POST.getlist('additional_charge[]')

        for vehicle, rate, type, km, fixed_rate, additional_charge in zip(vehicles_list, rates_list, types_list, fixed_km_list, fixed_rate_list, additional_charge_list):
            if not vehicle: 
                continue

            exists = RateChild.objects.filter(
                master__company=company,
                master__customer_name=customer_name,
                vehicle=vehicle, 
                type=type
            ).exists()

            if exists:
                context = {
                    'customers': customers,
                    'vehicles': vehicles,
                    'error': 'Rates already exist for this vehicle and customer.',
                }
                return render(request, 'accounts/rate_master/rate_master.html', context)
                

            if not exists:
                master = RateMaster.objects.create(company=company, customer_name=customer_name)
                RateChild.objects.create(master=master, vehicle=vehicle, rate=rate or None, type=type, km=km or None, fixed_rate=fixed_rate or None, additional_charge=additional_charge or None)

        context = {
            'customers': customers,
            'vehicles': vehicles,
            'success': 'Rates saved successfully ?',
        }
        return render(request, 'accounts/rate_master/rate_master.html', context)

    return render(request, 'accounts/rate_master/rate_master.html', {
        'customers': customers,
        'vehicles': vehicles
    })


def rate_list(request):
    rates = RateChild.objects.filter(master__company__company_id=request.session.get('co_id'))
    return render(request, 'accounts/rate_master/rate_list.html', {'rates': rates})

def rate_delete(request, rate_id):
    try:
        rate = RateChild.objects.get(id=rate_id)
        rate.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




# ------------------------------------ LOCATION MASTER ----------------------------------

from .models import LocationMaster

def location_master(request):
    vehicles = Vehicle_type.objects.filter(co_id=request.session.get('co_id'))
    customers = Table_Accountsmaster.objects.filter(group='SUNDRY DEBTORS', user__company__company_id=request.session.get('co_id'))
    if request.method == "POST":
        customer = request.POST.get('customer')
        loading_point = request.POST.get('loading_point')
        unloading_point = request.POST.get('unloading_point')
        rate = request.POST.get('rate')
        vehicle_type_id = request.POST.get('vehicle_type')
        vehicle_type = Vehicle_type.objects.get(id=vehicle_type_id)

        exists = LocationMaster.objects.filter(
            customer=customer,
            loading_point=loading_point,
            unloading_point=unloading_point,
            rate=rate,
            vehicle_type=vehicle_type
        ).exists()
        if exists:
            return render(request, 'accounts/location_master/location_master.html', {
                'vehicles': vehicles,
                'error': 'Location with the same details already exists.'
            })

        try:
            LocationMaster.objects.create(
                company=Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id')),
                customer=customer,
                loading_point=loading_point,
                unloading_point=unloading_point,
                rate=rate,
                vehicle_type=vehicle_type
            )
            return render(request, 'accounts/location_master/location_master.html', {
                'vehicles': vehicles,
                'customers': customers,
                'success': 'Location created successfully.'
            })
        except Exception as e:
            return render(request, 'accounts/location_master/location_master.html', {
                'vehicles': vehicles,
                'customers': customers,
                'error': str(e)
            })

    return render(request, 'accounts/location_master/location_master.html', {'vehicles': vehicles, 'customers': customers})

def location_list(request):
    locations = LocationMaster.objects.filter(company__company_id=request.session.get('co_id'))
    return render(request, 'accounts/location_master/location_list.html', {'locations': locations})

def delete_location(request, location_id):
    try:
        location = LocationMaster.objects.get(id=location_id)
        location.delete()
        return redirect('main:location_list')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def location_edit(request, location_id):
    location = LocationMaster.objects.get(id=location_id)
    vehicles = Vehicle_type.objects.filter(co_id=request.session.get('co_id'))
    customers = Table_Accountsmaster.objects.filter(group='SUNDRY DEBTORS', user__company__company_id=request.session.get('co_id'))
    if request.method == "POST":
        customer = request.POST.get('customer')
        loading_point = request.POST.get('loading_point')
        unloading_point = request.POST.get('unloading_point')
        rate = request.POST.get('rate')
        vehicle_type_id = request.POST.get('vehicle_type')
        vehicle_type = Vehicle_type.objects.get(id=vehicle_type_id)

        exists = LocationMaster.objects.filter(
            customer=customer,
            loading_point=loading_point,
            unloading_point=unloading_point,
            rate=rate,
            vehicle_type=vehicle_type
        ).exists()
        if exists:
            return render(request, 'accounts/location_master/location_edit.html', {
                'vehicles': vehicles,
                'customers': customers,
                'location': location,
                'error': 'Location with the same details already exists.'
            })

        location.customer = customer
        location.loading_point = loading_point
        location.unloading_point = unloading_point
        location.rate = rate
        location.vehicle_type = vehicle_type
        location.save()

        return render(request, 'accounts/location_master/location_edit.html', {
            'location': location,
            'customers': customers,
            'vehicles': vehicles,
            'success': 'Location updated successfully.'
        })

    return render(request, 'accounts/location_master/location_edit.html', {'location': location, 'vehicles': vehicles, 'customers': customers})


# ------------------------------------ VENDOR MASTER ----------------------------------

from .models import VendorMaster

def vendor_master(request):
    if request.method == "POST":
        fuel_station = request.POST.get("fuel_station")
        exists = VendorMaster.objects.filter(fuel_station=fuel_station, company__company_id=request.session.get('co_id')).exists()
        if exists:
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "error": "Vendor with this name already exists."
            })
        try:
            VendorMaster.objects.create(
                company=Table_Companydetailsmaster.objects.get(company_id=request.session.get('co_id')),
                fuel_station=fuel_station
            )
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "success": "Vendor created successfully."
            })
        except Exception as e:
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "error": str(e)
            })
    return render(request, "accounts/vendor_master/vendor_master.html")

def vendor_list(request):
    vendors = VendorMaster.objects.filter(company__company_id=request.session.get('co_id'))
    return render(request, "accounts/vendor_master/vendor_list.html", {"vendors": vendors})

def edit_vendor(request, vendor_id):
    fuel_station = VendorMaster.objects.get(id=vendor_id).fuel_station
    if request.method == "POST":
        fuel_station = request.POST.get("fuel_station")
        exists = VendorMaster.objects.filter(fuel_station=fuel_station, company__company_id=request.session.get('co_id')).exists()
        if exists:
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "error": "Vendor with this name already exists.",
                "fuel_station": fuel_station
            })
        try:
            VendorMaster.objects.filter(id=vendor_id).update(
                fuel_station=fuel_station
            )
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "success": "Vendor updated successfully."
            })
        except Exception as e:
            return render(request, "accounts/vendor_master/vendor_master.html", {
                "fuel_station": fuel_station,
                "error": str(e)
            })
    return render(request, "accounts/vendor_master/vendor_master.html", {"fuel_station": fuel_station, "vendor_id": vendor_id})

def delete_vendor(request, vendor_id):
    try:
        vendor = VendorMaster.objects.get(id=vendor_id)
        vendor.delete()
        return redirect('main:vendor_list')
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})