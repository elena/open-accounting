# -*- coding: utf-8 -*-
import re

from decimal import Decimal
from django.db.models import Model
from django.db.models.base import ModelBase
from django.utils.module_loading import import_string


def get_source(source):
    """ source is project model Class.

    input class Object or string path

    Returns consistent output to save as reference.
    """
    try:
        Obj = source._meta.model
    except AttributeError:
        Obj = import_string(source)
    return "{}.{}".format(Obj.__module__, Obj.__name__)


def get_source_name(source):
    return source.split(".").last()


def make_decimal(value):
    try:
        return round(Decimal(re.sub(r'[^\d\-.]', '', value)), 2)
    except TypeError:
        return round(Decimal(value), 2)


def set_CR(value):
    """ These functions only exist to make CR/DR really clear.
    Otherwise setting CR is mere tiny little easily missable minus sign. """
    return -make_decimal(value)


def set_DR(value):
    """ These functions only exist to make CR/DR really clear. """
    return make_decimal(value)


def tsv_to_dict(dump):
    """ Make a sensible k,v dict from imported tsv.

    No validation is done here, just simple conversion."""
    try:
        rows = [items for items in dump.split("\r\n")]
        header_row = rows[0].split("\t")
        list_row_dicts = []
        for item in rows[1:]:
            row_dict = dict(list(zip(header_row, item.split("\t"))))
            list_row_dicts.append(row_dict)
        return list_row_dicts
    except:
        raise Exception("""Failed to convert dump to dict.

All that is required is a copy and paste from a spreadsheet.""")
