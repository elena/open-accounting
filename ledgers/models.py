from django.db import models
from django.conf import settings

from . import querysets


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

## Classifying and organising.

## Set up once, refined and then rarely modifed afterwards.

## Referred to for the purpose of reporting and categorising Transaction Items

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Tag(models.Model):

    name = models.CharField(max_length=16)


class Account(models.Model):

    element = models.CharField(max_length=2, choices=ELEMENTS)

    parent = models.ForeignKey('self', null=True, blank=True, default=None,
                               related_name="parent+")

    number = models.CharField(max_length=4, blank=True, default=None)

    name = models.CharField(max_length=64)

    tags = models.ManyToManyField(Tag, blank=True, default=None,
                                  related_name="accounts")

    description = models.TextField(blank=True, default='')

    # Accounts which are "hard" referenced by code.
    special_account = models.CharField(max_length=8, choices=SPECIAL, blank=True,
                                       null=True, default=None)

    objects = querysets.AccountQuerySet.as_manager()

    class Meta:
        ordering = ['element', 'number', 'name']

    def get_code(self):
        return "{}-{}".format(self.element, self.number)

    def __str__(self):
        return "[{code}] {name}".format(
            code=self.get_code(),
            name=self.name)



# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# TRANSACTION objects

## The most important part.

## This must be clean and simple and always balance.

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Transaction(models.Model):
    """ The master object. The most basic form of Ledger Entry, with minimal requirements.

    Transactions are sacred and must always balance to zero.

    Sub-ledgers interact with `Accounts`/`Lines` all via this `Transaction` object.

    ## Checking Zero Balancing:

    Upon every `Line` save check to see if balances to zero, if not, `balances` = False.
    This property can be handled later.

    Setting as a BooleanField at save will add to DB size, but save transaction time later when
    trying to view every `Transaction` balances without also processing every `Line`.

    @@ TD is this efficient? Doesn't feel like it is, but it is simple.

    """

    # ---
    # Minimum required fields for object.

    date = models.DateField()

    reference = models.CharField(max_length=16)

    value = models.DecimalField(max_digits=19, decimal_places=2)

    # ---
    # Additional useful optional fields.

    note = models.CharField(max_length=2048, blank=True, default="")

    # ---
    # For our internal use/reference.

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="transactions")

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    # Basic check to ensure that all the lines associated with transaction
    # sum out to zero. This is fundamental.
    is_balanced = models.BooleanField(default=False)


class Line(models.Model):
    """
    Value is absolute value in General Ledger.

    Correct DR/CR value to be calculated in relevant view or subledger.
    """
    transaction = models.ForeignKey(Transaction, null=False, related_name="lines")

    account = models.ForeignKey(Account, null=False, related_name="lines")

    value = models.DecimalField(max_digits=19, decimal_places=2)

    note = models.CharField(max_length=2048, blank=True, default="")