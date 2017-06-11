# -*- coding: utf-8 -*-
from django.db import models


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Bank Accounts
#
# See detailed discussion:
# http://admin-accounting.blogspot.com/2017/06/bank-reconciliations-sure.html
# http://admin-accounting.blogspot.com/2017/06/bank-import-process-matching-goes.html
# http://admin-accounting.blogspot.com/2017/06/bank-accounts-couplingpayment-accounts.html

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


BANKS = [
    ('CBA', 'CBA'),
    ('NAB', 'NAB'),
]


class BankAccount(models.Model):

    account = models.OneToOneField('ledgers.Account', null=False, related_name="bankaccounts")

    bank = models.CharField(max_length=8, choices=BANKS, blank=True,
                            null=True, default=None,
                            help_text="Used for statement importing formats.")

    name = models.CharField(max_length=6, blank=True, default="")

    bsb = models.CharField(max_length=64, blank=True, default="")

    account_number = models.IntegerField(blank=True, null=True)

    note = models.CharField(max_length=2048, blank=True, default="")

    def __str__(self):
        return "{} {} {}".format(self.bsb, self.account_number, self.account)