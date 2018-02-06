# -*- coding: utf-8 -*-
from django import forms
from django.utils.module_loading import import_string

from subledgers.settings import OBJECT_SETTINGS


OBJECT_CHOICES = [(None, "Mixed (must define `type` column)"), ] + sorted([(
    x, import_string(OBJECT_SETTINGS[x]['source'])._meta.verbose_name.title())
    for x in OBJECT_SETTINGS])

LIVE = [
    (1, 'Live'),
    (0, 'Not Live'),
]


class BasicForm(forms.Form):

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))


class UploadForm(forms.Form):

    object_name = forms.ChoiceField(widget=forms.RadioSelect,
                                    choices=OBJECT_CHOICES,)

    live = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=LIVE)

    input_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 15, 'cols': 100}))
