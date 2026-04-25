from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import CollegeOffice, User, AdminProfile, CollegeProfile

class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username", "first_name", "middle_name", "last_name", "email", "phone_number", "password1",
            "password2"
        )
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "juan123", 
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Juan"
                }
            ),
            "middle_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Santos"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Dela Cruz"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "juandelacruz@wmsu.edu.ph"
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "123 456 7890"
                }
            ),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.fields["username"].widget.attrs.pop("autofocus", None)

        self.fields["password1"].widget = forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "placeholder": "Create a password"
            }
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "placeholder": "Confirm password"
            }
        )
        

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ("employee_id_number", "profile_photo",)
        widgets = {
            "employee_id_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Enter Employee ID number"
                }
            ),
            "profile_photo": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100",
                    "id": "profile-photo-id", "accept": "image/*"
                }
            )
        }

class AdminAidCreationForm(forms.ModelForm):
    employee_id_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "placeholder": "Enter Employee ID number"
            }
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "middle_name", "last_name", "email", "phone_number")
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Juan"
                }
            ),   
            "middle_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Santos"
                }
            ),   
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Dela Cruz"
                }
            ),   
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "juandelacruz@wmsu.edu.ph"
                }
            ),   
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "123 456 7890"
                }
            ),   
        }


class AdminAidSetupForm(forms.ModelForm):
    password1 = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ("username",)
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "juan123", 
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.fields["username"].widget.attrs.pop("autofocus", None)

        self.fields["password1"].widget = forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "placeholder": "Create a password"
            }
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "placeholder": "Confirm password"
            }
        )


class AdminAidSetupProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ("profile_photo",)
        widgets = {
            "profile_photo": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100",
                    "id": "profile-photo-id", "accept": "image/*"
                }
            )
        }


class CollegeReapplyUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name", "middle_name", "last_name", "email", "phone_number",
        )
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Juan"
                }
            ),
            "middle_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Santos"
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Dela Cruz"
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "juandelacruz@wmsu.edu.ph"
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "123 456 7890"
                }
            ),
        }

    
class CollegeProfileForm(forms.ModelForm):
    college_office = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                "id": "college-office-dropdown", "list": "college-office-list", "autocomplete": "off",
                "placeholder": "College of Computing Studies"
            }
        )
    )

    class Meta:
        model = CollegeProfile
        fields = ("college_office", "position_title",)
        widgets = {
            "position_title": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Dean"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fills college office with name instead of id when editing an existing instance
        if self.instance and self.instance.pk:
            try:
                self.initial["college_office"] = self.instance.college_office.name
            except:
                pass

    def clean_college_office(self):
        college_office_name = self.cleaned_data["college_office"]
        college_office = CollegeOffice.objects.filter(name=college_office_name).first()

        if not college_office:
            raise forms.ValidationError("Invalide college/office selected. Please choose from the given options")
        
        return college_office