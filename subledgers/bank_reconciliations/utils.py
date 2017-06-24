# -*- coding: utf-8 -*-
import dateparser
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum

from .models import BankTransaction
from ledgers.bank_accounts.models import BankAccount

""" When importing statements we want to ensure that there are not
duplicate transactions.

This is impossible checking any individual line of a statement. It is
possible for details which are identical in every way to occur twice on a
bank statement.

Therefore we will check each *day* and be prejudiced against any
misalignment.

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


def import_bank_statement(data):

    results = []
    bank = BankAccount.objects.get(pk=data['bank'])
    preprocessor = globals()['preprocess_statement_{}'.format(bank.bank)]

    # 1. generate list of **kwargs based on lines from statement
    list_kwargs = preprocessor(data['input_data'])

    # 2. get oldest and newest dates to iterate through
    dates = [x['date'] for x in list_kwargs]
    working_date, max_date = min(dates), max(dates)

    # 3. iterate through date, check integrity against existing objects
    while working_date <= max_date:
        sum_value_obj = BankTransaction.objects.filter(
            date=working_date).aggregate(Sum('value'))
        sum_value_kwargs = sum(
            [x['value'] for x in list_kwargs if x['date'] == working_date])
        list_day_obj = BankTransaction.objects.filter(date=working_date)
        list_day_kwargs = [x for x in list_kwargs if x['date'] == working_date]

        if list_day_obj.count() == 0:
            # Nothing exists in database.
            # There are no objects, create new objects.
            for kwargs in list_day_kwargs:
                new = BankTransaction(bank_account=bank, **kwargs)
                new.save()
                results.append(new)
            working_date += timedelta(1)
            continue
        elif sum_value_obj['value__sum'] == sum_value_kwargs \
                and len(list_day_obj) == len(list_day_kwargs):
            # Seems to be perfect match in database.
            # Sum and count both match, continue.
            # @@TODO still edge cases here.
            working_date += timedelta(1)
            continue
        else:
            # Mismatch:
            # Firstly sift out any object which may have already been matched
            for obj in list_day_obj:
                if obj.transaction:
                    # if object is already matched try and find match in
                    # list_kwargs and remove it from this list
                    match_list = [
                        x for x in list_kwargs if x['value'] == obj.value]
                    if len(match_list) == 0:
                        # obj missed out on import
                        continue
                    elif len(match_list) == 1:
                        # 1 match easy to remove
                        list_day_kwargs.remove(match_list[0])
                    else:
                        # if multiple matches try and get a better match
                        match_list2 = [
                            x for x in match_list if x['balance'] == obj.balance]  # noqa
                        if len(match_list2) == 0:
                            match_list3 = [x for x in match_list
                                           if x['description'] == obj.description]  # noqa
                            if match_list3:
                                list_day_kwargs.remove(match_list3[0])
                            else:
                                list_day_kwargs.remove(match_list[0])
                        elif len(match_list2) == 1:
                            list_day_kwargs.remove(match_list2[0])
                        else:
                            match_list3 = [x for x in match_list2
                                           if x['description'] == obj.description]  # noqa
                            if match_list3:
                                list_day_kwargs.remove(match_list3[0])
                            else:
                                list_day_kwargs.remove(match_list2[0])
                else:
                    # the newer/greater statement should be correct, delete
                    # anything not already matched.
                    obj.delete()
            # should have reduced kwargs list, now create new obj.
            for kwargs in list_day_kwargs:
                new = BankTransaction(bank_account=bank, **kwargs)
                new.save()
                results.append(new)
            working_date += timedelta(1)
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
        kwargs['date'] = dateparser.parse(
            date, settings={'DATE_ORDER': 'DMY'}).date()
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
        kwargs['date'] = dateparser.parse(
            date, settings={'DATE_ORDER': 'DMY'}).date()
        kwargs['value'] = Decimal(value)
        kwargs['line_dump'] = "{} {}".format(description, additional)
        kwargs['description'] = description
        kwargs['additional'] = additional
        kwargs['balance'] = Decimal(balance)
        processed_lines.append(kwargs)
    return processed_lines
