# -*- coding: utf-8 -*-
from django import forms
from .models import Account


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('element', 'parent', 'number', 'name')
