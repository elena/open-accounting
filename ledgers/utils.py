# -*- coding: utf-8 -*-
import re
import dateparser
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
from django.utils.module_loading import import_string

from ledgers.periods import settings as period_settings
from subledgers import settings as subledger_settings


# Classes


def get_source(source):
    """ Returns string.

    Provide ModelObject or str.path to Model

    eg. as per OBJECT_SETTINGS[source] or 'subledgers.journals.JournalEntry'

    Returns consistent output to save as reference.
    """
    try:
        Obj = source._meta.model
    except AttributeError:
        Obj = import_string(source)
    return "{}.{}".format(Obj.__module__, Obj.__name__)


def get_source_name(source):
    source = get_source(source)
    return source.split(".")[-1]


def get_cls(name):
    """ Returns ModelObject.

    Input variations (convert to source_str):
    # 1. ModelObject or str.path to Model (per OBJECT_SETTINGS[source])
    # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
    # 3. source_str
    """

    # 1. ModelObject
    #    *or* str.path to Model (per OBJECT_SETTINGS[source])
    try:
        source = get_source(name)
    except ImportError:
        pass

    # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
    try:
        source = subledger_settings.OBJECT_SETTINGS[name]['source']
    except KeyError:
        pass

    # check is a VALID_SOURCES and return
    try:
        if get_source(source) in subledger_settings.VALID_SOURCES:
            cls = import_string(source)
            return cls
        else:
            raise Exception("Not a VALID SOURCE `type` {}.".format(name))
    except UnboundLocalError:
        raise Exception("No valid upload `type` {}.".format(name))
    raise Exception("No valid `type` found for {}.".format(name))


# Dates


def make_date(value):
    """ Open to serious integrity error because of USA v. ISO8601 date
    variation, eg: 5-2-2017 v. 2-5-2017 (May or Feb?).

    Firmly enforce non-ambiguous date by Month as word eg: 2-May-2017.
    """
    if type(value) == date:
        return value

    if type(value) == datetime:
        return value

    if type(value) is str and len(value) == 8:
        try:
            return date(int(value[0:4]), int(value[4:6]), int(value[6:8]))
        except ValueError:
            pass

    if type(value) is str and len(value) == 7:
        try:
            return date(int(value[0:4]), int(value[5:7]), 1)
        except ValueError:
            pass

    if type(value) is str and len(value) == 6:
        try:
            return date(int(value[0:4]), int(value[4:6]), 1)
        except ValueError:
            pass

    month_as_word = re.sub(r'[^a-zA-Z.]', '', value)
    if not month_as_word:
        raise Exception(
            "Ambiguous date provided. Please provide month as word. eg: GOOD: 2-May-2017 BAD: 2017-02-05")  # noqa

    return dateparser.parse(value)


def make_date_end(value):
    end_date = make_date(value)
    year, mth = end_date.year, end_date.month
    return date(year, mth, monthrange(year, mth)[1])


def get_months_fyear(fyear):
    return [d.isoformat()[:7] for d in rrule(
        MONTHLY, count=12,
        dtstart=period_settings.FINANCIAL_YEARS[fyear][0])]


def get_months(start, end):
    months_list = []
    start, end = make_date(start), make_date_end(end)
    while start < end:
        months_list.append(start.isoformat()[:7])
        start = start + relativedelta(months=1)
    return months_list


# Numbers Formats


def make_decimal(value):
    if value in ['', False, None]:
        value = 0
    try:
        return round(Decimal(re.sub(r'[^0-9\-.]', '', value)), 2)
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


# ===

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
