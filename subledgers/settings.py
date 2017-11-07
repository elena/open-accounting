# -*- coding: utf-8 -*-
from django.conf import settings


DEFAULT_TERMS = getattr(settings, 'SUBLEDGERS_DEFAULT_TERMS', 14)

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL')

AGED_PERIODS = [7, 14, 30, 60, 90, 120]

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Default ledger accounts
#
# @@ This is very opinionated. Will certainly have to be improved.

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


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

PAYROLL_CLEARING_ACCOUNT = getattr(
    settings, 'PAYROLL_CLEARNING_ACCOUNT', '03-0450')


# This is used to categorise bank transactions
# 3rd field is namespace used to generate URLs for jumping to matching page
SUBLEDGERS_AVAILABLE = {
    'creditors': {
        'human': 'Creditor',
        'account': ACCOUNTS_PAYABLE_ACCOUNT,
        'url': '/acp/'},
    'expenses': {
        'human': 'Expense',
        'account': EXPENSE_CLEARING_ACCOUNT,
        'url': None},  # '/expenses/' },
    'sales': {
        'human': 'Sale',
        'account': SALES_CLEARING_ACCOUNT,
        'url': None},  # '/sales/'},
    'wages': {
        'human': 'Payroll',
        'account': PAYROLL_CLEARING_ACCOUNT,
        'url': None},
    'journals': {
        'human': 'Journal',
        'account': None,
        'url': None},  # '/journals/'},
    'bank_reconciliations': {
        'human': 'Bank Reconciliation',
        'account': None,
        'url': '/bank/reconciliations/'},
    # 'debtors', ACCOUNTS_RECEIVABLE_ACCOUNT
    # 'wages',
}


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Field definitions

# For use in imports.
# @@ Explore making view for each import type.

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# @@ TODO Could use whatever Django db|forms use to get required fields.
# more control doing as follows

# `user` also, but considered separately

OTHER_REQUIRED_FIELDS = ['lines']
# manually add 'lines' to Transacton.save(lines=lines)

FIELDS_TRANSACTION_REQUIRED = ['date', 'value', 'user', 'source']

FIELDS_ENTRY_REQUIRED = []
FIELDS_BANK_ENTRY_REQUIRED = ['bank_transaction_id']
FIELDS_PAYMENT_REQUIRED = ['relation', 'bank_transaction_id']
FIELDS_INVOICE_REQUIRED = ['invoice_number', 'gst_total', 'relation']

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
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },
    'BankEntry': {
        'relation_class': False,
        'source': 'subledgers.bank_reconciliations.models.BankEntry',
        'is_tb_account_CR': True,
        'required_fields': FIELDS_BANK_ENTRY_REQUIRED,
    },


    'Sale': {
        'source': 'subledgers.sales.models.Sale',
        'tb_account': SALES_CLEARING_ACCOUNT,
        'is_tb_account_DR': True,
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },

    # 'DebtorInvoice': {
    #     'relation_class': 'subledgers.debtors.models.Debtor',
    #     'source': 'subledgers.debtors.models.DebtorInvoice',
    #     'tb_account': ACCOUNTS_RECEIVABLE_ACCOUNT,
    #     'is_tb_account_DR': True,
    #     'required_fields': FIELDS_INVOICE_REQUIRED,
    # },

    # 'DebtorPayment': {
    #     'relation_class': 'subledgers.debtors.models.Debtor',
    #     'source': 'subledgers.debtors.models.DebtorPayment',
    #     'tb_account': ACCOUNTS_RECEIVABLE_ACCOUNT,
    #     'is_tb_account_CR': True,
    #     'required_fields': FIELDS_PAYMENT_REQUIRED,
    # },


    'Expense': {
        'relation_class': 'entities.models.Entity',
        'source': 'subledgers.expenses.models.Expense',
        'tb_account': EXPENSE_CLEARING_ACCOUNT,
        'is_tb_account_CR': True,
        'required_fields': FIELDS_ENTRY_REQUIRED,
    },

    'CreditorInvoice': {
        'relation_class': 'subledgers.creditors.models.Creditor',
        'source': 'subledgers.creditors.models.CreditorInvoice',
        'tb_account': ACCOUNTS_PAYABLE_ACCOUNT,
        'is_tb_account_CR': True,
        'required_fields': FIELDS_INVOICE_REQUIRED,
    },

    'CreditorPayment': {
        'relation_class': 'subledgers.creditors.models.Creditor',
        'source': 'subledgers.creditors.models.CreditorPayment',
        'tb_account': ACCOUNTS_PAYABLE_ACCOUNT,
        'is_tb_account_DR': True,
        'required_fields': FIELDS_PAYMENT_REQUIRED,
    },
}

VALID_SOURCES = [OBJECT_SETTINGS[obj_name]['source']
                 for obj_name in [key for key in OBJECT_SETTINGS]]
