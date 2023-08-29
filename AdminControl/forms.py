from django import forms
from .models import BatchCode

class BatchForm(forms.Form):
    batchCode = forms.ModelChoiceField(queryset=BatchCode.objects.all(), empty_label=None)
    batchCode.label = "Select the batchCode "