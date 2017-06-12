# -*- coding: utf-8 -*-
from django.db import models

from .. import settings
from ..models import Entry, Transaction


class BankTransaction(models.Model):
    """ Nothing to do with `subledgers.Transaction`.

    For reconciliation purposes.

    List of transaction which come from the bank statements.

    Dumped in here and then allocated. Transaction can be created using the details
    provided from statement.
    """

    bank_account = models.ForeignKey('bank_accounts.BankAccount',
                                     related_name='banktransactions')

    transaction = models.OneToOneField(Transaction, null=True, blank=True,
                                       default=None,
                                       related_name='banktransactions')

    # ~~ fields from dump ~~

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

    # ~~ working fields ~~

    note = models.CharField(max_length=64, blank=True, default=None, null=True)

    tags = models.ManyToManyField('ledgers.Tag', blank=True, default=None,
                                  related_name="banktransactions")

    class Meta:
        ordering = ['date']
    def __str__(self):
        return "{:%d-%b-%Y} -- ${} -- {}".format(self.date, self.value, self.description)



# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Bank Account Matching

# Same as above there is plenty of discussion here:
# http://admin-accounting.blogspot.com/2017/06/bank-reconciliations-sure.html
# http://admin-accounting.blogspot.com/2017/06/bank-import-process-matching-goes.html
# http://admin-accounting.blogspot.com/2017/06/bank-accounts-couplingpayment-accounts.html

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class BankLearning(models.Model):

    word = models.CharField(max_length=64)

    account = models.ForeignKey('ledgers.Account')