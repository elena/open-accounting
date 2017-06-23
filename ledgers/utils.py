# -*- coding: utf-8 -*-
import re
from decimal import Decimal


def get_source(source):
    """ source is project model Class """
    return "{}".format(source.__module__).replace("models", source.__name__)


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
