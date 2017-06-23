# -*- coding: utf-8 -*-
from django import forms

from subledgers.settings import OBJECT_CHOICES


OBJECT_CHOICES = OBJECT_CHOICES + [
    (None, "Mixed (must define `type` column)"),
]


class BasicForm(forms.Form):

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))


class UploadForm(forms.Form):

    object_name = forms.ChoiceField(widget=forms.RadioSelect,
                                    choices=OBJECT_CHOICES,)

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))
