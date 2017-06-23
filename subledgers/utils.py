# -*- coding: utf-8 -*-
import dateparser
import re

from subledgers import settings
from entities.models import Entity
from ledgers.models import Account, Transaction
from ledgers.utils import get_source, make_decimal, set_CR, set_DR

"""
# Purpose: convert dump in to series of subledger objects.

# 1. find where are the variations per subledger

 - Creditors/Debtors: terms


# 2. universal "dump" box view
  >> sends to appropriate subledger area

"""


def tsv_to_dict(dump):
    """ Make a sensible k,v dict from imported tsv.

    No validation is done here, just simple conversion."""
    try:
        rows = [items for items in dump.split("\r\n")]
        header_row = rows[0].split("\t")
        list_row_dicts = []
        for item in rows[1:]:
            row_dict = dict(list(zip(header_row, item.split("\t"))))
            list_row_dicts.append(row_dict)
        return list_row_dicts
    except:
        raise Exception("""Failed to convert dump to dict.

All that is required is a copy and paste from a spreadsheet.""")


def check_required(row_dict, object_name):
    object_settings = settings.OBJECT_SETTINGS[object_name]
    if not object_settings.get('uses_invoices'):
        # transactions
        required_fields = [x for x in settings.FIELDS_TRANSACTION_REQUIRED]
    else:
        # invoices
        required_fields = [x for x in settings.FIELDS_ALL_REQUIRED]

    for key, value in row_dict.items():

        # if necessary check contains some entity, remove from requirements
        if object_settings.get('uses_invoices'):
            if key in settings.FIELD_IS_RELATION:
                required_fields.remove('relation')

        if key in required_fields:
            required_fields.remove(key)

    # there shouldn't be any required fields left
    if required_fields:
        raise Exception("Missing fields: {}".format(
            ", ".join(required_fields)))
    else:
        return True


def get_relation(code, object_name):

    # Could be method on Entity, but like having Entity uncoupled.

    code = re.sub(r'\s', '', code)
    object_settings = settings.OBJECT_SETTINGS[object_name]

    # Creditor/Debtor class
    _Relation = object_settings.get('entity')

    try:
        # try to get existing Creditor/Debtor (here as _Relation)
        relation = _Relation.objects.get(entity__code=code)
    except:
        try:
            # entity exists but creditor does not.
            # get entity, create creditor.
            entity = Entity.objects.get(code=code)
            relation = _Relation.objects.create(entity=entity)
        except:
            # return just the string
            # @@ TOOD make this better
            raise Exception(
                "Object not found with code: {}".format(code))
    return relation


def dump_to_kwargs(dump, user, object_name=None):
    """ Main function for bringing together the elements of constructing
    the list of kwargs for transactions/invoices based upon whatever is
    required for the object.

    Defining Object type by "object_name":
     Either: batch of same Object Class (using *arg `object_name`)
         or: column header called `object_name` defining on a row-by-row basis.

     There is the choice of either preselecting what object_name of objects are
     being defined such as "CreditorInvoice" objects or "JournalEntry" objects.

     Alternatively each `row` should define a `object_name`.

    `user` will be added here as the individual creating this list is the one
    who should be tied to the objects.

    The processing here is:

    1. convert .tsv_to_dict(dump)

    2. check all required fields are represented (or explode)

    for each line/row:

        3. add `source` using ledgers.utils.get_source(`Model`)
                        based upon `Model` provided in object settings
           add `user` from positional arg
           add `object` from positional arg

        4. convert: IS_DATE using dateparser.parse
                    IS_MONEY using ledgers.utils.make_decimal()
                    IS_ENTITY using .get_relation(key, object_name)

        5. create and add `lines` list of tuples:
           5a. find fields that are accounts using Account.get_account(key)
           add (k, v) to `lines`

           5b.
           add `value` (correct CR/DR)
           add `gst_total` [optional, if specified in object settings]

           5c. add `lines` to `kwargs`

    6. append `row_dict` set to `list_kwargs`
    """

    # 1. convert
    object_settings = settings.OBJECT_SETTINGS[object_name]
    list_kwargs = []

    for row_dict in tsv_to_dict(dump):

        # copy kwargs to make valid set
        kwargs = {k.lower(): v for k, v in row_dict.items()}

        # flush lines list at the beginning of each loop
        lines = []

        # 2. check
        # powerful check, will explode if not quite precisely correct
        check_required(row_dict, object_name)

        # 3. add user and source
        kwargs['user'] = user
        kwargs['source'] = get_source(object_settings['source'])

        if object_name:
            kwargs['object_name'] = object_name

        for key in row_dict:

            # 4. typing
            if key in settings.FIELD_IS_DATE:
                kwargs[key] = dateparser.parse(row_dict[key])
            if key in settings.FIELD_IS_DECIMAL:
                kwargs[key] = make_decimal(row_dict[key])
            if key in settings.FIELD_IS_RELATION:
                kwargs['relation'] = get_relation(row_dict[key], object_name)

            if object_name is None:
                try:
                    kwargs['object_name'] = row_dict['object_name']
                except KeyError:
                    raise Exception(
                        "'object_name' column must be defined.")

            # 5. find account fields, add lines
            try:
                # 5a. find accounts, create line
                # `if` is unnecessary but included for clarity
                if Account.get_account(key):
                    lines.append((Account.get_account(key),
                                  make_decimal(row_dict[key])))
            except:
                pass

        # 5b. and value and (conditionally) gst_total
        if object_settings['tb_account']:

            # @@ TODO write tests for correct DR/CR

            # CR/Liability
            if object_settings.get('is_CR_in_tb'):
                lines.append((
                    object_settings['tb_account'],
                    set_CR(row_dict['value'])))

                # Include GST
                if object_settings['uses_invoices']:
                    lines.append((
                        settings.GST_DR_ACCOUNT,
                        set_DR(row_dict['gst_total'])))

            # DR/Asset
            if object_settings.get('is_DR_in_tb'):
                lines.append((
                    object_settings['tb_account'],
                    set_DR(row_dict['value'])))

                # Include GST
                if object_settings['uses_invoices']:
                    lines.append((
                        settings.GST_CR_ACCOUNT,
                        set_CR(row_dict['gst_total'])))

            # @@ TODO make a decision about adding Invoice due_date

        # 5c.
        kwargs['lines'] = lines

        # 6. append constructed kwargs to list

        list_kwargs.append(kwargs)

    return list_kwargs


def create_objects(list_kwargs, object_name=None, live=True):
    """ Input: (:obj:`list` of :obj:`dict`).

    Each :obj:`dict` represents the necessary **kwargs to create an object.

    Defining Object class:
        Either: batch of same Class Object (using function *arg `object_name`)
            or: kwarg key called `object_name` defined on a row-by-row basis.

    """

    # new_transactions = []
    # new_invoices = []
    new_objects = []

    for kwargs in list_kwargs:

        try:
            object_settings = settings.OBJECT_SETTINGS[kwargs['object_name']]
        except KeyError:
            # fall-back.
            object_settings = settings.OBJECT_SETTINGS[object_name]
        # print(kwargs)

        # winnowing only need fields

        transaction_kwargs = {k: kwargs.get(k)
                              for k in settings.FIELDS_TRANSACTION}

        if object_settings['uses_invoices']:
            object_kwargs = {k: kwargs.get(k)
                             for k in settings.FIELDS_INVOICE}
        else:
            object_kwargs = {}

        new_object = object_settings['source'](
            **object_kwargs)

        if live:
            new_transaction = Transaction(**transaction_kwargs)
            new_transaction.save(lines=kwargs['lines'])
            new_object.transaction = new_transaction
            new_object.save()
            new_objects.append(new_object)

        # # add objects to tracer bullets
        # new_transactions.append(new_transaction)
        # new_invoices.append(new_invoice)
        # new_transactions.append(transaction_kwargs)
        # new_invoices.append(invoice_kwargs)

    results = new_objects

    return results
