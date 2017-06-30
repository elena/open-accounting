# -*- coding: utf-8 -*-
import re
import decimal
from django.db import models
from django.db.models import Sum
from django.conf import settings

from ledgers import querysets


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Settings

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


VALUE = (
    ('DR', 'Debit'),
    ('CR', 'Credit'),
)


REPORT = (
    ('Balance Sheet', 'Balance Sheet'),
    ('Profit and Loss', 'Profit and Loss'),
)


ELEMENTS = (
    ('01', 'Asset'),
    ('03', 'Liability'),
    ('05', "Owner's Equity"),
    ('10', 'Revenue'),
    ('15', 'Expenses'),
)

SPECIAL = [
    ('ACP', 'Accounts Payable Liability Account'),
    ('ACR', 'Accounts Receivable Asset Account'),
    ('bank', 'Bank Account'),
    ('owner', 'Owner Equity'),
    ('suspense', 'Holding/Suspense'),
]


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# CHART of ACCOUNTS (CofA)

# Classifying and organising.

# Set up once, refined and then rarely modifed afterwards.

# Referred to for the purpose of reporting and categorising Transaction Items

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Tag(models.Model):

    name = models.CharField(max_length=16)


class Account(models.Model):

    element = models.CharField(max_length=2, choices=ELEMENTS)

    parent = models.ForeignKey('self', null=True, blank=True, default=None,
                               related_name="parent+")

    number = models.CharField(max_length=4, blank=True, default=None)

    name = models.CharField(max_length=64)

    tags = models.ManyToManyField('ledgers.Tag', blank=True, default=None,
                                  related_name="accounts")

    description = models.TextField(blank=True, default='')

    # Accounts which are "hard" referenced by code.
    special_account = models.CharField(max_length=8, choices=SPECIAL,
                                       blank=True, null=True, default=None)

    objects = querysets.AccountQuerySet.as_manager()

    class Meta:
        ordering = ['element', 'number', 'name']

    def __str__(self):
        return "[{code}] {name}".format(
            code=self.get_code(),
            name=self.name)

    def get_code(self):
        """ beware: This format is parsed back by queryset.AccountQuerySet """
        return "{element}-{number:0>4}".format(element=self.element,
                                               number=self.number)

    def get_account(data):
        """ Allow fetch `Account` by either string of "code" or Account obj"""

        # is `Account` object
        if type(data) == Account:
            return data

        # is string, search for `Account` object
        data = re.sub(r'[^\d\-.]', '', data)
        account = Account.objects.by_code(data)
        if account:
            return account
        # @@TODO Could potentially raise a TypeError here
        return False


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# TRANSACTION objects

# The most important part. Integrity of transactions/lines is paramount.
# Can NOT be DIRECTLY ADDED/MODIFIED.
# Can NOT be DELETED at all.

# Accounting systems are one of the rare systems that only ever move forward.
# Deactivation doesn't make sense and once in the ledger a transaction is
# never ever deleted. It can be adjusted or reversed by another transaction,
# but once it exists, it exists forever.

# Transactions/Lines are not directly modifiable, they can only be CRUD by
# subledgers.

# These must be clean and simple and always balance.

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Transaction(models.Model):
    """ The master object. The most basic form of Ledger Entry, with minimal
    requirements.

    Integrity of transactions/lines is paramount.
    Can NOT be DIRECTLY ADDED/MODIFIED.
    Can NOT be DELETED at all.

    The master object. The most basic form of Ledger Entry, with minimal
    requirements.

    Transactions are sacred and must always balance to zero.

    Sub-ledgers interact with `Accounts`/`Lines` all via this `Transaction`
    object.

    # Checking Zero Balancing:

    Upon every `Line` save check to see if balances to zero, if not,
    `balances` = False. This property can be handled later.

    Setting as a BooleanField at save will add to DB size, but save transaction
    time later when  trying to view every `Transaction` balances without also
    processing every `Line`.
    """

    # ---
    # Minimum required fields for object.

    date = models.DateField()

    value = models.DecimalField(max_digits=19, decimal_places=2)

    # ---
    # Additional useful optional fields.

    note = models.CharField(max_length=2048, blank=True, default="", null=True)

    # reference = models.CharField(max_length=16)

    # @@TODO could be generic relation
    source = models.CharField(max_length=1024, blank=True, default="")

    # ---
    # For our internal use/reference.

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="transactions")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Basic check to ensure that all the lines associated with transaction
    # sum out to zero. This is fundamental.
    is_balanced = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "[{}] ${:.2f} {}".format(self.pk, self.value, self.source.split(".")[-1])

    # Overwrite built-in Model methods

    def save(self, lines=None, *args, **kwargs):

        if not self.pk and lines is None:
            """ New object check: Basic 'is adequate' to create check. """
            raise Exception("""Lines are necessary to save new Transaction. Input should be:

lines = (DR_account, CR_account, value)) # must be DR first immutable tuple
    or
lines = [(account, 1),
         (account, 1, "Optional Note"),
         (account, -2)] # must balance

new_transaction.save(lines)
""")

        if not self.pk:
            """ New objects: 'lines' input only works for NEW Transactions
            @@TODO: use `lines` for updates?
            """
            # this is just passively preparing value and line kwargs
            self.value, valid_lines = Transaction.line_validation(lines)

            # if passed line_validation then it is balanced
            self.is_balanced = True

            # must save `Transaction` before able to save lines
            # this should validate self before lines are added
            # the timing of this matters
            super(Transaction, self).save(*args, **kwargs)

            # create the lines
            for line_kwargs in valid_lines:
                new_line = Line(transaction=self, **line_kwargs)
                new_line.save()
        else:
            """ Existing objects: check and save """
            # Always check balances.
            if not self.is_balanced == self.check_is_balanced():
                self.is_balanced = self.check_is_balanced()
            super(Transaction, self).save(*args, **kwargs)

    # Custom methods

    def check_is_balanced(self):
        """ Challenge with this method is knowing when all the lines have been
        updated.
        """
        if self.lines.count() >= 2 \
           and self.lines.aggregate(Sum('value'))['value__sum'] == decimal.Decimal(0):
            return True
        return False
        # raise Exception('Transaction does not balance.')

    def line_validation(data):
        """ Returns a tuple as follows: (value, {**kwarg}, {**kwarg} {**kwarg})
        where `kwargs` are everything that's required to generate lines.
        """
        ERR_MSG = """
Input was:
{}

Input should be:
(DR_account, CR_account, value) # must be DR first immutable tuple
    or
[(account, 1),
 (account, 1, "Optional Note"),
 (account, -2),
 ...
]""".format(data)

        # case multiple:
        # basically matter of converting list/tuple to list kwargs
        if (type(data) == list or type(data) == tuple) and len(data) >= 2 \
           and type(data[0]) == tuple:
            bal, lines = 0, [0, []]
            for line in data:
                kwargs = {}
                if len(line) >= 2:
                    kwargs['account'] = Account.get_account(line[0])
                    kwargs['value'] = value = decimal.Decimal(line[1])
                    if len(line) > 2:
                        kwargs['note'] = line[2]
                    bal += value
                if value > 0:
                    lines[0] += value
                lines[1].append(kwargs)
            if bal:
                raise Exception(
                    "Lines do not balance. Total is {}".format(bal))
            else:
                return lines

        # case simple/single:
        if type(data) == tuple and len(data) == 3:
            """ BEWARE!! Transactions may be posted upside-down. CHECK USAGE.
            Note: only multi-line transactions/lines can allow Line notes.
            Necessary compromise for simplicity 3-obj adding allows.
            """
            try:
                dr_account = Account.get_account(data[0])
                cr_account = Account.get_account(data[1])
                value = decimal.Decimal(data[2])
                if dr_account and cr_account and value \
                   and not dr_account == cr_account:
                    return (value,
                            [{'account': dr_account, 'value': value},
                             {'account': cr_account, 'value': -value}])
            except (decimal.InvalidOperation, AttributeError):
                raise Exception(ERR_MSG)

        raise Exception(ERR_MSG)


class Line(models.Model):
    """
    Value is absolute value in General Ledger.

    Correct DR/CR value to be calculated in relevant view or subledger.
    """
    transaction = models.ForeignKey(
        Transaction, null=False, related_name="lines")

    account = models.ForeignKey(Account, null=False, related_name="lines")

    value = models.DecimalField(max_digits=19, decimal_places=2)

    note = models.CharField(max_length=2048, blank=True, default="")

    objects = querysets.LineQuerySet.as_manager()

    def __str__(self):
        name = "[{acc}] {date} ${val}".format(
            acc=self.account.get_code(), val=self.value,
            date=self.transaction.date)
        if self.transaction.source:
            name = "{} -- {}".format(name,
                                     self.transaction.source.split(".")[-1])
        return name

    def save(self, *args, **kwargs):
        obj = super(Line, self).save(*args, **kwargs)
        # re-save for `Transaction.is_balanced`
        self.transaction.save()
