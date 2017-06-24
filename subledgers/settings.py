# -*- coding: utf-8 -*-
from django.conf import settings

from subledgers.creditors.models import Creditor, CreditorInvoice
# from subledgers.debtors.models import Debtor, DebtorInvoice
from subledgers.bank_reconciliations.models import BankTransaction
# from subledgers.journals.models import JournalEntry
# from subledgers.expenses.models import Expense
# from subledgers.sales.models import Sale


DEFAULT_TERMS = getattr(settings, 'SUBLEDGERS_DEFAULT_TERMS', 14)

GST_DR_ACCOUNT = getattr(
    settings, 'GST_SPENT', '03-0713')

GST_CR_ACCOUNT = getattr(
    settings, 'GST_COLLECTED', '03-0733')

ACCOUNTS_PAYABLE_ACCOUNT = getattr(
    settings, 'ACCOUNTS_PAYABLE_ACCOUNT', '03-0300')

ACCOUNTS_RECEIVABLE_ACCOUNT = getattr(
    settings, 'ACCOUNTS_RECEIVABLE_ACCOUNT', '01-0300')

DEFAULT_BANK_ACCOUNT = getattr(
    settings, 'DEFAULT_BANK_ACCOUNT', '01-0101')
#  @@ TODO this is not cool
# BankAccount.objects.first().account.get_code())

EXPENSE_CLEARING_ACCOUNT = getattr(
    settings, 'EXPENSE_CLEARING_ACCOUNT', '01-0300')

SALES_CLEARING_ACCOUNT = getattr(
    settings, 'SALES_CLEARNING_ACCOUNT', '01-0300')


# @@ TODO Could use whatever Django db|forms use to get required fields.
# more control doing as follows

# `user` also, but considered separately
FIELDS_TRANSACTION_REQUIRED = ['date', 'value', 'lines', 'user',
                               'object_name', 'source']

FIELDS_TRANSACTION = FIELDS_TRANSACTION_REQUIRED + ['note']

FIELDS_ENTRY_REQUIRED = []

FIELDS_ENTRY = FIELDS_ENTRY_REQUIRED + ['additional', 'relation']

FIELDS_PAYMENT_REQUIRED = ['relation', 'bank_transaction_id']

FIELDS_PAYMENT = FIELDS_PAYMENT_REQUIRED + ['additional']

FIELDS_INVOICE_REQUIRED = ['invoice_number', 'gst_total', 'relation']

# All fields available to invoices (required or not)
FIELDS_INVOICE = FIELDS_INVOICE_REQUIRED + \
    ['order_number', 'reference', 'due_date', 'relation']

FIELD_IS_DATE = ['date']
FIELD_IS_DECIMAL = ['value', 'gst_total']
FIELD_IS_RELATION = ['relation', 'entity',
                     'creditor', 'debtor', 'creditors', 'debtors']


""" Both: `is_CR_in_tb` and `is_DR_in_tb` to be as explicit as possible.
Correctly defining CR/DR in subledgers is one of the most important aspects
of the system therefore being as clear and explicit as possible.
"""
OBJECT_SETTINGS = {
    # 'JournalEntry': {
    #     'source': JournalEntry,
    #     'fields': FIELDS_TRANSACTION,
    #     'required_fields': FIELDS_TRANSACTION_REQUIRED,
    # },
    'BankTransaction': {
        'source': BankTransaction,
        'tb_account': DEFAULT_BANK_ACCOUNT,
        'is_DR_in_tb': True,
        'fields': FIELDS_TRANSACTION,
        'required_fields': FIELDS_TRANSACTION_REQUIRED,
    },

    # 'Sale': {
    #     'source': Sale,
    #     'tb_account': SALES_CLEARING_ACCOUNT,
    #     'is_DR_in_tb': True,
    #     'fields': FIELDS_TRANSACTION,
    #     'required_fields': FIELDS_TRANSACTION_REQUIRED,
    # },
    # 'Expense': {
    #     'source': Expense,
    #     'tb_account': EXPENSE_CLEARING_ACCOUNT,
    #     'is_CR_in_tb': True,
    #     'fields': FIELDS_TRANSACTION,
    #     'required_fields': FIELDS_TRANSACTION_REQUIRED,
    # },
    # 'Sale': {
    #     'source': Sale,
    #     'tb_account': SALES_CLEARING_ACCOUNT,
    #     'is_DR_in_tb': True,
    #     'fields': FIELDS_TRANSACTION,
    #     'required_fields': FIELDS_TRANSACTION_REQUIRED,
    # },
    # 'Expense': {
    #     'source': Expense,
    #     'tb_account': EXPENSE_CLEARING_ACCOUNT,
    #     'is_CR_in_tb': True,
    #     'fields': FIELDS_TRANSACTION,
    #     'required_fields': FIELDS_TRANSACTION_REQUIRED,
    # },

    'CreditorInvoice': {
        'uses_invoices': True,
        'entity': Creditor,
        'source': CreditorInvoice,
        'tb_account': ACCOUNTS_PAYABLE_ACCOUNT,
        'is_CR_in_tb': True,
        'fields': FIELDS_INVOICE,
        'required_fields': FIELDS_INVOICE_REQUIRED,
    },
    # 'CreditorPayment': {
    #     'entity': Creditor,
    #     'source': CreditorPayment,
    #     'tb_account':
    #     'is_CR_in_tb':
    #     'fields':
    #     'required_fields':
    # },


    # 'DebtorInvoice': {
    #     'uses_invoices': True,
    #     'entity': Debtor,
    #     'source': DebtorInvoice,
    #     'tb_account':  ACCOUNTS_RECEIVABLE_ACCOUNT,
    #     'is_DR_in_tb': True,
    #     'fields': FIELDS_INVOICE,
    #     'required_fields': FIELDS_INVOICE_REQUIRED,
    # },

}

OBJECT_CHOICES = sorted([(x, OBJECT_SETTINGS[x]['source']._meta.verbose_name.title())  # noqa
                         for x in OBJECT_SETTINGS])
