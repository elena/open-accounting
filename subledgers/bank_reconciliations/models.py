# -*- coding: utf-8 -*-
from django.db import models

from ..models import Entry
from ..settings import SUBLEDGERS_AVAILABLE
from . import querysets


class BankEntry(Entry):
    """ Inherits attribute `ledger.Transaction` from `subledger.Entry`. """

    bank_line = models.OneToOneField(
        'bank_reconciliations.BankLine')

    subledger = models.CharField(
        max_length=50,
        choices=[(subledger['actual'], subledger['human'])
                 for subledger in SUBLEDGERS_AVAILABLE],
        default='', blank=True)


    class Meta:
        verbose_name_plural = "bank entries"


class BankLine(models.Model):

    # ** Outside of Trial Balance/accounting system **
    # No relationship to `ledgers.Transaction`

    """
    For information storage and reconciliation purposes.

    List of transaction which come from the bank statements.

    Dumped in here and then allocated.
    Transaction can be created using the details  provided from statement.
    """

    bank_account = models.ForeignKey('bank_accounts.BankAccount',
                                     related_name='banktransactions')

    # ~~ fields from dump ~~

    # Straight from import uniquely stored here, not duplicate of `Transaction`
    date = models.DateField()

    value = models.DecimalField(max_digits=19, decimal_places=2)

    # Straight from import, so don't lose anything
    line_dump = models.CharField(max_length=2048)

    # For use by NLTK to creating learning.
    # Might be just same as 'line_dump', but may have had some processing
    description = models.CharField(max_length=512)

    # Additional bank-supplied information not important to this system.
    # Eg "CREDIT CARD PURCHASE", "AUS Card xx7495"
    additional = models.CharField(max_length=512, null=True, blank=True,
                                  default=None)

    # No real reason to gather this except for the reason that it can be.
    balance = models.DecimalField(max_digits=19, decimal_places=2,
                                  null=True, blank=True, default=None)

    not_now = models.BooleanField(default=False)
    # ~~ working fields ~~

    note = models.CharField(max_length=64, blank=True, default=None, null=True)

    tags = models.ManyToManyField('ledgers.Tag', blank=True, default=None,
                                  related_name="banktransactions")

    objects = querysets.QuerySet.as_manager()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return "{:%d-%b-%Y} -- ${} -- {}".format(self.date, self.value,
                                                 self.description)


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Bank Account Matching

# Same as above there is plenty of discussion here:
# http://open-accounting.blogspot.com/2017/06/bank-reconciliations-sure.html
# http://open-accounting.blogspot.com/2017/06/bank-import-process-matching-goes.html
# http://open-accounting.blogspot.com/2017/06/bank-accounts-couplingpayment-accounts.html

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class BankLearning(models.Model):

    word = models.CharField(max_length=64)

    account = models.ForeignKey('ledgers.Account')
