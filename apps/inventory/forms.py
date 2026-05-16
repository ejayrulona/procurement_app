from django import forms
from django.core.exceptions import ValidationError
from .models import ObjectOfExpenditure, ObjectCode, ItemCode, Item

class ObjectOfExpenditureForm(forms.ModelForm):
    class Meta:
        model = ObjectOfExpenditure
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                    "placeholder": "Office Supplies Expenses"
                }
            )
        }


class ObjectCodeForm(forms.ModelForm):
    expenditure = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                "id": "expenditure-dropdown", "list": "expenditure-list", "autocomplete": "off",
                "placeholder": "Office Supplies Expenses"
            }
        )
    )

    class Meta:
        model = ObjectCode
        fields = ("code",)
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                    "placeholder": "0000000000"
                }
            ),
        }

    def clean_expenditure(self):
        name = self.cleaned_data.get("expenditure")
        
        try:
            return ObjectOfExpenditure.objects.get(name=name)
        except ObjectOfExpenditure.DoesNotExist:
            raise forms.ValidationError(
                "Invalid object of expenditure. Please choose from the given options."
            )
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.expenditure = self.cleaned_data["expenditure"]

        if commit:
            instance.save()

        return instance


class ItemCodeForm(forms.ModelForm):
    object_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                "id": "object-code-dropdown", "list": "object-code-list", "autocomplete": "off",
                "placeholder": "0000000000"
            }
        )
    )
    class Meta:
        model = ItemCode
        fields = ("code", "general_description")
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                    "placeholder": "000"
                }
            ),
            "general_description": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                    "placeholder": "Bondpaper A4"
                }
            )
        }

    def clean_object_code(self):
        code = self.cleaned_data.get("object_code")

        try:
            return ObjectCode.objects.get(code=code)
        except ItemCode.DoesNotExist:
            raise forms.ValidationError(
                "Invalid object code. Please choose from the given options."
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.object_code = self.cleaned_data["object_code"]

        if commit:
            instance.save()

        return instance


class ItemForm(forms.ModelForm):
    object_of_expenditure = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                "id": "object-expenditure-dropdown", "list": "object-expenditure-list", "autocomplete": "off",
                "placeholder": ""
            }
        )
    )
    object_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                "id": "object-code-dropdown", "list": "object-code-list", "autocomplete": "off",
                "placeholder": ""
            }
        )
    )
    item_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                "id": "item-code-dropdown", "list": "item-code-list", "autocomplete": "off",
                "placeholder": ""
            }
        )
    )
    
    class Meta:
        model = Item
        fields = ("name", "specification", "unit", "unit_cost")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
                }
            ),
            "specification": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                }
            ),
            "unit_cost": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
                }
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            try:
                self.initial["object_of_expenditure"] = self.instance.item_code.object_code.expenditure.name
                self.initial["object_code"] = self.instance.item_code.object_code.code
                self.initial["item_code"] = self.instance.item_code.code
            except:
                pass

    def clean_object_of_expenditure(self):
        name = self.cleaned_data.get("object_of_expenditure")
        
        try:
            return ObjectOfExpenditure.objects.get(name=name)
        except ObjectOfExpenditure.DoesNotExist:
            raise forms.ValidationError(
                "Invalid object of expenditure. Please choose from the given options."
            )

    def clean_object_code(self):
        code = self.cleaned_data.get("object_code")
        expenditure = self.cleaned_data.get("object_of_expenditure")

        if not expenditure:
            return None

        try:
            object_code = ObjectCode.objects.get(code=code, expenditure=expenditure)
            return object_code
        except ObjectCode.DoesNotExist:
            raise forms.ValidationError(
                "Invalid object code. Please choose a code that belongs to the selected expenditure."
            )

    def clean_item_code(self):
        code = self.cleaned_data.get("item_code")
        object_code = self.cleaned_data.get("object_code")

        if not object_code:
            return None

        try:
            item_code = ItemCode.objects.get(code=code, object_code=object_code)
            return item_code
        except ItemCode.DoesNotExist:
            raise forms.ValidationError(
                "Invalid item code. Please choose a code that belongs to the selected object code."
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.item_code = self.cleaned_data["item_code"]

        if commit:
            instance.save()

        return instance