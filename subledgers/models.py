# -*- coding: utf-8 -*-
import dateparser
import re

from django.db import models
from django.utils.module_loading import import_string
from decimal import Decimal

from subledgers import settings
from ledgers import utils
from entities.models import Entity
from ledgers.models import Account, Transaction


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Abstract Classes for Subledgers
#
# See detailed discussion:
# http://admin-accounting.blogspot.com.au/2017/06/subledger-generalisation-and-specifics.html

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Entry(models.Model):

    # *** ABSTRACT CLASS ***

    """ Generalised in case more fields are necessary for subjedgers.

    For use with at least: Sales, Expenses
    """

    transaction = models.OneToOneField('ledgers.Transaction')

    additional = models.CharField(
        max_length=128, blank=True, default="", null=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.relation:
            return "{} [{}]-- ${} ".format(self.relation.entity.code,
                                           self.transaction.date,
                                           self.transaction.value)
        else:
            return "{} -- ${} -- {}".format(self.transaction.date,
                                            self.transaction.value,
                                            self.transaction.note)

    def get_required(object_name):
        required = set([x for x in settings.FIELDS_TRANSACTION_REQUIRED]
                       + [x for x in settings.OBJECT_SETTINGS[object_name]
                          ['required_fields']])
        return required

    def check_required(kwargs):
        required_fields = Entry.get_required(kwargs['object_name'])
        for key, value in kwargs.items():
            if key in settings.FIELD_IS_RELATION:
                try:
                    required_fields.remove('relation')
                except KeyError:
                    pass
            if key in required_fields:
                required_fields.remove(key)
        # there shouldn't be any required fields left
        if required_fields:
            raise Exception("Missing fields: {}".format(
                ", ".join(required_fields)))
        else:
            return True

    def get_cls(name):
        """ Input variations (convert to source_str):
        # 1. ModelObject
        # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
        # 3. source_str
        """

        # 1. ModelObject
        try:
            source = utils.get_source(name)
        except AttributeError:
            pass

        # 2. object_name -- valid vanilla name, eg "CreditorInvoice"
        try:
            source = settings.OBJECT_SETTINGS[name]['source']
        except KeyError:
            pass

        # 3. source_str
        if source in settings.VALID_SOURCES:
            cls = import_string(source)
            return cls
        else:
            raise Exception("No valid `type` found for {}.".format(name))

    def dump_to_kwargs(dump, user, object_name=None, self=None):
        """ Main function for bringing together the elements of constructing
        the list of kwargs for transactions/invoices based upon whatever is
        required for the object.

        Defining Object type by "object_name":
         Either: batch of same Object Class (using *arg `object_name`)
                 or: by calling method from Object Class (eg. CreditorInvoice)
             or: column header `object_name` defining on a row-by-row basis.

         There is the choice of either preselecting what object_name of
         objects are being defined such as "CreditorInvoice" objects or
        "JournalEntry" objects.

         Alternatively each `row` should define a `object_name`.

        `user` will be added here as the individual creating this list is
        the one who should be tied to the objects.

        The processing here is:

        1. convert .tsv_to_dict(dump)

        for each line/row:

            2. add `source` using ledgers.utils.get_source(`Model`)
                            based upon `Model` provided in object settings
               add `user` from positional arg
               add `object` from positional arg

            3. convert: IS_DATE using dateparser.parse
                        IS_MONEY using ledgers.utils.make_decimal()
                        IS_ENTITY using .get_relation(key, object_name)

            4. create and add `lines` list of tuples:
               4a. find fields that are accounts using Account.get_account(key)
               add (k, v) to `lines`

               4b.
               add `value` (correct CR/DR)
               add `gst_total` [optional, if specified in object settings]

               4c. add `lines` to `kwargs`

        5. check all required fields are represented (or explode)
           append `row_dict` set to `list_kwargs`
        """

        # 1. convert
        object_settings = settings.OBJECT_SETTINGS[object_name]
        list_kwargs = []

        for row_dict in utils.tsv_to_dict(dump):

            # copy kwargs to make valid set
            kwargs = {k.lower(): v for k, v in row_dict.items()}

            # flush lines list at the beginning of each loop
            lines = []

            # 2. add user and source
            kwargs['user'] = user
            kwargs['source'] = utils.get_source(object_settings['source'])

            if row_dict.get('type'):
                cls = Entry.get_cls(row_dict['type'])
            elif object_name:
                cls = Entry.get_cls(object_name)
            elif self:
                cls = Entry.get_cls(self)
            else:
                raise Exception("No `type` column used.")

            kwargs['cls'] = cls
            kwargs['object_name'] = object_name = cls.__name__

            for key in row_dict:

                # 3. typing
                if key in settings.FIELD_IS_DATE:
                    kwargs[key] = dateparser.parse(row_dict[key])
                if key in settings.FIELD_IS_DECIMAL:
                    kwargs[key] = utils.make_decimal(row_dict[key])
                if key in settings.FIELD_IS_RELATION:
                    kwargs['relation'] = Relation.get_relation(
                        row_dict[key], object_name)

                if object_name is None:
                    try:
                        kwargs['object_name'] = row_dict['object_name']
                    except KeyError:
                        raise Exception(
                            "'object_name' column must be defined.")

                # 4. find account fields, add lines
                try:
                    # 4a. find accounts, create line
                    # `if` is unnecessary but included for clarity
                    if Account.get_account(key):
                        lines.append((Account.get_account(key),
                                      utils.make_decimal(row_dict[key])))
                except:
                    pass

            # 4b. and value and (conditionally) gst_total
            if object_settings['tb_account']:

                # @@ TODO write tests for correct DR/CR

                # CR/Liability
                if object_settings.get('is_CR_in_tb'):
                    lines.append((
                        object_settings['tb_account'],
                        utils.set_CR(row_dict['value'])))

                    # Include GST
                    if object_settings['abstract'] is 'INVOICE':
                        lines.append((
                            settings.GST_DR_ACCOUNT,
                            utils.set_DR(row_dict['gst_total'])))

                # DR/Asset
                if object_settings.get('is_DR_in_tb'):
                    lines.append((
                        object_settings['tb_account'],
                        utils.set_DR(row_dict['value'])))

                    # Include GST
                    if object_settings['abstract'] is 'INVOICE':
                        lines.append((
                            settings.GST_CR_ACCOUNT,
                            utils.set_CR(row_dict['gst_total'])))

                # @@ TODO make a decision about adding Invoice due_date

            # 4c.
            kwargs['lines'] = lines

            # 5. append constructed kwargs to list

            # 6. check and add
            # powerful check, will explode if not quite precisely correct
            Entity.check_required(kwargs)

            list_kwargs.append(kwargs)

        # Returns list of big dictionaries containing everything dumped in.
        # This big dictionary needs to be
        return list_kwargs

    def make_transaction_dict_pair(kwargs):
        transaction_kwargs = {k: kwargs.get(k)
                              for k in settings.FIELDS_TRANSACTION}

        object_settings = settings.OBJECT_SETTINGS[kwargs['object_name']]
        object_kwargs = {k: kwargs.get(k)
                         for k in object_settings['fields']}
        return (transaction_kwargs, object_kwargs)

    def create_objects(list_kwargs, live=True):
        """ Input: :obj:`list` of :obj:`dict`.

        Each :obj:`dict` represents the necessary **kwargs to create an object.

        Can be generated from a spreadsheet dump using `self.dump_to_kwargs`
        providing all the necessary fields are represented.

        # Inception Rules:
          if: called via abstract class `Entry` can be mixed
              `type` column must be specified.

          if: this used via concrete class:
             if `type` column, this will be used to create object
             otherwise: concrete class will be assumed for all objects.

        Defining Object class:
            Either: batch of same Class Object (using *arg `object_name`)
                or: kwarg key `object_name` defined on a row-by-row basis.

        """

        # new_transactions = []
        # new_invoices = []
        new_objects = []

        for kwargs in list_kwargs:

            transaction_kwargs, object_kwargs = make_transaction_dict_pair(  # noqa
                kwargs)

            object_settings = settings.OBJECT_SETTINGS[
                object_kwargs['object_name']]
            new_object = object_settings['source'](**object_kwargs)

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


class Invoice(Entry):

    # *** ABSTRACT CLASS ***

    """ For use with at least: Creditors Invoices, Debtors Invoices

    7 legal components of an invoice: the words "invoice", date, seller,
    seller abn, what, tax (and what applied to), total value, (due date)

    Transaction contains:
    from *abstract* `Entry`
      transaction = models.OneToOneField('ledgers.Transaction')
      - *Date
      - *Value
      - Note
      - *User
      - source
    """

    due_date = models.DateField(null=True)

    invoice_number = models.CharField(max_length=128)

    order_number = models.CharField(
        max_length=128, blank=True, default="", null=True)

    reference = models.CharField(
        max_length=128, blank=True, default="", null=True)

    gst_total = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        abstract = True


class Payment(Entry):

    # *** ABSTRACT CLASS ***

    """ Relation is compulsory, but probably best defined at concrete class.
    """

    bank_transaction = models.ForeignKey(
        'bank_reconciliations.BankTransaction')

    class Meta:
        abstract = True


class Relation(models.Model):

    # *** ABSTRACT CLASS ***

    """ All that `Relation` does is provide `get_relation` model method.
    """

    class Meta:
        abstract = True

    def clean_code(s):
        return re.sub(r'\s', '', s)

    def get_or_create_relation(code, _Relation):
        """ `Entity` exists. `Creditor`/`Debtor` associated object) may not.

        We'll always want to just create related if `Entity` already exists.
        """
        try:
            # try to get existing Creditor/Debtor (here as _Relation)
            return _Relation.objects.get(entity__code=code)
        except:
            try:
                # entity exists but creditor does not.
                # get entity, create creditor.
                entity = Entity.objects.get(code=code)
                return _Relation.objects.create(entity=entity)
            except Entity.DoesNotExist:
                raise Exception(
                    "Entity not found with code: {}".format(code))

    def get_or_create_relation_and_entity(self, code, name):
        """ Creates both `Creditor` or `Debtor` and `Entity`.

        name is required. Not sure when going to use this method.
        """

        _Relation = self._meta.model
        try:
            # try to get existing Creditor/Debtor (here as _Relation)
            return _Relation.objects.get(entity__code=code)
        except:
            try:
                # entity exists but creditor does not.
                # get entity, create creditor.
                entity = Entity.objects.get(code=code)
                return _Relation.objects.create(entity=entity)
            except:
                if not name:
                    raise Exception(
                        "Does not exist. Name must be specified to create {}".format(code))  # noqa
                else:
                    entity = Entity.objects.create(code=code, name=name)
                    return _Relation.objects.create(entity=entity)

    def get_relation(self, code, object_name=None):
        """ get the correct related Entity for *this* whatever,
        eg `Creditor`/`Debtor`.

        Alternatively can specify using `object_name`

        Must be object instance eg. Creditor().get_relation("ACME")
        """
        if object_name:
            return Relation.get_specific_relation(code, object_name)
        else:
            _Relation = self._meta.model
            return _Relation.get_or_create_relation(
                Relation.clean_code(code), _Relation)

    def get_specific_relation(code, object_name):
        """ Specify the 'object_name' of the this you want the Relation of
        eg. object_name = 'CreditorInvoice', object_name = 'CreditorPayment'.

        Doesn't need to be instance.
        """
        object_settings = settings.OBJECT_SETTINGS[object_name]
        _Relation = import_string(object_settings.get('entity_class'))
        return Relation.get_or_create_relation(
            Relation.clean_code(code), _Relation)
