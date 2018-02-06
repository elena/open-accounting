from __future__ import absolute_import, unicode_literals
from django import forms
# from django.views import generic

from ledgers.bank_accounts.models import BankAccount
# from .models import BankLine


class StatementUploadForm(forms.Form):

    bank = forms.ModelChoiceField(
        queryset=BankAccount.objects.all(), empty_label=None)
    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))


class BankReconciliationForm(forms.Form):

    pk = forms.IntegerField()
    account = forms.CharField()  # checked on model, str is fine here
    value = forms.DecimalField()
    notes = forms.CharField(required=False)
    line_notes = forms.CharField(required=False)
    date = forms.DateField()
