# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import binascii
import os
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify


def generate_unique_slug(text, queryset, slug_field='slug', iteration=0):

    slug = slugify(text)
    if not slug:
        slug = '-'

    if iteration > 0:
        slug = '{0}-{1}'.format(iteration, slug)
    slug = slug[:50]

    try:
        queryset.get(**{slug_field: slug})
    except ObjectDoesNotExist:
        return slug
    else:
        iteration += 1
        return generate_unique_slug(text, queryset=queryset,
                                    slug_field=slug_field, iteration=iteration)

def generate_unique_hex(length=3, check=None, queryset=None):
    code = binascii.hexlify(os.urandom(length)).decode('UTF-8')
    if check:
        if code!=check:
            return code
        else:
            generate_unique_hex(check=code)
    if queryset:
        if not queryset.filter(code=code):
            return code
        else:
            generate_unique_hex(queryset=queryset)
    return code
