from django.contrib import admin
from .models import Brand, Vehicle, Vehicle_type, Vehicle_master, Employee_master, Trip_sheet, Table_Accountsmaster, \
    Table_Acntchild, VoucherConfiguration,Table_Companydetailsmaster,Table_companyDetailschild, Table_DrCrNote,Table_Acntchild,Table_Accountsmaster,Table_Voucher, Table_Contra_Entry, \
    Table_Journal_Entry, RateMaster

# Register your models here.

admin.site.register(Brand)
admin.site.register(Vehicle)
admin.site.register(Vehicle_type)
# admin.site.register(Vehicle_master)
admin.site.register(Employee_master)
admin.site.register(Trip_sheet)
admin.site.register(RateMaster)


@admin.register(Vehicle_master)
class VehicleMasterAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'rc_owner_name')


admin.site.register(Table_Acntchild)
admin.site.register(Table_Accountsmaster)

@admin.register(VoucherConfiguration)
class VoucherConfigurationAdmin(admin.ModelAdmin):
    list_display = ('category', 'series', 'serial_no')
    search_fields = ('category', 'series')
    list_filter = ('category',)

class CompanydetailsmasterAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'companyname', 'email', 'gst', 'pan')
    search_fields = ('company_id', 'companyname')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

class CompanyDetailschildAdmin(admin.ModelAdmin):
    list_display = ('company_id', 'fycode', 'finyearfrom', 'finyearto', 'databasename1')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company_id__user=request.user)

admin.site.register(Table_Companydetailsmaster, CompanydetailsmasterAdmin)
admin.site.register(Table_companyDetailschild, CompanyDetailschildAdmin)


from django.utils.html import format_html
from django.urls import reverse
from django.contrib import admin
from .models import Table_BillMaster, Table_BillItems

class TableBillItemsInline(admin.TabularInline):
    model = Table_BillItems
    extra = 0
    fields = [
        'trip', 'code', 'vehicle_no', 'vehicle_type', 'km_rate',
        'ehr_rate', 'fixed_charge', 'toll_parking', 'haulting',
        'monthly_fixed_charge', 'tax', 'gross_amount', 'net_value'
    ]
    readonly_fields = []

@admin.register(Table_BillMaster)
class TableBillMasterAdmin(admin.ModelAdmin):
    list_display = [
        'get_company_name', 'series', 'bill_no', 'bill_date', 'bill_type', 'get_customer',
        'date_from', 'date_to', 'sp_disc_perc', 'sp_disc_amt', 'round_off', 'total_km',
        'total_gross', 'amt_before_tax', 'cgst', 'sgst', 'igst', 'grand_total'
    ]
    search_fields = ['bill_no', 'customer__head']
    list_filter = ['bill_date', 'customer']
    inlines = [TableBillItemsInline]
    fields = list_display

    @admin.display(description='Company')
    def get_company_name(self, obj):
        if obj.company:
            url = reverse('admin:main_table_companydetailsmaster_change', args=[obj.company.id])
            return format_html('<a href="{}">{}</a>', url, obj.company.companyname)
        return "-"

    @admin.display(description='Customer')
    def get_customer(self, obj):
       return obj.customer.head if obj.customer else "-"

@admin.register(Table_BillItems)
class TableBillItemsAdmin(admin.ModelAdmin):
    list_display = [
        'master', 'trip', 'code', 'vehicle_no', 'vehicle_type', 'km_rate', 'total_km',
        'ehr_rate', 'fixed_charge', 'toll_parking', 'haulting', 
        'monthly_fixed_charge', 'tax', 'gross_amount', 'net_value'
    ]
    search_fields = ['vehicle_no', 'trip__entry_number']
    list_filter = ['vehicle_type']
    fields = list_display





@admin.register(Table_DrCrNote)
class Table_DrCrNoteAdmin(admin.ModelAdmin):
    list_display = ("series", "noteno", "ndate", "accountcode", "narration", "dramount", "cramount", "ntype", "userid", "coid", "fycode", "brid")


class ContraEntryNoteAdmin(admin.ModelAdmin):
    list_display = ('series', 'voucher_no', 'vdate', 'accountcode', 'narration', 'dramount', 'cramount', 'user_id', 'coid', 'fycode', 'brid')

admin.site.register(Table_Contra_Entry, ContraEntryNoteAdmin)


class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('series', 'voucher_no', 'vdate', 'accountcode', 'narration', 'dramount', 'cramount', 'user_id', 'coid', 'fycode', 'brid')

admin.site.register(Table_Journal_Entry, JournalEntryAdmin)




class TableVoucherAdmin(admin.ModelAdmin):
    list_display = ('Series', 'VoucherNo', 'Vdate', 'Accountcode', 'Headcode', 'payment', 'VAmount', 'VType', 'Narration', 'CStatus', 'UserID', 'FYCode', 'Coid', 'Branch_ID')
    search_fields = ('Series', 'VoucherNo', 'Accountcode', 'Headcode', 'Narration')
    list_filter = ('Series', 'Vdate', 'VType', 'CStatus')

admin.site.register(Table_Voucher, TableVoucherAdmin)