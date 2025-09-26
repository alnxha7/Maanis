from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models
from django.utils.text import slugify




# branch master
class Branch_master(models.Model):
    branch_name = models.CharField(max_length=50, unique=True)
    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.IntegerField(default=1)
    financial_year = models.CharField(max_length=10, default='2024-2025')

    def __str__(self):
        return self.branch_name



class Table_Companydetailsmaster(models.Model):
    company_id = models.CharField(max_length=1, unique=True)
    companyname = models.CharField(max_length=50, unique=True)
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, blank=True, null=True)
    address3 = models.CharField(max_length=50, blank=True, null=True)
    pinCode = models.IntegerField()
    phoneno = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    gst = models.CharField(max_length=30, unique=True)
    pan = models.CharField(max_length=30, blank=True, null=True)
    finyearfrom = models.DateField()
    finyearto = models.DateField(blank=True, null=True)
    slug = models.SlugField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.company_id

    def save(self, *args, **kwargs):
        # Generate slug from the company name if not set
        if not self.slug:
            self.slug = slugify(self.companyname)
        super().save(*args, **kwargs)

        # Calculate fycode based on finyearfrom and finyearto
        fycode = f"{self.finyearfrom.year}-{self.finyearto.year}"

        Table_companyDetailschild.objects.update_or_create(
            company_id=self,
            defaults={
                "finyearfrom": str(self.finyearfrom),
                "finyearto": str(self.finyearto),
                "fycode": fycode,
                "databasename1": "databasename1",  # This should ideally be dynamic or provided
            },
        )

    def get_absolute_url(self):
        return reverse("main:companymaster_detail", kwargs={"slug": self.slug})


class Table_companyDetailschild(models.Model):
    company_id = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    fycode = models.CharField(max_length=20)
    finyearfrom = models.CharField(max_length=19)
    finyearto = models.CharField(max_length=10, blank=True, null=True)
    databasename1 = models.CharField(max_length=50)  # Increased max_length to 50

    def __str__(self):
        return f"{self.company_id.companyname} - {self.fycode}"





# Create your models here.
class Brand(models.Model):
    brand_name = models.CharField(max_length=250)
    brand_custom_id = models.IntegerField(default=0)
    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")
    # co_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    # branch_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    #
    # def save(self, *args, **kwargs):
    #     if not self.co_id:
    #         last_entry = Brand.objects.order_by('-co_id').first()
    #         self.co_id = last_entry.co_id + 1 if last_entry else 1
    #
    #     if not self.branch_id:
    #         last_entry = Brand.objects.order_by('-branch_id').first()
    #         self.branch_id = last_entry.branch_id + 1 if last_entry else 1
    #
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.brand_name


class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('PETROL', 'PETROL'),
        ('CNG', 'CNG'),
        ('ELECTRIC', 'ELECTRIC'),
        ('DIESEL', 'DIESEL')

    ]

    model_name = models.CharField(max_length=100)
    fuel = models.CharField(max_length=10, choices=FUEL_CHOICES)
    brand_id = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")
    def __str__(self):
        return self.model_name


class Vehicle_type(models.Model):
    vehicle_name = models.CharField(max_length=100)
    brand_id = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.SET_NULL,null=True)
    vehicle_type_custom_id = models.IntegerField(null=True, blank=True)
    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")
    def __str__(self):
        return self.vehicle_name

class Employee_master(models.Model):
    employee_custom_id = models.IntegerField(null=True, blank=True)
    WORKING_STATUS=[
        ('YES','YES'),
        ('NO','NO')
    ]
    employee_name = models.CharField(max_length=100)
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255)
    address_3 = models.CharField(max_length=255)
    telephone = PhoneNumberField(blank=True, null=True)
    mobile = PhoneNumberField(blank=True, null=True)
    working_status = models.CharField(max_length=10, choices=WORKING_STATUS)
    # dob = models.DateField()
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_length=10,max_digits=10, decimal_places=2, default=0.00)
    esi = models.DecimalField(max_length=10,max_digits=10, decimal_places=2, default=0.00)
    pf = models.DecimalField(max_length=10,max_digits=10, decimal_places=2, default=0.00)
    date_joining = models.DateField()
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=100)
    casual_leaves = models.IntegerField(default=12)

    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")

    def __str__(self):
        return self.employee_name


class Vehicle_master(models.Model):
    # User = get_user_model()
    FUEL_CHOICES = [
        ('PETROL', 'PETROL'),
        ('CNG', 'CNG'),
        ('ELECTRIC', 'ELECTRIC'),
        ('DIESEL', 'DIESEL')

    ]

    rc_owner_id=models.PositiveIntegerField( blank=True, null=True)
    rc_owner_name=models.CharField(max_length=100)
    mobile = PhoneNumberField()
    brand_id = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    vehicle_id = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    vehicle_type = models.ForeignKey(Vehicle_type, on_delete=models.SET_NULL, null=True)
    fuel = models.CharField(max_length=10, choices=FUEL_CHOICES)
    registration_number = models.CharField(max_length=20)
    make_year = models.PositiveIntegerField()
    chase_number = models.CharField(max_length=50)
    engine_number = models.CharField(max_length=50)
    insurance_renewal = models.DateField()
    pollution_renewal = models.DateField()
    # driver = models.ForeignKey(User, on_delete=models.SET_NULL, to_field="username", null=True)
    driver = models.ForeignKey(Employee_master, on_delete=models.SET_NULL,blank=True, null=True)

    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")

    def __str__(self):
        return self.rc_owner_name

    def save(self, *args, **kwargs):
        if not self.rc_owner_id:
            last_entry = Vehicle_master.objects.order_by('-rc_owner_id').first()
            self.rc_owner_id = last_entry.rc_owner_id + 1 if last_entry else 1

        super().save(*args, **kwargs)



from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Max
from django.db import IntegrityError


class Table_Accountsmaster(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts', null=True)
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True)

    account_code = models.IntegerField(blank=True, null=True)
    head = models.CharField(max_length=100)

    GROUP_CHOICES = [
        ('LIABILITIES', 'LIABILITIES'),
        ('INCOME', 'INCOME'),
        ('EXPENSES', 'EXPENSES'),
        ('TRADING EXPENSES', 'TRADING EXPENSES'),
        ('TRADING INCOME', 'TRADING INCOME'),
        ('CURRENT ASSET', 'CURRENT ASSET'),
        ('FIXED ASSETS', 'FIXED ASSETS'),
        ('CURRENT LIABILITIES', 'CURRENT LIABILITIES'),
        ('INDIRECT INCOME', 'INDIRECT INCOME'),
        ('INDIRECT EXPENSES', 'INDIRECT EXPENSES'),
        ('SUNDRY DEBTORS', 'SUNDRY DEBTORS'),
        ('SUNDRY CREDITORS', 'SUNDRY CREDITORS'),
        ('CASH AT BANK', 'CASH AT BANK'),
        ('CASH IN HAND', 'CASH IN HAND'),
        ('DUTIES AND TAXES', 'DUTIES AND TAXES'),
        ('LOANS', 'LOANS'),
        ('CAPITAL ACCOUNT', 'CAPITAL ACCOUNT'),
    ]

    group = models.CharField(max_length=249, choices=GROUP_CHOICES)

    CATEGORY_CHOICES = [
        ('Accounts', 'Accounts'),
        ('Cashbook', 'Cashbook'),
        ('Bank', 'Bank'),
        ('Customers', 'Customers'),
        ('Suppliers', 'Suppliers'),
    ]
    category = models.CharField(max_length=249, choices=CATEGORY_CHOICES)

    PRICEGROUP_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    ]
    pricegroup = models.CharField(max_length=249, null=True, blank=True, choices=PRICEGROUP_CHOICES)

    DEBIT_CREDIT_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]
    debitcredit = models.CharField(max_length=249, choices=DEBIT_CREDIT_CHOICES)

    gstno = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=299, null=True, blank=True)
    state = models.CharField(max_length=249, null=True, blank=True)
    address2 = models.CharField(max_length=299, null=True, blank=True)
    statecode = models.CharField(max_length=249, null=True, blank=True)
    address3 = models.CharField(max_length=249, null=True, blank=True)
    panno = models.CharField(max_length=249, null=True, blank=True)
    district = models.CharField(max_length=249, null=True, blank=True)
    creditlimit = models.CharField(max_length=249, null=True, blank=True)
    email = models.CharField(max_length=249, null=True, blank=True)
    creditdays = models.CharField(max_length=249, null=True, blank=True)
    telno = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    opbalance = models.IntegerField(null=True, blank=True, default=0)
    whattsapp = models.CharField(max_length=249, null=True, blank=True)
    currentbalance = models.CharField(max_length=249, null=True, blank=True)  # Ensure this matches your model definition
    slug = models.SlugField(max_length=250, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    class Meta:
        unique_together = ('user', 'head')  # Uniqueness is enforced per user 

    def save(self, *args, **kwargs):
        if not self.account_code:
            last_id = Table_Accountsmaster.objects.filter(user=self.user).aggregate(max_id=Max('account_code'))['max_id']
            self.account_code = (last_id or 999) + 1

        if self.head:
            self.head = self.head.upper()

        if not self.slug:
            base_slug = slugify(self.head)
            unique_slug = base_slug
            num = 1
            while Table_Accountsmaster.objects.filter(slug=unique_slug, user=self.user).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        if self.whattsapp is None:
            self.whattsapp = ""

        super(Table_Accountsmaster, self).save(*args, **kwargs)

        fycode = getattr(self, "_fycode", None)

        Table_Acntchild.objects.update_or_create(
            account_master=self,
            fyc_code=fycode,
            defaults={
                'account_code': self.account_code,
                'openning_balance': self.opbalance,
                'current_balance': self.currentbalance or 0,
                'debit_Credit': self.debitcredit,
                'disp': 'Y',
                'company_id': self.company.company_id if self.company else '',
                'branch_id': self.branch.branch_name if self.branch else '',
            }
        )     


    def __str__(self):
        return f"{self.head} ({self.account_code})"

    def get_absolute_url(self):
        return reverse("main:account_master_detail", kwargs={"slug": self.slug})

class Table_Acntchild(models.Model):
    account_master = models.ForeignKey('Table_Accountsmaster', on_delete=models.CASCADE, related_name='children')
    account_code = models.CharField(max_length=20)
    openning_balance = models.CharField(max_length=19)
    current_balance = models.CharField(max_length=100)
    debit_Credit = models.CharField(max_length=10)
    disp = models.CharField(max_length=10)
    company_id = models.CharField(max_length=100, null=True, blank=True)
    branch_id = models.CharField(max_length=100, null=True, blank=True)
    fyc_code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.account_code        
 #voucher       
class VoucherConfiguration(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster,on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch_master,on_delete=models.CASCADE, null=True)
    CATEGORY_CHOICES = [
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
        ('Debit Note', 'Debit Note'),
        ('Credit Note', 'Credit Note'),
        ('Contra Entry', 'Contra Entry'),
        ('Journal Entry', 'Journal Entry'),
        ('Trip sheet', 'Trip sheet'),
        ('Sales', 'Sales'),
    ]
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    series = models.CharField(max_length=255)
    serial_no = models.IntegerField()

    class Meta:
        unique_together = ('category', 'series')

    def __str__(self):
        return f"{self.category} - {self.series} - {self.serial_no}"


class Trip_sheet(models.Model):
    PAYMENT_BY = [
        ('CASH', 'CASH'),
        ('CREDIT', 'CREDIT'),
        ('GOOGLE PAY', 'GOOGLE PAY'),
        ('CARD', 'CARD')
    ]
    series = models.CharField(max_length=100,default='default')
    series_id=models.ForeignKey(VoucherConfiguration,on_delete=models.SET_NULL,null=True)
    entry_number= models.CharField(max_length=100)
    vehicle_number_id = models.ForeignKey(Vehicle_master, on_delete=models.SET_NULL,null=True,blank=True)
    vehicle_type_id=models.ForeignKey(Vehicle_type,on_delete=models.SET_NULL,null=True)
    loading_date = models.DateField()
    unloading_date=models.DateField()
    driver_name_id=models.ForeignKey(Employee_master,on_delete=models.SET_NULL,null=True)
    sl_no = models.PositiveIntegerField( blank=True, null=True)
    # customer_name=models.CharField(max_length=100)
    customer_name=models.ForeignKey(Table_Accountsmaster,on_delete=models.SET_NULL,null=True)
    loading_point=models.CharField(max_length=100)
    unloading_point=models.CharField(max_length=100)
    product=models.CharField(max_length=100)
    remark=models.CharField(max_length=100)
    starting_km=models.FloatField(default=0.00,null=True, blank=True)
    ending_km=models.FloatField(default=0.00,null=True, blank=True)
    km_rate=models.FloatField(default=0.00,null=True, blank=True)
    filling_km=models.FloatField(default=0.00,null=True, blank=True)
    payment_by = models.CharField(max_length=12, choices=PAYMENT_BY)
    tyre_work=models.FloatField(default=0.00,null=True, blank=True)
    battery=models.FloatField(default=0.00,null=True, blank=True)
    mech_electric=models.FloatField(default=0.00,null=True, blank=True)
    statutory_charge=models.FloatField(default=0.00,null=True, blank=True)
    statutory_narration=models.CharField(max_length=50)
    total_km=models.FloatField(default=0.00,null=True, blank=True)
    km_charge_total=models.FloatField(default=0.00, null=True, blank=True)
    extra_hour_charge_total=models.FloatField(default=0.00, null=True, blank=True)
    fixed_charge_total=models.FloatField(default=0.00,null=True, blank=True)
    haulting_charge_total=models.FloatField(default=0.00, null=True, blank=True)
    toll_parking_total=models.FloatField(default=0.00, null=True, blank=True)
    diesel_ltr=models.FloatField(default=0.00,null=True, blank=True)
    diesel_charges=models.FloatField(default=0.00,null=True, blank=True)
    advance_driver=models.FloatField(default=0.00,null=True, blank=True)
    driver_bata=models.FloatField(default=0.00,null=True, blank=True)
    advance_from_customer=models.FloatField(default=0.00,null=True, blank=True)
    total_freight_charges=models.FloatField(default=0.00,null=True, blank=True)
    account_code = models.IntegerField(blank=True, null=True)
    rate_type=models.CharField(max_length=20, null=True, blank=True)

    co_id = models.CharField(max_length=10, default='c')  # Default value 'c'
    branch_id = models.CharField(max_length=50,default="branch")
    financial_year =models.CharField(max_length=10,default='2024-2025')
    user = models.CharField(max_length=50,default='user')

# User
class User(AbstractUser):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True, related_name='company_users')
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True, related_name='branch_users')
    def __str__(self):
        return self.username

class Table_BillMaster(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True)
    fy_code = models.CharField(max_length=15, default='2025-2026')
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    series = models.ForeignKey(VoucherConfiguration,on_delete=models.CASCADE)
    bill_no = models.PositiveIntegerField()
    bill_date = models.DateField()
    gst_type = models.CharField(max_length=25, default='gst')
    bill_type = models.CharField(max_length=55)
    customer = models.ForeignKey(Table_Accountsmaster,on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    rate_type = models.CharField(max_length=20, null=True, blank=True)
    sp_disc_perc = models.FloatField(default=0.00)
    sp_disc_amt = models.FloatField(default=0.00)
    round_off = models.FloatField(default=0.00)
    total_discounts = models.FloatField(default=0.00)
    total_km = models.FloatField(null=True, blank=True)
    additional_charges = models.FloatField(default=0.00)
    total_gross = models.FloatField()
    amt_before_tax = models.FloatField()
    cgst = models.FloatField(default=0.00)
    sgst = models.FloatField(default=0.00)
    igst = models.FloatField(default=0.00)
    grand_total = models.FloatField()

class Table_BillItems(models.Model):
    master = models.ForeignKey(Table_BillMaster, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip_sheet, on_delete=models.CASCADE)
    code = models.PositiveIntegerField()
    vehicle_no = models.CharField(max_length=30)
    vehicle_type = models.CharField(max_length=90)
    total_km = models.FloatField(null=True, blank=True)
    km_rate = models.FloatField()
    ehr_rate = models.FloatField(null=True, blank=True)
    fixed_charge = models.FloatField()
    toll_parking = models.FloatField(null=True, blank=True)
    haulting = models.FloatField(null=True, blank=True)
    monthly_fixed_charge = models.FloatField(default=0.00)
    tax = models.FloatField()
    gross_amount = models.FloatField()
    net_value = models.FloatField()






# ---------------------------------  SALES ACCOUNT TABLE  ----------------------------



class Table_FormattedConfig(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    account_master = models.ForeignKey(Table_Accountsmaster, on_delete=models.CASCADE, null=True, blank=True)
    iform_id = models.PositiveIntegerField()
    form_name = models.CharField(max_length=50)
    vconfiq_value = models.CharField(max_length=70)
    vdb_field = models.CharField(max_length=70)

class Table_Mapping(models.Model):
    master = models.ForeignKey(Table_FormattedConfig, on_delete=models.CASCADE)
    iconfiq_id = models.PositiveIntegerField()
    iacc_id = models.CharField(max_length=200)
    drcr = models.CharField(max_length=8)





# ---------------------------------  TAX MASTER  ----------------------------


class TaxMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    master = models.ForeignKey(Table_Accountsmaster,on_delete=models.CASCADE, null=True, blank=True)
    tax_code = models.AutoField(primary_key=True)
    category = models.CharField(max_length=44)
    tax_type = models.CharField(max_length=18)
    tax_perc = models.FloatField()
    account_head = models.CharField(max_length=125)
    status = models.CharField(max_length=10)
    account_code = models.IntegerField()
    group_code = models.IntegerField(null=True, blank=True)
    tax_category = models.CharField(max_length=40, null=True, blank=True)
    co_id = models.CharField(max_length=5)
    fy_code = models.CharField(max_length=15)






# --------------------------------GODOWN MASTER--------------------------

class GodownMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    godown = models.CharField(max_length=255)



# --------------------------------GROUP MASTER--------------------------

class GroupMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    item_group = models.CharField(max_length=200)
    item_subgroup = models.CharField(max_length=200, null=True, blank=True)
    primary_group = models.CharField(max_length=5, default='N')


# --------------------------------UNIT MASTER--------------------------
class UnitMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    unit = models.CharField(max_length=100)
    subunit = models.CharField(max_length=100)
    conv_factor = models.FloatField()









class Wallet(models.Model):
    amount = models.FloatField(default=0.0)


# -------------------------------------ACCOUNTS NOTES-------------------------------------


from django.utils import timezone


from django.conf import settings
class Table_DrCrNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    series = models.CharField(max_length=150, null=True, blank=True)
    noteno = models.CharField(max_length=150, null=True, blank=True)
    ndate = models.DateField(default=timezone.now, null=True, blank=True)
    accountcode = models.CharField(max_length=200, null=True, blank=True)
    narration = models.CharField(max_length=200, null=True, blank=True)
    dramount = models.CharField(max_length=230, null=True, blank=True)
    cramount = models.CharField(max_length=230, null=True, blank=True)
    ntype = models.CharField(max_length=1, null=True, blank=True)
    userid = models.CharField(max_length=25, null=True, blank=True)
    coid = models.CharField(max_length=1, null=True, blank=True)
    fycode = models.CharField(max_length=15, null=True, blank=True)
    brid = models.CharField(max_length=1, null=True, blank=True)
    

    def __str__(self):
        return f"Series: {self.series}, Noteno: {self.noteno}, Date: {self.ndate}"



class Table_Voucher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    Series = models.CharField(max_length=255, blank=True, null=True)
    VoucherNo = models.IntegerField(blank=True, null=True)
    Vdate = models.DateField(blank=True, null=True)
    Accountcode = models.CharField(max_length=255, blank=True, null=True)
    Headcode = models.CharField(max_length=255, blank=True, null=True)
    CStatus = models.CharField(max_length=255, blank=True, null=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    VAmount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    VType = models.CharField(max_length=255, blank=True, null=True)
    Narration = models.TextField(blank=True, null=True)
    UserID = models.CharField(max_length=255, blank=True, null=True)
    FYCode = models.CharField(max_length=255, blank=True, null=True)
    Coid = models.CharField(max_length=255, blank=True, null=True)
    Branch_ID = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.Series} - {self.VoucherNo}"



class Table_Journal_Entry(models.Model):
    auth_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    series = models.CharField(max_length=100, null=True, blank=True)
    voucher_no = models.IntegerField(null=True, blank=True)
    vdate = models.DateField( null=True, blank=True)
    accountcode = models.CharField(max_length=250, null=True, blank=True)
    narration = models.TextField(null=True, blank=True)
    dramount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    cramount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    fycode = models.CharField(max_length=100, null=True, blank=True)
    coid = models.CharField(max_length=100, null=True, blank=True)
    brid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.series}-{self.voucher_no}"



class Table_Contra_Entry(models.Model):
    auth_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    series = models.CharField(max_length=100, null=True, blank=True)
    voucher_no = models.IntegerField(null=True, blank=True)
    vdate = models.DateField( null=True, blank=True)
    accountcode = models.CharField(max_length=200, null=True, blank=True)
    narration = models.TextField(null=True, blank=True)
    dramount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    cramount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    fycode = models.CharField(max_length=100, null=True, blank=True)
    coid = models.CharField(max_length=100, null=True, blank=True)
    brid = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.series}-{self.voucher_no}"


class Ledger(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE, null=True, blank=True)
    AccountCode = models.CharField(max_length=15, null=True, blank=True)
    VoucherType = models.CharField(max_length=15, null=True, blank=True)
    VoucherSeries = models.CharField(max_length=15, null=True, blank=True)
    VoucherNo = models.IntegerField(null=True, blank=True)
    FormType = models.CharField(max_length=15, null=True, blank=True)
    Narration = models.CharField(max_length=255, null=True, blank=True)
    Amount = models.IntegerField(null=True, blank=True)
    Dr_Cr = models.CharField(max_length=15, null=True, blank=True)
    FinancialYear = models.CharField(max_length=15, null=True, blank=True)
    BranchID = models.CharField(max_length=15, null=True, blank=True)
    CompanyID = models.CharField(max_length=15, null=True, blank=True)



# ------------------------------- RATE MASTER ----------------------------

class RateMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=200)

class RateChild(models.Model):
    master = models.ForeignKey(RateMaster, on_delete=models.CASCADE)
    vehicle = models.CharField(max_length=200)
    rate = models.FloatField(null=True, blank=True)
    type = models.CharField(max_length=25)
    km = models.IntegerField(null=True, blank=True)
    fixed_rate = models.FloatField(null=True, blank=True)
    additional_charge = models.FloatField(null=True, blank=True)


# ------------------------------- LOCATION MASTER ----------------------------

class LocationMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True)
    loading_point = models.CharField(max_length=200)
    unloading_point = models.CharField(max_length=200)
    rate = models.FloatField(null=True, blank=True)
    vehicle_type = models.ForeignKey(Vehicle_type, on_delete=models.CASCADE, null=True, blank=True)


# ------------------------------- VENDOR MASTER ----------------------------

class VendorMaster(models.Model):
    company = models.ForeignKey(Table_Companydetailsmaster, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch_master, on_delete=models.CASCADE, null=True, blank=True)
    fuel_station = models.CharField(max_length=200)