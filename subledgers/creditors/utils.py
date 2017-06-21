# -*- coding: utf-8 -*-
import dateparser
import re
from datetime import date, time, timedelta
from decimal import Decimal

from entities.models import Entity
from ledgers.models import Account, Transaction
from ledgers.utils import get_source, make_decimal, set_CR, set_DR
from ..settings import ACCOUNTS_PAYABLE_ACCOUNT, GST_EXPENSE_ACCOUNT
from .models import Creditor, CreditorInvoice

""" Importing creditor statements

@@TODO THIS IS NOT ROBUST! This is very opinionated in this first version.

Trying to get it out get it out get it out.
"""


def import_creditors(data, user, single_pass=True):

    results = []
    list_kwargs = {}

    # 1. normalise the data
    #    make a sensible k,v dict from imported tsv

    # @@ TODO make this in to reusable function!!

    list_data = [items for items in data.split("\r\n")]
    header, tmp_map, transactions = list_data[0].split("\t"), [], []
    header[0] = 'entity'
    for item in list_data[1:]:
        tmp = list(zip(header, item.split("\t")))
        tmp_map.append(dict(tmp))

    # 2. populate a formset

    # @@ TODO
    # preflight check to test for duds
    # duds: - not minimum required
    #       - entity doesn't exist
    # return them still but at the end and separately
    # required = ['date', 'invoice_number', 'gst_total', 'value']
    # other = ['order_number', 'reference', 'note']

    # ~ ** ~~ THIS VERSION MUST STRAIGHT MATCH ~~*~
    # nothing time-consuming and fancy this round please.

    for item in tmp_map:

        # @@ TODO Make function to get entity (for acp and acr)
        # def get_entity(value, subledger=[acr|acp]

        # get or create creditor/entity
        try:
            item['creditor'] = Creditor.objects.get(
                entity__code=item['entity'])
        except Creditor.DoesNotExist:
            try:
                # entity exists but creditor does not.
                # get entity, create creditor.
                entity = Entity.objects.get(code=item['entity'])
                item['creditor'] = Creditor.objects.create(entity=entity)
            except:
                # return just the string
                # @@ TOOD make this better
                raise Exception(
                    "Creditor or Entity doesn't exist: {}".format(item['entity']))

        # @@ TODO Tidy to convert numbers
        # using `make_decimal`
        # money_values = ['value', 'gst_total']

        # clean up value (for good luck)
        item['value'] = Decimal(re.sub(r'[^\d\-.]', '', item.get('value')))

        if item.get('gst_total'):
            item['gst_total'] = Decimal(
                re.sub(r'[^\d.]', '', item.get('gst_total')))
        else:
            # calculate GST
            item['gst_total'] = round(float(item['value']) / 10, 2)

        # @@ TODO make better robust line conversion
        # this is very flakey and specific!
        # 2-part function, only 2 inputs are necessary
        # output quite fussy
        # defining 'account' in dump less good, prefix "["?
        # prefix "[" and when striped is account number ...

        # construct lines
        lines = []
        for k, v in item.items():
            if k[0] == "[" and len(k) == 9 and not v == "":
                lines.append((Account.get_account(k), v))

        results = lines

        # construct dictionary with values we want
        # this is single dict, for potential use in formset

        transaction = {'creditor': item['creditor'],
                       'date': dateparser.parse(item['date']),
                       'invoice_number': item['invoice_number'],
                       'order_number': item.get('order_number'),
                       'reference': item.get('reference'),
                       'gst_total': Decimal(item['gst_total']),
                       'value': float(item['value']),
                       'note': item.get('note'),
                       'lines': lines
                       }
        transactions.append(transaction)

    """
    Single Pass v. Multiple Pass (checking screens)

   # Output diverges
    @@TODO make separate functions or something.

    Output can be a list of kwargs or just straight up unsaved objects.
    """

    if single_pass:
        """ Must check for FAILURES and REPORT them.

        @@ First pass:

        RAISE any error, fail the whole lot.

        """
        # Check all first.

        for index, item in enumerate(transactions):

            # 0. Quick pass for obvious failures

            # @@ TODO OMGZ ... generalise this ffs.

            ERR_MSG = " provided for item {}. Nothing has been saved."

            if not type(item.get('creditor')) == Creditor:
                raise Exception(
                    "Creditor or Entity doesn't exist: {}. Nothing has been saved.".format(
                        item['entity']))

            if not item.get('invoice_number'):
                raise Exception(
                    "No invoice number{}".format(ERR_MSG.format(index)))

            if not item.get('date'):
                raise Exception(
                    "No date{}".format(ERR_MSG.format(index)))

            if not item.get('value'):
                raise Exception(
                    "No invoice total{}".format(ERR_MSG.format(index)))

            if not item.get('lines'):
                raise Exception(
                    "No accounts{}".format(ERR_MSG.format(index)))

            # test sums correctly
            item_value = 0
            for line in item.get('lines'):
                account, value = line
                item_value += Decimal(value)

            lines_total = Decimal(round(item_value + item.get('gst_total'), 2))
            value = Decimal(round(item.get('value'), 2))
            if not lines_total == round(value, 2):
                raise Exception("Doesn't add up for item {}: Lines + GST ({}) doesn't equal Value({}). Nothing has been saved.".format(
                    index, lines_total, value))

        # Make sure all are checked before continuing.

        new_transactions = []
        new_invoices = []
        for index, item in enumerate(transactions):

            # 1. Create Transaction
            # don't need to use items.get below this. It should be checked.

            # CR/DR must be correct way-around here. THIS IS WHERE IT MATTERS.
            # Accounts Payable is Liability/CR
            lines = item['lines'] + [
                (ACCOUNTS_PAYABLE_ACCOUNT,
                 set_CR(item['value'])),
                (GST_EXPENSE_ACCOUNT,
                 set_DR(item['gst_total'])), ]

            transaction_kwargs = {
                'user': user,
                'date':  item['date'],
                'source': get_source(CreditorInvoice, "CreditorInvoice"),
                'value': item['value']
            }
            if item.get('note'):
                transaction_kwargs['note'] = item['note']

            invoice_kwargs = {
                'creditor': item['creditor'],
                'invoice_number': item['invoice_number'],
                'gst_total': item['gst_total'],
            }
            if item.get('order_number'):
                invoice_kwargs['order_number'] = item.get('order_number')
            if item.get('reference'):
                invoice_kwargs['reference'] = item.get('reference')

            # instantiate new objects
            new_transaction = Transaction(**transaction_kwargs)
            new_invoice = CreditorInvoice(**invoice_kwargs)

            # save new objects to DB
            new_transaction.save(lines=lines)
            new_invoice.transaction = new_transaction
            new_invoice.save()

            # add objects to tracer bullets
            new_transactions.append(new_transaction)
            new_invoices.append(new_invoice)

        results = (new_transactions, new_invoices)

    else:

        # formset data necessary headers
        data = {'form-TOTAL_FORMS': len(transactions),
                'form-INITIAL_FORMS': '0',
                'form-MIN_NUM_FORMS': '',
                'form-MAX_NUM_FORMS': '', }

        # convert dictionary to formset initial data
        for index, transaction in enumerate(transactions):
            form = "form-{}-".format(index)
            for k, v in transaction.items():
                data["{}{}".format(form, k)] = v

    return results
