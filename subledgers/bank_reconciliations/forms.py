from __future__ import absolute_import, unicode_literals
from django import forms
from django.views import generic

from ledgers.bank_accounts.models import BankAccount
from .models import BankTransaction


class StatementUploadForm(forms.Form):

    bank = forms.ModelChoiceField(queryset=BankAccount.objects.all(), empty_label=None)
    input_data = forms.CharField(widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))
