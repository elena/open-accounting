# -*- coding: utf-8 -*-
from decimal import Decimal

from .models import BankTransaction
from ledgers.utils import make_date
from ledgers.bank_accounts.models import BankAccount

""" When importing statements we want to ensure that there are not
duplicate transactions.

This is impossible checking any individual line of a statement. It is
possible for details which are identical in every way to occur twice on a
bank statement.
"""


def import_bank_statement(data):

    results = []
    bank = BankAccount.objects.get(pk=data['bank'])
    preprocessor = globals()['preprocess_statement_{}'.format(bank.bank)]

    # 1. generate list of **kwargs based on lines from statement
    list_kwargs = preprocessor(data['input_data'])

    for kwargs in list_kwargs:
        new = BankTransaction(bank_account=bank, **kwargs)
        new.save()
        results.append(new)

    return results


def preprocess_statement_CBA(data):
    """ returns list of **kwargs """
    # date	value	line_dump	balance

    def process_line_dump(line_dump):
        splits = [
            'Card xx',
            'Value Date: ',
            'BPAY ',
        ]
        for split in splits:
            try:
                description, additional = line_dump.split(split)
                return description, "{}{}".format(split, additional)
            except ValueError:
                return line_dump, ''

    raw_lines = data.split('\r\n')
    processed_lines = []
    for line in raw_lines:
        if line.split('\t')[0] == 'date':
            continue
        kwargs = {}
        date, value, line_dump, balance = line.split('\t')
        kwargs['date'] = make_date(date).date()
        kwargs['value'] = Decimal(value)
        kwargs['line_dump'] = line_dump
        kwargs['description'], kwargs['additional'] = process_line_dump(
            line_dump)
        kwargs['balance'] = Decimal(balance)
        processed_lines.append(kwargs)
    return processed_lines


def preprocess_statement_NAB(data):
    """ returns list of **kwargs """
    # date	value	nil	nil	additional	description	balance

    raw_lines = data.split('\r\n')
    processed_lines = []
    for line in raw_lines:
        kwargs = {}
        date, value, nil, nil, additional, description, balance = line.split(
            '\t')
        kwargs['date'] = make_date(date).date()
        kwargs['value'] = Decimal(value)
        kwargs['line_dump'] = "{} {}".format(description, additional)
        kwargs['description'] = description
        kwargs['additional'] = additional
        kwargs['balance'] = Decimal(balance)
        processed_lines.append(kwargs)
    return processed_lines
