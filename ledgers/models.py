from django.db import models
from django.conf import settings


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

    parent = models.ForeignKey('self', null=True, blank=True, default=None, related_name="parent+")

    number = models.CharField(max_length=4, blank=True, default=None)

    name = models.CharField(max_length=64)

    tags = models.ManyToManyField(Tag, blank=True, default=None, related_name="account")

    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['element', 'number', 'name']

    def __str__(self):
        return self.name

    @property
    def account(self):
        return "{element}-{number:04}".format(self.element, self.number)


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

    # TRANSACTION objects

    ## The most important part.

    ## This must be clean and simple and always balance.

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Transaction(models.Model):
    """ The master object. The most basic form of Ledger Entry, with minimal requirements.

    Transactions are sacred and must always balance to zero.

    Sub-ledgers interact with `Accounts`/`Lines` all via this `Transaction` object.

    """

    date = models.DateField()

    reference = models.CharField(max_length=16)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name="transaction")

    value = models.DecimalField(max_digits=19, decimal_places=2)

    note = models.CharField(max_length=2048)


class Line(models.Model):
    """
    Value is absolute value in General Ledger.

    Correct DR/CR value to be calculated in relevant view or subledger.
    """
    transaction = models.ForeignKey(Transaction, null=False, related_name="line")

    account = models.ForeignKey(Account, null=False, related_name="line")

    value = models.DecimalField(max_digits=19, decimal_places=2)

    note = models.CharField(max_length=2048)