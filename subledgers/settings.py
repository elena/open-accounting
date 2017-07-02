# -*- coding: utf-8 -*-
from django.conf import settings


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
    settings, 'EXPENSE_CLEARING_ACCOUNT', '03-0430')

SALES_CLEARING_ACCOUNT = getattr(
    settings, 'SALES_CLEARNING_ACCOUNT', '03-0410')


# @@ TODO Could use whatever Django db|forms use to get required fields.
# more control doing as follows

# `user` also, but considered separately

OTHER_REQUIRED_FIELDS = ['object_name', 'cls', 'lines']
# manually add 'lines' to Transacton.save(lines=lines)

FIELDS_TRANSACTION_REQUIRED = ['date', 'value', 'user', 'source']

FIELDS_TRANSACTION = FIELDS_TRANSACTION_REQUIRED + ['note']

FIELDS_ENTRY_REQUIRED = []

FIELDS_ENTRY = FIELDS_ENTRY_REQUIRED + ['additional', 'relation']

FIELDS_BANK_ENTRY_REQUIRED = ['bank_transaction_id']

FIELDS_BANK_ENTRY = FIELDS_BANK_ENTRY_REQUIRED + ['additional']

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
    'JournalEntry': {
        'relation_class': 'entities.models.Entity',
        'source': 'subledgers.journals.models.JournalEntry',
        'fields': FIELDS_ENTRY,
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },
    'BankEntry': {
        'relation_class': False,
        'source': 'subledgers.bank_reconciliations.models.BankEntry',
        'is_tb_account_DR': True,
        'fields': FIELDS_BANK_ENTRY,
        'required_fields': FIELDS_BANK_ENTRY_REQUIRED,
    },

    'Sale': {
        'is_GST': True,
        'source': 'subledgers.sales.models.Sale',
        'tb_account': SALES_CLEARING_ACCOUNT,
        'is_tb_account_DR': True,
        'fields': FIELDS_ENTRY,
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },
    'Expense': {
        'is_GST': True,
        'relation_class': 'entities.models.Entity',
        'source': 'subledgers.expenses.models.Expense',
        'tb_account': EXPENSE_CLEARING_ACCOUNT,
        'is_tb_account_CR': True,
        'fields': FIELDS_ENTRY,
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },

    'CreditorInvoice': {
        'is_GST': True,
        'relation_class': 'subledgers.creditors.models.Creditor',
        'source': 'subledgers.creditors.models.CreditorInvoice',
        'tb_account': ACCOUNTS_PAYABLE_ACCOUNT,
        'is_tb_account_CR': True,
        'fields': FIELDS_INVOICE,
        'required_fields': FIELDS_INVOICE_REQUIRED,
    },
    'CreditorPayment': {
        'relation_class': 'subledgers.creditors.models.Creditor',
        'source': 'subledgers.creditors.models.CreditorPayment',
        'tb_account': ACCOUNTS_PAYABLE_ACCOUNT,
        'is_DR_in_tb': True,
        'fields': FIELDS_PAYMENT,
        'required_fields': FIELDS_PAYMENT_REQUIRED,
    },


    # 'DebtorInvoice': {
    #     'is_GST': True,
    #     'entity': Debtor,
    #     'source': DebtorInvoice,
    #     'tb_account':  ACCOUNTS_RECEIVABLE_ACCOUNT,
    #     'is_DR_in_tb': True,
    #     'fields': FIELDS_INVOICE,
    #     'required_fields': FIELDS_INVOICE_REQUIRED,
    # },

}

VALID_SOURCES = [OBJECT_SETTINGS[obj_name]['source']
                 for obj_name in [key for key in OBJECT_SETTINGS]]
