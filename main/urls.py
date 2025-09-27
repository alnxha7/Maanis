from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . views import AccountMasterView,AccountmMasterUserView,AccountMasterDetailView,DeleteAccountmMasterUserView,EditAccountmMasterUserView,VoucherConfigurationTable,VoucherConfigurationListView,CompanyDetailsMasterView,CompanyMasterUserView,CompanyMasterDetailView,DeletecompanymMasterUserView,EditCompanyMasterUserView
from .views import (AccountCreditNoteView, AccountCreditTableView,
                    AccountDebitNoteView, AccountDebitTableView,
                    AccountMasterDetailView, AccountMasterView,
                    AccountmMasterUserView,
                    CompanyDetailsMasterView, CompanyMasterDetailView,
                    CompanyMasterUserView, ContraEntryTable,
                    ContraEntryView, DeletecompanymMasterUserView, DeleteContraEntryView,
                    DeleteCreditNoteView, DeleteDebitNoteView, DeleteJournalEntryView, 
                    EditAccountmMasterUserView, EditCompanyMasterUserView,
                    EditContraEntry, EditJournalEntry, 
                    EditPaymentView, EditReceiptView,
                    EnterAmountView, JournalEntryTable, JournalEntryView,
                    LedgerSearchView, LedgerView,
                    PaymentEnterAmountView, PaymentListTable,
                    ReceiptDetailView, ReceiptListTable, SearchContraEntryView,
                    SearchCreditTableView, SearchDebitTableView,
                    SearchJournalEntryView, SearchPaymentView,
                    SearchReceiptView, 
                    VoucherConfigurationListView, VoucherConfigurationTable,CashBookSearchView,
                    BankBookSearchView,CashBookView,BankBookView,DayBookSearchView,DayBookView,TrialBalanceView, 
                    ProfitAndLossSearchView,ProfitAndLossView,BalanceSheetSearchView,BalanceSheetView,FinancialYearFormView,
                    )


app_name = 'main'

urlpatterns = [
    path('',views.index,name='index'),
    # Company & User login
    path('company-login/', views.co_login_view, name='co_login'),
    path('login/',views.user_login, name='login'),

    path('driver-register/',views.driver_register,name='driver_register'),
    path('driver-login/',views.driver_login, name='driver_login'),
    path('driver-logout/',views.driver_logout, name='driver_logout'),
    # brand url
    path('brand-list/', views.brand_list, name='brand_list'),
    path('brand-new/', views.brand_create, name='brand_create'),
    path('brand-readonly/<int:pk>/', views.brand_readonly, name='brand_readonly'),
    path('brand-edit/<int:pk>/', views.brand_update, name='brand_update'),
    path('brand-delete/<int:pk>/', views.brand_delete, name='brand_delete'),
    # Model url
    path('vehicle-list/', views.vehicle_list, name='vehicle_list'),
    path('vehicle-add/', views.vehicle_create, name='vehicle_add'),
    path('vehicle-readonly/<int:pk>/', views.vehicle_readonly, name="vehicle_readonly"),
    path('vehicle-update/<int:pk>/', views.vehicle_update, name='vehicle_update'),
    path('vehicle-delete/<int:pk>/', views.vehicle_delete, name='vehicle_delete'),
    # vehicle type url
    path('vehicle-type-list/',views.vehicle_type_list, name='vehicle_type_list'),
    path('vehicle-type-add/',views.vehicle_type_create, name='vehicle_type_create'),
    path('vehicle-type-readonly/<int:pk>/',views.vehicle_type_readonly, name="vehicle_type_readonly"),
    path('vehicle-type-edit/<int:pk>/',views.vehicle_type_update, name='vehicle_type_update'),
    path('vehicle-types-delete/<int:pk>/',views.vehicle_type_delete, name='vehicle_type_delete'),
    # vehicle msater url
    path('vehicle-master-list/',views.vehicle_master_list, name='vehicle_master_list'),
    path('vehicles-master-add/', views.vehicle_master_add, name='vehicle_master_add'),
    path('vehicles-master-readonly/<int:pk>/' ,views.vehicle_master_readonly, name="vehicle_master_readonly"),
    path('vehicles-master-edit/<int:pk>/', views.vehicle_master_update, name='vehicle_master_update'),
    path('vehicles-master-delete/<int:pk>/', views.vehicle_master_delete, name='vehicle_master_delete'),
    # employee url
    path('employee-list/',views.employee_list, name='employee_list'),
    path('employee-add/',views.employee_create, name='employee_create'),
    path('employee-readonly/<int:pk>/',views.employee_readonly, name='employee_readonly'),
    path('employee-edit/<int:pk>/', views.employee_update, name='employee_update'),
    path('employee-delete/<int:pk>/',views.employee_delete, name='employee_delete'),
    #Trip sheet
    path('trips-create/', views.trip_create, name='trip_create'),
    path('trips-list/', views.trip_list, name='trip_list'),
    path('trips-update/<str:series>/<str:entry_number>/', views.trip_update, name='trip_update'),
    path('trips-search-delete/', views.trip_search_delete, name='trip_search_delete'),
    path('trips-read-only/<str:series>/<str:entry_number>/', views.trip_read_only, name='trip_read_only'),
    path('trip-delete/<str:series>/<int:entry_number>/', views.trip_delete, name='trip_delete'),

    path('get-next-entry-number/', views.get_next_entry_number, name='get_next_entry_number'),
    path('get_rate/', views.get_rate, name='get_rate'),
    path('get_fixed_rate/', views.get_fixed_rate, name='get_fixed_rate'),


    # path('trips/delete/<int:pk>/', views.trip_delete, name='trip_delete'),

    # accounts - account master
    path('account-master/', AccountMasterView.as_view(), name='acc_master'),
    path('account-master-list/', AccountmMasterUserView.as_view(), name='acc_master_list'),
    path('delete/account-master-list/<int:pk>/', DeleteAccountmMasterUserView.as_view(), name='delete_acc_master_list'),
    path('account/<slug:slug>/', AccountMasterDetailView.as_view(), name='account_master_detail'),
    path('edit/account-master-list/<slug:slug>/', EditAccountmMasterUserView.as_view(), name='edit_acc_master_list'),
    # accounts - voucher configuration
    path('accounts/voucher-configuration/list/search/', VoucherConfigurationTable.as_view(), name='voucher_search'),
    path('accounts/voucher-configuration/', VoucherConfigurationListView.as_view(), name='voucher_configuration'),
    # path('accounts/voucher-configuration/validate/', ValidateVoucherConfiguration.as_view(), name='validate_voucher_configuration'),
    # accounts - company master
    path('accounts/company-master/details/', CompanyDetailsMasterView.as_view(), name='company_details_master'),
    path('accounts/company-master/list/',CompanyMasterUserView.as_view(),name='company_master_list'),
    path('accounts/company-master/<slug:slug>/', CompanyMasterDetailView.as_view(), name='companymaster_detail'),
    path("accounts/company-master/delete/<int:pk>/",DeletecompanymMasterUserView.as_view(),name="delete_company_master_list",),
    path("accounts/company-master/edit/<int:pk>/",EditCompanyMasterUserView.as_view(),name="edit_company_master_list"),

    # account-branch master
    path('accounts/branch-master/list/', views.branch_list, name='branch_list'),
    path('accounts/branch-master/create/', views.branch_create, name='branch_create'),
    path('accounts/branch-master/readonly/<int:pk>/', views.branch_readonly, name='branch_readonly'),
    path('accounts/branch-master/update/<int:pk>/', views.branch_update, name='branch_update'),
    path('accounts/branch-master/delete/<int:pk>/', views.branch_delete, name='branch_delete'),

    path('get-branches/', views.get_branches, name='get_branches'),	


    path("bill_details/", views.bill_details, name="bill_details"),
    path('get-serial-number/', views.get_serial_number, name='get_serial_number'),
    path('ajax/autocomplete-customers/', views.autocomplete_customers, name='autocomplete_customers'),
    path("bill_search/", views.bill_search, name="bill_search"),
    path("bill_edit/<int:bill_id>/", views.bill_edit, name="bill_edit"),
    path("bill_delete/<int:bill_id>/", views.bill_delete, name="bill_delete"),
    path("bill_delete_search/", views.bill_delete_search, name="bill_delete_search"),


    path("bill_report_search/", views.bill_report_search, name="bill_report_search"),
    path("bill_wise_report/", views.bill_wise_report, name="bill_wise_report"),

    path("formatted_config/", views.formatted_config, name="formatted_config"),
    path("mapping/", views.mapping, name="mapping"),

    path("add_tax/", views.add_tax, name="add_tax"),
    path("tax_list/", views.tax_list, name="tax_list"),

    path("new_godown/", views.new_godown, name="new_godown"),
    path("godown_list/", views.godown_list, name="godown_list"),
    path("edit_godown/<int:godown_id>", views.edit_godown, name="edit_godown"),
    path("delete_godown/<int:godown_id>", views.delete_godown, name="delete_godown"),

    path("new_group/", views.new_group, name="new_group"),
    path("group_list/", views.group_list, name="group_list"),
    path("group_edit/<int:group_id>", views.group_edit, name="group_edit"),
    path("group_delete/<int:group_id>", views.group_delete, name="group_delete"),

    path("add_unit/", views.add_unit, name="add_unit"),
    path("unit_list/", views.unit_list, name="unit_list"),
    path("unit_edit/<int:unit_id>", views.unit_edit, name="unit_edit"),
    path("unit_delete/<int:unit_id>", views.unit_delete, name="unit_delete"),

    #report
    path('trip-sheet-date-wise/', views.trip_sheet_date_wise, name='trip_sheet_date_wise'),
    path('trip-sheets-by-loading-date/', views.trip_sheets_by_loading_date, name='trip_sheets_by_loading_date'),
    
    path('trip-sheet-driver-wise/', views.trip_sheet_driver_wise, name='trip_sheet_driver_wise'),
    path('trip-sheets-driver-loading-date/', views.trip_sheets_driver_loading_date, name='trip_sheets_driver_loading_date'),

    path('trip-sheet-vehicle-wise/', views.trip_sheet_vehicle_wise, name='trip_sheet_vehicle_wise'),
    path('trip-sheets-vehicle-loading-date/',views.trip_sheets_vehicle_loading_date,name='trip_sheets_vehicle_loading_date' ),

    path('trip-sheet-customer-wise/', views.trip_sheet_customer_wise, name='trip_sheet_customer_wise'),
    path('get-customers/', views.get_customers, name='get_customers'),
    path('trip-sheets-customer-loading-date/',views.trip_sheets_customer_loading_date, name='trip_sheets_customer_loading_date'),




    path("rate_master/", views.rate_master, name="rate_master"),
    path("rate_list/", views.rate_list, name="rate_list"),
    path("rate_delete/<int:rate_id>/", views.rate_delete, name="rate_delete"),


    path("location_master/", views.location_master, name="location_master"),
    path("location_list/", views.location_list, name="location_list"),
    path("delete_location/<int:location_id>/", views.delete_location, name="location_delete"),
    path("location_edit/<int:location_id>/", views.location_edit, name="location_edit"),


    path("vendor_master/", views.vendor_master, name="vendor_master"),
    path("vendor_list/", views.vendor_list, name="vendor_list"),
    path("edit_vendor/<int:vendor_id>/", views.edit_vendor, name="edit_vendor"),
    path("delete_vendor/<int:vendor_id>/", views.delete_vendor, name="delete_vendor"),


    


    # accounts - debit-note
    path("accounts/debit-note/",AccountDebitNoteView.as_view(),name="account_debit_note"),
    path('debit-note/delete/<int:pk1>/<int:pk2>/', DeleteDebitNoteView.as_view(), name='delete_debit_note'),
    path("accounts/debit-note/search/",SearchDebitTableView.as_view(),name="search_debit_note"),
    path("accounts/debit-note/<str:series>/<int:serial_no>/", AccountDebitNoteView.as_view(), name="account_debit_note"),
    path("accounts/debit-note/table/",AccountDebitTableView.as_view(),name="account_debit_table"),


    # accounts - credit-note
    path("accounts/credit-note/",AccountCreditNoteView.as_view(),name="account_credit_note"),
    path("accounts/credit-note/table/",AccountCreditTableView.as_view(),name="account_credit_table"),
    path("accounts/credit-note/search/",SearchCreditTableView.as_view(),name="search_credit_note"),
    path('accounts/credit-note/<str:series>/<str:serial_no>/', AccountCreditNoteView.as_view(), name='account_credit_note'),
    path('accounts/credit-note/delete/<int:pk1>/<int:pk2>/', DeleteCreditNoteView.as_view(), name='delete_credit_note'),


    # accounts - receipt voucher
    path('accounts/receipt-voucher/', EnterAmountView.as_view(), name='receipt'),
    path('accounts/receipt-voucher/<int:voucher_id>/', ReceiptDetailView.as_view(), name='receipt_detail'),
    path('accounts/receipt-voucher/<int:voucher_id>/', ReceiptDetailView.as_view(), name='receipt_detail'),
    path("accounts/receipt-voucher/list/", ReceiptListTable.as_view(), name="receipt_list"),
    path('accounts/receipt-voucher-modify/', SearchReceiptView.as_view(), name='receipt_modify'),
    path('accounts/receipt-voucher/edit/', EditReceiptView.as_view(), name='edit_receipt'),

    # accounts - payment voucher
    path('accounts/payment-voucher/edit/', EditPaymentView.as_view(), name='edit_payment'),
    path('accounts/payment-voucher-modify/', SearchPaymentView.as_view(), name='payment_modify'),
    path('accounts/payment-voucher/', PaymentEnterAmountView.as_view(), name='payment'),
    path("accounts/payment-voucher/list/", PaymentListTable.as_view(), name="payment_list"),


    # accounts - Journal entry
    path('accounts/journal-entry/', JournalEntryView.as_view(), name='account_journal_entry'),
    path("accounts/journal-entry/table/",JournalEntryTable.as_view(),name="account_journal_table"),
    path('accounts/journal-entry/search/', SearchJournalEntryView.as_view(), name='search_journal_entry'),
    path('accounts/journal-entry/edit/', EditJournalEntry.as_view(), name='edit_journal_entry'),
    path('accounts/journal-entry/delete/<str:voucher_no>/', DeleteJournalEntryView.as_view(), name='delete_journal_entry'),



    #accounts - Contra entry
    path('accounts/contra-entry/', ContraEntryView.as_view(), name='account_contra_entry'),
    path('accounts/contra-entry/search/', SearchContraEntryView.as_view(), name='search_contra_entry'),
    path('accounts/contra-entry/edit/', EditContraEntry.as_view(), name='edit_contra_entry'),
    path("accounts/contra-entry/table/",ContraEntryTable.as_view(),name="account_contra_table"),
    path('accounts/contra-entry/delete/<str:voucher_no>/', DeleteContraEntryView.as_view(), name='delete_contra_entry'),



    # accounts - ledger
    path("accounts/ledger/search/", LedgerSearchView.as_view(), name="ledger_search"),
    path("accounts/ledger/list/<str:account_code>/<str:start_date>/<str:end_date>/",LedgerView.as_view(),name="ledger",),

    # accounts - cashbook
    path("accounts/cashbook/search/", CashBookSearchView.as_view(), name="cashbook_search"),
    path("accounts/cashbook/list/<str:account_code>/<str:start_date>/<str:end_date>/",CashBookView.as_view(),name="cashbook",),


    # accounts - bankbook
    path("accounts/bank/search/", BankBookSearchView.as_view(), name="bankbook_search"),
    path("accounts/bank/list/<str:account_code>/<str:start_date>/<str:end_date>/",BankBookView.as_view(),name="bankbook",),

    # accounts - daybook
    path("accounts/daybook/search/", DayBookSearchView.as_view(), name="daybook_search"),
    path('accounts/daybook/list/<str:start_date>/<str:end_date>/', DayBookView.as_view(), name='daybook'),

    
    # accounts - bankbook
    path('accounts/trial-balance', TrialBalanceView.as_view(), name='trial_balance'),



    # accounts - profit and loss
    path("accounts/profit-and-loss/search/", ProfitAndLossSearchView.as_view(), name="profit_and_loss_search"),
    path('accounts/profit-and-loss/list/<str:start_date>/<str:end_date>/', ProfitAndLossView.as_view(), name='profit_and_loss'),

    # accounts - balance sheet
    path("accounts/balance-sheet/search/", BalanceSheetSearchView.as_view(), name="balance_sheet_search"),
    path('accounts/balance-sheet/list/<str:start_date>/<str:end_date>/', BalanceSheetView.as_view(), name='balance_sheet'),

    #accounts fin-year-form
    path('accounts/financial-year-form/', FinancialYearFormView.as_view(), name='financial_year_form'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
