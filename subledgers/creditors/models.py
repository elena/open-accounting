# -*- coding: utf-8 -*-
from subledgers.models import Invoice, Payment, Relation
from django.db import models


class Creditor(Relation):
    """ Group all Entity objects who have terms and invoices to allow for
    simpler queries.
    """

    entity = models.ForeignKey('entities.Entity', related_name='creditors')

    terms = models.IntegerField(default=14)  # settings.DEFAULT_TERMS)

    def __str__(self):
        return self.entity.name


class SpecifyRelation(Relation, models.Model):

    # *** ABSTRACT CLASS ***

    """ Convenience class: Rather than 'Entity' relation should be 'Creditor'

    This will be convenient/less messy for queries later.
    """

    relation = models.ForeignKey('creditors.Creditor')

    class Meta:
        abstract = True


class CreditorInvoice(SpecifyRelation, Invoice):

    """ `Invoice` is `Entry` that has more details.
    """

    def __str__(self):
        return "[{}] {} -- {} -- ${}".format(self.relation.entity.code,
                                             self.transaction.date,
                                             self.invoice_number,
                                             self.transaction.value)

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


class CreditorPayment(SpecifyRelation, Payment):
    """ `Payment` has:

    `Entity` so can know status of account

    `Payment` <<>> `BankTransaction` so can know details of payment.

    `Transaction` ledger for clearing ACP
    """
    pass
