# -*- coding: utf-8 -*-
from importlib import import_module
from ledgers import utils


def process_tax(country_code, cls, kwargs):
    settings = import_module(
        'subledgers.taxes.{}.settings'.format(country_code))
    object_settings = settings.OBJECT_SETTINGS

    lines = kwargs['lines']

    # @@ TODO facilitate other taxes and surcharges.
    if object_settings.get('is_GST'):

        # There are 2 methods of adding GST:
        # 1. defining GST_CR_ACCOUNT or GST_DR_ACCOUNT among lines
        #  or
        # 2. defining `GST_total` column on import

        # First check if GST_CR_ACCOUNT or GST_DR_ACCOUNT lines exist
        gst_allocated = False
        for line in lines:
            if line[0] == settings.GST_DR_ACCOUNT\
               or line[0] == settings.GST_CR_ACCOUNT:
                gst_allocated = True

        # If not:
        # - set line value using `GST_total` column value
        # - set acccount using `is_tb_account_DR/CR` to get `GST_DR/CR_ACCOUNT`
        # Note: the value +/- is correct to subledger. May not be correct for
        #       the tb. +/- corrected to tb set in different process.
        if not gst_allocated:
            # note: correct GST account, abs value
            # fix dr/cr +/- in next process, not here.
            if object_settings.get('is_tb_account_DR'):
                lines.append((
                    settings.GST_DR_ACCOUNT,
                    utils.make_decimal(kwargs['gst_total'])))
            if object_settings.get('is_tb_account_CR'):
                lines.append((
                    settings.GST_CR_ACCOUNT,
                    utils.make_decimal(kwargs['gst_total'])))
    return lines
