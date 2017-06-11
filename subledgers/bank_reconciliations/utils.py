# -*- coding: utf-8 -*-
import dateparser
from decimal import Decimal


""" When importing statements we want to ensure that there are not duplicate transactions.

This is impossible checking any individual line of a statement. It is possible for
details which are identical in every way to occur twice on a bank statement.

Therefore we will check each *day* and be prejudiced against any misalignment.

To do this we will:
1. import data and create dictionary with: date, value, line_dump, balance
2. we will get the oldest and newest date
3. we will iterate through each day and check to if:
  - dict obj v. bank transaction
  - sum values
  - are equal
  if so: continue. (perhaps do a count of transactions here also)
  else:
    check which has the greater COUNT of transactions.
    if DB is greater: ignore dict
    if dict >=: blow away the day in DB and reimport per this dict
"""


def bank_statement_import(data, bank):
    preprocessor = globals()['preprocess_statement_{}'.format(bank)]
    list_kwargs = preprocessor(data)
    return list_kwargs


def preprocess_statement_CBA(data):
    """ returns list of **kwargs """
    #date	value	line_dump	balance

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
        kwargs = {}
        date, value, line_dump, balance = line.split('\t')
        kwargs['date'] = dateparser.parse(date)
        kwargs['value'] = Decimal(value)
        kwargs['line_dump'] = line_dump
        kwargs['description'], kwargs['additional'] = process_line_dump(line_dump)
        kwargs['balance'] = Decimal(balance)
        processed_lines.append(kwargs)
    return processed_lines


def preprocess_statement_NAB(data):
    """ returns list of **kwargs """
    #date	value	nil	nil	additional	description	balance

    raw_lines = data.split('\r\n')
    processed_lines = []
    for line in raw_lines:
        kwargs = {}
        date, value, nil, nil, additional, description, balance = line.split('\t')
        kwargs['date'] = dateparser.parse(date)
        kwargs['value'] = Decimal(value)
        kwargs['line_dump'] = "{} {}".format(description, additional)
        kwargs['description'] = description
        kwargs['additional'] = additional
        kwargs['balance'] = Decimal(balance)
        processed_lines.append(kwargs)
    return processed_lines