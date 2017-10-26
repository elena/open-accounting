# -*- coding: utf-8 -*-
import re
import dateparser
from datetime import date, datetime
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
from django.utils.module_loading import import_string

from ledgers.periods import settings


def get_months(fyear):
    return [d.isoformat()[:7] for d in rrule(
        MONTHLY, count=12,
        dtstart=settings.FINANCIAL_YEARS[fyear][0])]


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


def make_date(value):
    """ Open to serious integrity error because of USA v. ISO8601 date
    variation, eg: 5-2-2017 v. 2-5-2017 (May or Feb?).

    Firmly enforce non-ambiguous date by Month as word eg: 2-May-2017.
    """
    if type(value)==date:
        return value

    if type(value)==datetime:
        return value

    month_as_word = re.sub(r'[^a-zA-Z.]', '', value)
    if not month_as_word:
        raise Exception(
            "Ambiguous date provided. Please provide month as word. eg: GOOD: 2-May-2017 BAD: 2017-02-05")  # noqa
    return dateparser.parse(value)


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


def make_CRDR(value):
    if value > 0:
        return '{:,.2f} DR'.format(value)
    elif value == 0:
        return ''
    else:
        return '-{:,.2f} CR'.format(-value)


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
