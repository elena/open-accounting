# -*- coding: utf-8 -*-
from django.db import models
from django.utils.module_loading import import_string
from decimal import Decimal
from importlib import import_module

from entities.models import Entity
from ledgers import utils
from ledgers.models import Account, Transaction
from subledgers import settings


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

    transaction = models.OneToOneField(
        'ledgers.Transaction', models.CASCADE, blank=True, default="",
        null=True)

    additional = models.CharField(
        max_length=128, blank=True, default="", null=True)

    class Meta:
        abstract = True
        ordering = ['transaction__date']

    def __str__(self):
        if self.transaction.note:
            return "{} -- ${} -- {}".format(self.transaction.date,
                                            self.transaction.value,
                                            self.transaction.note)
        else:
            return "{} -- ${}".format(self.transaction.date,
                                      self.transaction.value)

    # Entry specific utilities:

    def save_transaction(self, kwargs, live=True):
        """ Creates self instance with necessary `Transaction` and `Lines`
        based upon kwargs provided.

        @@TODO still should be pre-save signal, though this is simple.

        `account` and `accounts` DON'T include tb account.
        This is inferred from cls/self and OBJECT_SETTINGS.

        `lines` are complete and should balance to zero.

        Minimum required fields:
        {
          'user':
          'date':
          'account':
          'value':
        or
          'accounts'
        }

        Note: if `JournalEntry` must define:
        {
          'account_DR':
          'account_CR':
          'value':
        or
          'lines'
        }

        where:
            accounts = [
              (account, val),
              (account, val),
              (account, val)]
              **tb account not included, added later**
            lines = [
              (account_DR, val),
              (account_DR, val),
              (account_DR, val, notes),
              (account_CR, val, notes),
              (account_CR, val)]

        Note: see `Transaction` documentation regarding correct use of `lines`
        or simplified case of providing (`ac_DR`, `ac_CR`, `value`).

        Example usage of `.save_transaction`:

        # simple
        new_journalentry = JournalEntry()
        new_journalentry.save_transaction(kwargs)

        # with entity:
        kwargs['invoice_number'] = 'abc123'
        kwargs['relation'] = Creditor.objects.get(code="GUI")
        new_creditorinvoice = CreditorInvoice()
        new_creditorinvoice.save_transaction(kwargs)
        """
        lines, trans_kwargs, obj_kwargs = self.make_dicts(kwargs)

        if 'relation' in obj_kwargs:
            relation = obj_kwargs.pop('relation')

        # Note: self(**obj_kwargs) does not work in this case.
        for key in obj_kwargs:
            setattr(self, key, kwargs[key])

        # @@ TODO not sure why relation has to be removed and then re-added
        # but it works now after bit of agony and confusion. Explore this.
        if 'relation' in locals():
            self.relation = relation

        self_transaction = Transaction(**trans_kwargs)

        try:
            if live:
                self_transaction.save(lines=lines)
                self.transaction = self_transaction
                self.save(force_insert=True)
                return self
            else:
                print("Pass!: {}: {}".format(self, obj_kwargs))
                return kwargs
        except Exception as e:
            print("Error {}. Keys provided: {}".format(e, ", ".join(
                obj_kwargs)))
            try:
                # Delete transaction if created so not to pollute.
                # @@ TODO save signals
                self_transaction.delete()
            except NameError:
                pass

            return "Error {}: {}".format(e, ", ".join(kwargs))

    def get_object_settings(self):
        return settings.OBJECT_SETTINGS[utils.get_source_name(self)]

    def get_relation(self, data):

        RelationCls = import_string(
            self.get_object_settings()['relation_class'])

        if isinstance(data, RelationCls):
            return data
        elif RelationCls is Entity:
            try:
                return Entity.objects.get(code=data)
            except Entity.DoesNotExist:
                return None
        else:
            return RelationCls.objects.get(entity__code=data)

        raise Exception("{} with code {} doesn't exist.".format(
            type(RelationCls), data))

    def get_tb_account(self):
        object_settings = self.get_object_settings()
        if object_settings.get('tb_account'):
            try:
                return Account.get_account(object_settings.get('tb_account'))
            except Exception:
                raise Exception("No trial balance account for {}".format(self))
        else:
            return False

    def is_cr_or_dr_in_tb(self):
        object_settings = self.get_object_settings()
        if object_settings.get('is_tb_account_DR'):
            return "DR"
        if object_settings.get('is_tb_account_CR'):
            return "CR"
        return None

    # ---
    # ** Make Dicts **

    def make_dicts(self, input_kwargs):
        # Convert kwargs to dictionaries to create objects.

        kwargs = self.process_kwargs(input_kwargs)
        trans_kwargs, obj_kwargs = {}, {}

        # cherry-pick transaction kwargs from dir
        for attr in dir(Transaction):
            if kwargs.get(attr) and not attr == 'lines':
                trans_kwargs[attr] = kwargs.get(attr)

        # cherry-pick obj kwargs from dir
        for attr in dir(type(self)):
            if kwargs.get(attr):
                obj_kwargs[attr] = kwargs.get(attr)

        # @@TODO Should make_lines go here or in self.process_kwargs?
        lines = self.make_lines(kwargs)

        return (lines, trans_kwargs, obj_kwargs)

    # ---
    # Make Dicts processing methods:

    def get_required(self):
        required = set([
            x for x in settings.FIELDS_TRANSACTION_REQUIRED]
            + [x for x in self.get_object_settings()['required_fields']])
        return required

    def check_required(self, kwargs):
        # Basically check all required fields exist in kwargs.
        required_fields = self.get_required()

        for key, value in kwargs.items():
            if key in settings.FIELD_IS_RELATION:
                try:
                    required_fields.remove('relation')
                except KeyError:
                    pass
            if key in required_fields:
                required_fields.remove(key)
                if kwargs[key] is None:
                    raise Exception("{} ** Missing value: {}".format(
                        kwargs, key))

        # there shouldn't be any required fields left
        if required_fields:
            raise Exception(
                "Missing field/s: {}".format(", ".join(required_fields)))
        else:
            return True

    def process_kwargs(self, kwargs):
        """
        Minimum keys assumed included: 'user', 'date', 'lines'

        1. Keys added (if not already defined): 'cls', 'source'
             add `source` using ledgers.utils.get_source(`Model`)
             based upon `Model` provided in object settings

        2. Keys checked: 'relation', dates, decimals, required fields
             IS_DATE using dateparser.parse
             IS_DECIMAL using ledgers.utils.make_decimal()
             IS_RELATION to normalise relation field name

        3. Create dicts: (obj_kwargs, trans_kwargs)

        Check all required fields are represented (or explode)
             append `row_dict` set to `list_kwargs`
        """

        # Generate list of codes to check against.
        # Cheaper than checking db for every account.
        ACCOUNT_CODE_LIST = Account.get_account_code_list()

        process_kwargs = {k.lower(): v for k, v in kwargs.items()}

        # If `cls` not manually described in kwargs.
        process_kwargs['source'] = utils.get_source(self)

        for key in kwargs:
            if key in settings.FIELD_IS_DATE:
                process_kwargs[key] = utils.make_date(kwargs[key])

            if key in settings.FIELD_IS_DECIMAL:
                process_kwargs[key] = utils.make_decimal(kwargs[key])

            if key in settings.FIELD_IS_RELATION:
                # Relation names are not always consistently used.
                # eg. Creditor, Relation
                if kwargs[key] is None:
                    # Is likely to have emtpy relation column heading.
                    # Remove empty relation, so doesn't blow up save.
                    process_kwargs.pop(key)
                else:
                    process_kwargs['relation'] = self.get_relation(kwargs[key])

            if key in ACCOUNT_CODE_LIST:
                process_kwargs.setdefault(
                    'accounts', []).append((key, kwargs[key]))

        self.check_required(process_kwargs)

        return process_kwargs

    # ---
    # ** Make Lines **

    def make_lines(self, kwargs):
        """
        Create and add `lines` list of tuples:
        1. normalise `account`, `accounts` and `account_CR`/`account_DR`
           to `lines`.

        2. add `gst_total` [optional, if specified in object settings]


        3. correct CR/DR using .set_lines_sign()
           (this is a big deal)

        4. add `lines` back to `kwargs`
        """
        lines = ()
        if kwargs.get('lines'):

            # Lines are completely manual.
            # Should never be used by 'standard' subledgers:
            # Debtor/Creditor, Sales/Expense

            # Prioritise `lines` if defined in kwargs
            self.check_lines_equals_value(kwargs)
            lines = kwargs['lines']
        elif kwargs.get('account_dr') \
                and kwargs.get('account_cr') \
                and kwargs.get('value'):
            # Next try `account_DR`, `account_CR`, `value` combination
            # should be lowercase
            lines = self.process_line(
                kwargs.get('account_dr'),
                kwargs.get('account_cr'),
                kwargs.get('value'))
            # Next check for `inlines_accounts`
        elif kwargs.get('accounts') or kwargs.get('account'):

            # Accounts should *always* be used by 'standard' subledgers:
            # Debtor/Creditor, Sales/Expense
            # @@ TODO formalise 'standard' subledgers use of `accounts`
            # rather than `lines`

            # Next try normalising `account`/`accounts`
            if kwargs.get('accounts'):
                accounts = self.process_accounts(
                    kwargs.get('accounts'))
            elif kwargs.get('account'):
                accounts = self.process_account(
                    kwargs.get('account'),
                    kwargs.get('value'))

            # Check tax on 'standard' subledgers only.
            # Should be done before tb account is added.

            # In this early case, all thise means is checking that if GST
            # is required, that it has been added.

            # @@ TODO: Doesn't check IF tax should be included.
            # Should explode as necessary.
            accounts = self.process_lines_tax(kwargs, accounts)

            # Convert `accounts` to `lines` (ie `accounts` + tb account)
            if self.get_tb_account():
                accounts.append((
                    self.get_tb_account(),
                    utils.set_CR(self.get_lines_balance(accounts))))

            lines = accounts
        else:
            # fails here if a condition for providing lines is not met.
            raise Exception(
                "Lines/Accounts were not found in input: {}.".format(
                    kwargs))

        # Should now have a set of normalised lines.

        # @@ TOOD: check tb account not added incorrectly
        # @@ TOOD: protected reserved tb accounts?
        # @@ TODO: allow multiple methods to be used?

        # Trial Balance DR/CR Correction
        # This is confusing. Needs to be thoroughly checked.
        # At this point `lines` are correct for subledger.
        # Eg. - Increase in sales is positive.
        #     - Additional expense is positive.
        # Now fix `lines` to ensure correct +/- (dr/cr) for tb.
        lines = self.set_lines_sign(lines)

        # check lines are OK.
        if self.get_lines_balance(lines):
            raise Exception(
                "Lines do not balance to zero. Input: {}.".format(kwargs))

        return lines

    # ---
    # Lines processing methods:

    def process_account(self, account, val):
        """ If only account is provided, retrieve tb account. """
        return [(Account.get_account(account),
                 utils.set_DR(utils.make_decimal(val)))]

    def process_accounts(self, accounts):
        lines = []
        for account, val in accounts:
            # Note use of [0], .process_account return list
            lines.append(self.process_account(account, val)[0])
        return lines

    def process_line(self, account_DR, account_CR, val):
        return [(Account.get_account(account_DR),
                 utils.set_DR(utils.make_decimal(val))),
                (Account.get_account(account_CR),
                 utils.set_CR(utils.make_decimal(val)))]

    def process_lines_tax(self, kwargs, lines, local=None):
        # Process tax BEFORE set_lines_sign
        # @@ TODO: set country better, should be a setting somewhere probably

        if not local:
            local = 'AU'
        taxes_utils = import_module('subledgers.taxes.{}.utils'.format(local))
        lines = taxes_utils.process_tax(self, kwargs, lines)
        return lines

    def get_lines_balance(self, lines):
        balance = 0
        for i, line in enumerate(lines):
            balance += line[1]
        return balance

    def set_lines_sign(self, lines):

        # Invert signs if DR in tb
        # (as if DR in tb, is invert of native display
        #  eg. Sale $5 >> positive in subledger BUT sb positive in TB.
        #  default is offset $5, just need to be reversed for lines/gl/tb.)

        if self.is_cr_or_dr_in_tb() == 'DR':
            inverted_lines = []
            for line in lines:
                inverted_line = (line[0], -line[1])
                if len(line) == 3:  # if there is a `note`
                    inverted_line = inverted_line + line[2]
                inverted_lines.append(inverted_line)
            lines = inverted_lines
        return lines

    def check_lines_equals_value(self, kwargs):
        balance = self.get_lines_balance(kwargs['lines'])
        if kwargs.get('value') and\
           not Decimal(kwargs.get('value')) == abs(Decimal(balance)):
            raise Exception('Value provide ({}) does not equal remaining balance: {}'.format(kwargs['value'], balance))  # noqa
        return True


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

    unpaid = models.DecimalField(
        max_digits=19, decimal_places=2, default=Decimal('0.00'))

    # Provide something to sanity check DR/CR
    is_credit = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        try:
            return "{} [{}]-- ${} ".format(self.relation.entity.code,
                                           self.transaction.date,
                                           self.transaction.value)
        except (AttributeError, ValueError):
            if self.transaction.note:
                return "{} -- ${} -- {}".format(self.transaction.date,
                                                self.transaction.value,
                                                self.transaction.note)
            else:
                return "{} -- ${}".format(self.transaction.date,
                                          self.transaction.value)

    def is_cr_or_dr_in_tb(self):
        # override `Entry.is_cr_or_dr_in_tb` based upon self.is_credit
        # If is credit, do the CR/DR opposite:
        if self.is_credit:
            object_settings = self.get_object_settings()
            if object_settings.get('is_tb_account_DR'):
                return "CR"  # reverse credit
            if object_settings.get('is_tb_account_CR'):
                return "DR"  # reverse credit
        else:
            return super(Invoice, self).is_cr_or_dr_in_tb()


class Payment(models.Model):

    # *** ABSTRACT CLASS ***
    # *** NOT a Transaction  ***

    """ Not related to `ledgers` at all.

    Useful for queryset and reconciliation purposes.

    Relation is compulsory, but probably best defined at concrete class to
    be specific about subledger Relation, eg Creditor or Debtor.
    """

    bank_entry = models.OneToOneField(
        'bank_reconciliations.BankEntry',
        models.CASCADE, default='', blank=True, null=True)

    # ---
    # Minimum required fields for object.

    # will get date from BankEntry. Will never vary from bank statement.
    # date = models.DateField()

    # will get value from BankEntry.Transaction. Risky to duplicate.
    # before there is a BankEntry, can just user invoices total.
    # value = models.DecimalField(max_digits=19, decimal_places=2)

    # ---
    # Additional useful optional fields.

    note = models.CharField(max_length=2048, blank=True, default="", null=True)

    reference = models.CharField(
        max_length=128, blank=True, default="", null=True)

    # ---
    # For our internal use/reference.

    # could be useful to know who matched/created the payment object
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Relation(models.Model):

    # *** ABSTRACT CLASS ***

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
