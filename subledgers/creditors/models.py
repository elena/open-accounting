# -*- coding: utf-8 -*-
from datetime import date, timedelta
from decimal import Decimal
from django.db import models

from subledgers.models import Invoice, Payment, Relation
from subledgers.querysets import InvoiceQuerySet, RelationQuerySet
from subledgers.settings import AGED_PERIODS


class Creditor(Relation):
    """ Group all Entity objects who have terms and invoices to allow for
    simpler queries.
    """

    entity = models.OneToOneField('entities.Entity', related_name='creditors')

    terms = models.IntegerField(default=14)  # settings.DEFAULT_TERMS)



    objects = RelationQuerySet.as_manager()

    class Meta:
        ordering = ['entity__name']

    def __str__(self):
        return self.entity.name


    def invoices_aged(self):
        qs = self.creditorinvoice_set.all()
        aged = {x: "" for x in AGED_PERIODS}
        per_day1 = date.today()
        for period in AGED_PERIODS:
            if period == AGED_PERIODS[-1]:
                total = qs.filter(
                    transaction__date__lte=date.today() - timedelta(
                        days=AGED_PERIODS[-1])).aggregate(
                    period_total=models.Sum("transaction__value"))
                print(total)
            else:
                per_day2 = date.today() - timedelta(days=period)
                print(per_day1, per_day2)
                total = qs.filter(
                    transaction__date__lt=per_day1,
                    transaction__date__gt=per_day2).aggregate(
                        period_total=models.Sum("transaction__value"))
                per_day1 = per_day2 + timedelta(days=1)
            aged[period] = total['period_total']

        return aged


class CreditorAccount(models.Model):

    creditor = models.ForeignKey('creditors.Creditor')

    account = models.ForeignKey('ledgers.Account')

    order = models.CharField(max_length=16, default=0)


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

    objects = InvoiceQuerySet.as_manager()

    class Meta:
        ordering = ['transaction__date']
        unique_together = ("invoice_number", "relation")

    def __str__(self):
        return "[{}] {} -- {} -- ${} [outstanding: ${}]".format(
            self.relation.entity.code, self.transaction.date,
            self.invoice_number, self.transaction.value,
            self.unpaid)

    def save(self, *args, **kwargs):

        # Set unpaid value
        # @@ TODO This can be done better.
        if not self.pk:
            self.unpaid = self.transaction.value
        else:
            if not self.creditorpayment_set.all():
                self.unpaid = self.transaction.value
        super(CreditorInvoice, self).save(*args, **kwargs)

    def is_settled(self):
        if self.outstanding_balance():
            return False
        else:
            return True

    def outstanding_balance(self):
        value = self.transaction.value
        paid = self.creditorpaymentinvoice_set.aggregate(
            sum=models.Sum('value'))
        if paid['sum']:
            self.unpaid = value - paid['sum']
        else:
            self.unpaid = value
        self.save()
        return self.unpaid


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
        blank=True,
        through='creditors.CreditorPaymentInvoice')

    def __str__(self):
        return "[{}] {} -- {} -- ${}".format(
            self.relation.entity.code, self.relation.entity.name,
            self.bank_entry.transaction.date,
            self.bank_entry.transaction.value)

    def has_invoices(self):
        return self.creditorpaymentinvoice_set.count()

    def invoices_total(self):
        return self.creditorpaymentinvoice_set.aggregate(
            models.Sum('value'))['value__sum']

    def is_fully_allocated(self):
        if self.bank_entry and \
           self.invoices_total == self.bank_entry.transaction.value:
            return True
        else:
            return False

    def restart(self):
        # @@TODO probably should be pre-delete hook on CreditorPaymentInvoice
        for crpayinv in self.creditorpaymentinvoice_set.all():
            invoice = crpayinv.invoice
            crpayinv.delete()
            invoice.outstanding_balance()

    def match_invoices(self, value=None):
        """ Automatic matching done by LIFO.

        If bank_entry has been matched `transaction.value` will be used.
        Otherwise `value` argument must be added to this method. """
        if self.has_invoices():
            self.restart()

        if value:
            total = value
        else:
            total = self.bank_entry.transaction.value

        for invoice in self.relation.creditorinvoice_set.open():
            if total > 0:
                new_crpayinv = CreditorPaymentInvoice(
                    payment=self,
                    invoice=invoice,
                )
                if total > invoice.unpaid:
                    total = total - invoice.unpaid
                    new_crpayinv.value = invoice.unpaid
                    new_crpayinv.save()
                elif total < invoice.unpaid:
                    new_crpayinv.value = total
                    new_crpayinv.save()
                    total = 0
            else:
                break
        return self.invoices.all()


class CreditorPaymentInvoice(models.Model):

    payment = models.ForeignKey('creditors.CreditorPayment')

    invoice = models.ForeignKey('creditors.CreditorInvoice')

    value = models.DecimalField(max_digits=19, decimal_places=2)

    def save(self, *args, **kwargs):
        super(CreditorPaymentInvoice, self).save(*args, **kwargs)
        self.invoice.outstanding_balance()


class CreditorLearning(models.Model):

    word = models.CharField(max_length=64, unique=True)

    creditor = models.ForeignKey('creditors.Creditor')


class CreditorMatch(models.Model):

    bank_entry = models.ForeignKey('bank_reconciliations.BankEntry')

    description = models.CharField(max_length=512)

    creditor = models.ForeignKey('creditors.Creditor')
