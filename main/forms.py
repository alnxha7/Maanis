



from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import DateInput
from django.utils.html import mark_safe
from .models import Table_Accountsmaster, Table_Companydetailsmaster

# ACCOUNT MASTER

class AccountMasterForm(forms.ModelForm):
    class Meta:
        model = Table_Accountsmaster
        fields = [
            'head', 'group', 'gstno', 'category', 'address1', 'state', 'address2',
            'statecode', 'address3', 'panno', 'district', 'creditlimit', 'email',
            'creditdays', 'telno', 'pricegroup', 'mobile', 'opbalance', 'whattsapp',
            'debitcredit', 'currentbalance', 'tax',
        ]
        widgets = {
            'head': forms.TextInput(attrs={
                'class': 'custom-class',
                'style': 'background-color:rgb(185, 233, 246);text-transform: uppercase;',
            }),
            'gstno': forms.TextInput(attrs={
                'style': 'text-transform: uppercase;',
            }),
        }
        labels = {
            'head': 'Head',
            'group': 'Account Group',
            'gstno': 'GST Number',
            'category': 'Category',
            'address1': 'Address 1',
            'state': 'State',
            'address2': 'Address 2',
            'statecode': 'State Code',
            'address3': 'Address 3',
            'panno': 'PAN Number',
            'district': 'District',
            'creditlimit': 'Credit Limit',
            'email': 'Email Address',
            'creditdays': 'Credit Days',
            'telno': 'Telephone Number',
            'pricegroup': 'Price Group',
            'mobile': 'Mobile Number',
            'opbalance': 'Opening Balance',
            'whattsapp': 'WhatsApp Number',
            'debitcredit': 'Debit/Credit',
            'currentbalance': 'Current Balance',
            'tax': 'Tax(%)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AccountMasterForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['head'].widget.attrs['readonly'] = True
            self.fields['head'].required = False

    def clean_head(self):
        head = self.cleaned_data.get('head')
        if self.user is None:
            raise forms.ValidationError("User must be provided for validation.")

        # Check if the head already exists for this user
        if Table_Accountsmaster.objects.filter(head=head, user=self.user).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This head already exists for your account. Please choose a different one.")

        return head

   

    def clean_whattsapp(self):
        whattsapp = self.cleaned_data.get('whattsapp')
        if whattsapp and len(whattsapp) != 10:
            raise forms.ValidationError(
                mark_safe("<span style='color:red; font-size:12px;'>WhatsApp number must be 10 digits long.</span>"))
        return whattsapp


# COMPANY MASTER
class ComapnyDetailsMasterForm(forms.ModelForm):
    class Meta:
        model = Table_Companydetailsmaster
        fields = [
            "company_id",
            "companyname",
            "address1",
            "pinCode",
            "address2",
            "phoneno",
            "address3",
            "mobile",
            "email",
            "gst",
            "pan",
            "finyearfrom",
            "finyearto",
        ]

        labels = {
            "company_id": "Company ID",
            "companyname": "Company Name",
            "address1": "Address 1",
            "address2": "Address 2",
            "address3": "Address 3",
            "pinCode": "Pin Code",
            "phoneno": "Phone Number",
            "mobile": "Mobile Number",
            "email": "Email Address",
            "gst": "GST Number",
            "pan": "PAN Number",
            "finyearfrom": "Financial Year From",
            "finyearto": "Financial Year To",
        }

        widgets = {
            "companyname": forms.TextInput(
                attrs={
                    "class": "custom-class",
                    "style": "background-color:rgb(185, 233, 246); text-transform: uppercase;",
                }
            ),
            "company_id": forms.TextInput(
                attrs={
                    "style": "text-transform: uppercase; width:90px; padding-left:35px"
                }
            ),
            "gst": forms.TextInput(attrs={"style": "text-transform: uppercase;"}),
            "pan": forms.TextInput(attrs={"style": "text-transform: uppercase;"}),
            "finyearfrom": DateInput(
                format="%d/%m/%Y", attrs={"type": "date", "style": "width: 130px;"}
            ),
            "finyearto": DateInput(
                format="%d/%m/%Y",
                attrs={"type": "date", "style": "width: 130px; margin-left: 18px;"},
            ),
        }

    def _init_(self, *args, **kwargs):
        self.instance = kwargs.get("instance", None)
        super(ComapnyDetailsMasterForm, self)._init_(*args, **kwargs)

        if self.instance and self.instance.pk:
            # If editing an existing instance, exclude finyearfrom and finyearto fields
            self.fields.pop("finyearfrom")
            self.fields.pop("finyearto")

        if self.instance and self.instance.pk:
            self.fields["company_id"].widget.attrs["readonly"] = True
            self.fields["company_id"].widget.attrs[
                "style"
            ] += " background-color: lightgrey; text-align: center;"

    def clean_companyname(self):
        companyname = self.cleaned_data.get("companyname")
        if companyname:
            companyname = companyname.upper()
            # Check for uniqueness of companyname excluding the current instance if it's an update
            qs = Table_Companydetailsmaster.objects.filter(companyname=companyname)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This COMPANY NAME already exists.")
        return companyname

    def clean_company_id(self):
        company_id = self.cleaned_data.get("company_id")
        if company_id and not company_id.isalpha():
            raise forms.ValidationError("Company ID must contain only letters.")
        return company_id.upper() if company_id else None

    def clean_gst(self):
        gst = self.cleaned_data.get("gst")
        if gst and len(gst) != 15:
            raise forms.ValidationError(
                "GST number must be exactly 15 characters long."
            )
        # Check for uniqueness of GST number excluding the current instance if it's an update
        qs = Table_Companydetailsmaster.objects.filter(gst=gst)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This GST number already exists.")
        return gst.upper() if gst else None

    def clean_pan(self):
        pan = self.cleaned_data.get("pan")
        if pan and len(pan) != 10:
            raise forms.ValidationError(
                "PAN number must be exactly 10 characters long."
            )
        return pan.upper() if pan else None

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile")
        if mobile and (not mobile.isdigit() or len(mobile) != 10):
            raise forms.ValidationError("Mobile number must contain 10 digits only.")
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        company_id = cleaned_data.get("company_id")
        if company_id:
            # Check for uniqueness of company_id excluding the current instance if it's an update
            qs = Table_Companydetailsmaster.objects.filter(company_id=company_id)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error(
                    "company_id", f"Company ID '{company_id}' already exists."
                )
        return cleaned_data

    def save(self, commit=True):
        try:
            return super(ComapnyDetailsMasterForm, self).save(commit=commit)
        except IntegrityError:
            self.add_error(
                "company_id",
                f"Company ID '{self.cleaned_data.get('company_id')}' already exists.",
            )
            raise ValidationError(
                f"Company ID '{self.cleaned_data.get('company_id')}' already exists."
            )
