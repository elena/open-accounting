# -*- coding: utf-8 -*-
from django import forms
from django.utils.module_loading import import_string

from subledgers.settings import OBJECT_SETTINGS


OBJECT_CHOICES = sorted([(
    x, import_string(OBJECT_SETTINGS[x]['source'])._meta.verbose_name.title())
    for x in OBJECT_SETTINGS]) \
    + [(None, "Mixed (must define `type` column)"), ]


class BasicForm(forms.Form):

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))


class UploadForm(forms.Form):

    object_name = forms.ChoiceField(widget=forms.RadioSelect,
                                    choices=OBJECT_CHOICES,)

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))
