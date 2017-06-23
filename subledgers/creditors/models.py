# -*- coding: utf-8 -*-
from django.db import models

from .. import settings
from ..models import Invoice, Payment
from subledgers.models import Invoice, Payment


class Creditor(models.Model):
    """ To add additional details only interesting for this subledger.
    """
    entity = models.ForeignKey('entities.Entity', related_name='creditors')

    terms = models.IntegerField(default=settings.DEFAULT_TERMS)

    def __str__(self):
        return self.entity.name


class CreditorInvoice(Invoice):
    """ `Invoice` is `Entry` that has more details.
    """

    relation = models.ForeignKey('creditors.Creditor')

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


class CreditorPayment(Payment):
    """ `Payment` is `Transaction` where the methods matter.
    """

    # Intentional not compulsory.
    # Payments can be reconciled to here (objects created).
    # It is ALWAYS the case that some payments will not line up to
    relation = models.ForeignKey('creditors.Creditor', null=True, blank=True)

    value = models.DecimalField(max_digits=19, decimal_places=2,
                                null=True, blank=True, default=None)


class CreditorPaymentInvoice(Payment):
    payment = models.ForeignKey(
        'creditors.CreditorPayment', null=True, blank=True)

    invoice = models.ForeignKey(
        'creditors.CreditorInvoice', null=True, blank=True)
    value_paid = models.DecimalField(max_digits=19, decimal_places=2)
