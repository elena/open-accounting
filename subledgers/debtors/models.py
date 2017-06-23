# # -*- coding: utf-8 -*-
# from django.db import models

# from subledgers.models import Invoice, Payment


# class Debtor(models.Model):
#     """ To add additional details only interesting for this subledger.
#     """
#     entity = models.ForeignKey('entities.Entity', related_name='debtors')

#     terms = models.IntegerField(default=14)  # settings.DEFAULT_TERMS)

#     def __str__(self):
#         return self.entity.name


# class DebtorInvoice(Invoice):
#     """ `Invoice` is `Entry` that has more details. """

#     relation = models.ForeignKey('debtors.Debtor')

#     def __str__(self):
#         return "[{}] {} -- {} -- ${}".format(self.relation.entity.code,
#                                              self.transaction.date,
#                                              self.invoice_number,
#                                              self.transaction.value)


# class DebtorPayment(Payment):
#     """ `Payment` is `Transaction` where the methods matter. """

#     relation = models.ForeignKey('debtors.Debtor', null=True, blank=True)

#     value = models.DecimalField(max_digits=19, decimal_places=2,
#                                 null=True, blank=True, default=None)


# class DebtorPaymentInvoice(Payment):
#     payment = models.ForeignKey(
#         'debtors.DebtorPayment', null=True, blank=True)

#     invoice = models.ForeignKey(
#         'debtors.DebtorInvoice', null=True, blank=True)
#     value_paid = models.DecimalField(max_digits=19, decimal_places=2)
