from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, AdminProfile, OfficeProfile

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
        

class UserEditForm(forms.ModelForm):
    class Meta():
        model = User
        fields = (
            "username", "first_name", "middle_name", "last_name", "email", "phone_number"
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


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full py-3 pl-10 pr-4 transition-all duration-200 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 focus:ring-1 focus:ring-red-400",
                "placeholder": "Current Password"
            }
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full py-3 pl-10 pr-4 transition-all duration-200 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 focus:ring-1 focus:ring-red-400",
                "placeholder": "New Password"
            }
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full py-3 pl-10 pr-4 transition-all duration-200 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 focus:ring-1 focus:ring-red-400",
                "placeholder": "Confirm Password"
            }
        )
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


class OfficeReapplyUserForm(forms.ModelForm):
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

    
class OfficeProfileForm(forms.ModelForm):
    class Meta:
        model = OfficeProfile
        fields = ("pap_category", "office_name", "office_logo", "secretary_full_name", "secretary_email", "secretary_phone_number")
        widgets = {
            "pap_category": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": ""
                }
            ),
            "office_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "College of Computing Studies"
                }
            ),
            "office_logo": forms.FileInput(
                attrs={
                    "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100",
                    "id": "profile-photo-id", "accept": "image/*"
                }
            ),
            "secretary_full_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "Maria Angela Reyes"
                }
            ),
            "secretary_email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "maria@gmail.com"
                }
            ),
            "secretary_phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 focus:bg-white focus:border-red-400 transition-all duration-200",
                    "placeholder": "123 456 7890"
                }
            ),
        }