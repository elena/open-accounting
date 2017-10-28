# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.db import models

from subledgers.models import Invoice, Payment, Relation
from subledgers.querysets import InvoiceQuerySet
from subledgers.settings import AGED_PERIODS


class Creditor(Relation):
    """ Group all Entity objects who have terms and invoices to allow for
    simpler queries.
    """

    entity = models.OneToOneField('entities.Entity', related_name='creditors')

    terms = models.IntegerField(default=14)  # settings.DEFAULT_TERMS)



    class Meta:
        ordering = ['entity__name']

    def __str__(self):
        return self.entity.name




class SpecificRelation(Relation, models.Model):

    # *** ABSTRACT CLASS ***

    """ Convenience class: Rather than 'Entity' relation should be 'Creditor'

    This will be convenient/less messy for queries later.
    """

    relation = models.ForeignKey('creditors.Creditor')

    class Meta:
        abstract = True


class CreditorInvoice(SpecificRelation, Invoice):

    """ `Invoice` is `Entry` that has more details. """

    def __str__(self):
        return "[{}] {} -- {} -- ${} [oustanding: ${}]".format(self.relation.entity.code,
                                             self.transaction.date,
                                             self.invoice_number,
                                             self.transaction.value,
                                             self.unpaid)


    """
    def is_fully_paid(self):
        if self.get_outstanding_balance():
            return True
        else:
            return False


    def get_outstanding_balance(self):
        transaction_value
        minus
        sum related CreditorPaymentInvoices
        return #[]
    """


class CreditorPayment(SpecificRelation, Payment):

    # ** Outside of Trial Balance/accounting system **
    # No relationship to `ledgers.Transaction`

    """
    >> inherit: `relation` from `SpecificRelation`

    >> inherit: `bank_entry` from `Payment`


    `Payment` has:
    `relation`: `Entity` so can know status of account
    `Payment` <<>> `BankTransaction` so can know details of payment.

    """

    invoices = models.ManyToManyField(
        'creditors.CreditorInvoice',
        through='creditors.CreditorPaymentInvoice')


class CreditorPaymentInvoice(models.Model):

    payment = models.ForeignKey('creditors.CreditorPayment')

    invoice = models.ForeignKey('creditors.CreditorInvoice')

    value = models.DecimalField(max_digits=19, decimal_places=2)


class CreditorLearning(models.Model):

    word = models.CharField(max_length=64, unique=True)

    creditor = models.ForeignKey('creditors.Creditor')


class CreditorMatch(models.Model):

    bank_entry = models.ForeignKey('bank_reconciliations.BankEntry')

    description = models.CharField(max_length=512)

    creditor = models.ForeignKey('creditors.Creditor')
