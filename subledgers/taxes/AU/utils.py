# -*- coding: utf-8 -*-
from ledgers import utils
from ledgers.models import Account
from . import settings


def process_tax(cls, kwargs, lines):
    """ Just a check that GST is defined if required.

    If subledger requires GST error will be raised if GST
    not defined.

    GST should be defined in one of two ways:
    - GST tb account being used
    - `GST total` column/ `gst_total` key in kwargs
    """
    object_settings = settings.OBJECT_SETTINGS[utils.get_source_name(cls)]

    # @@ TODO facilitate other taxes and surcharges.
    if object_settings.get('is_GST'):

        # There are 2 methods of adding GST:
        # 1. defining GST_CR_ACCOUNT or GST_DR_ACCOUNT among lines
        #  or
        # 2. defining `GST_total` column on import

        # First check if GST_CR_ACCOUNT or GST_DR_ACCOUNT lines exist
        gst_allocated = False
        for line in lines:
            if Account.get_account(line[0]) == \
               Account.get_account(settings.GST_DR_ACCOUNT)\
               or Account.get_account(line[0]) == \
               Account.get_account(settings.GST_CR_ACCOUNT):
                gst_allocated = True

        # If not:
        # - set line value using `GST_total` column value
        # - set acccount using `is_tb_account_DR/CR` to get `GST_DR/CR_ACCOUNT`
        # Note: the value +/- is correct to subledger. May not be correct for
        #       the tb. +/- corrected to tb set in different process.

        if not gst_allocated:
            # note: correct GST account, abs value
            # fix dr/cr +/- in next process, not here.

            if not kwargs['gst_total'] in ['', None, 0]:
                if object_settings.get('is_tb_account_DR'):
                    lines.append((
                        settings.GST_DR_ACCOUNT,
                        utils.make_decimal(kwargs['gst_total'])))
                if object_settings.get('is_tb_account_CR'):
                    lines.append((
                        settings.GST_CR_ACCOUNT,
                        utils.make_decimal(kwargs['gst_total'])))

    return lines
