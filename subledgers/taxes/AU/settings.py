# -*- coding: utf-8 -*-
from django.conf import settings


GST_VALUE = 0.1

GST_DR_ACCOUNT = getattr(
    settings, 'GST_SPENT', '03-0713')

GST_CR_ACCOUNT = getattr(
    settings, 'GST_COLLECTED', '03-0733')

OBJECT_SETTINGS = {
    'Sale': {
        'is_GST': True,
        'is_tb_account_DR': True,
    },
    'Expense': {
        'is_GST': True,
        'is_tb_account_CR': True,
    },
    'CreditorInvoice': {
        'is_GST': True,
        'is_tb_account_CR': True,
    },
    'DebtorInvoice': {
        'is_GST': True,
        'is_tb_account_DR': True,
    },
}
