from django import forms
from .models import AmexTransaction

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

class DateInput(forms.DateInput):
    input_type = 'date'

class DateField(forms.DateField):
    widget = DateInput
    input_formats = ['%d-%m-%Y']

class AmexTransactionForm(forms.ModelForm):
    class Meta:
        model = AmexTransaction
        fields = ['date', 'amount', 'merchant', 'category', 'notes', 'reimbursable']
        widgets = {
            'date': DateInput(),
        }

