from django import forms
from .models import ProcurementProjectManagementPlan

class PPMPForm(forms.ModelForm):
    class Meta:
        model = ProcurementProjectManagementPlan
        fields = ("classification", "source_of_funds", "fiscal_year", "ceiling")
        widgets = {
            "classification": forms.Select(
                attrs={
                    "class": "w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 transition bg-white"
                }
            ),
            "source_of_funds": forms.Select(
                attrs={
                    "class": "w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 transition bg-white"
                }
            ),
            "fiscal_year": forms.NumberInput(
                attrs={
                    "class": "w-full border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 transition",
                    "readonly": True
                }
            ),
            "ceiling": forms.NumberInput(
                attrs={
                    "class": "w-full pl-8 border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 transition"
                }
            )
        }

    def clean_fiscal_year(self):
        fiscal_year = self.cleaned_data.get("fiscal_year")

        if fiscal_year < 2000 or fiscal_year > 2100:
            raise forms.ValidationError("Please enter a valid fiscal year.")

        return fiscal_year

    def clean_ceiling(self):
        ceiling = self.cleaned_data.get("ceiling")

        if ceiling <= 0:
            raise forms.ValidationError("Ceiling amount must be greater than zero.")

        return ceiling