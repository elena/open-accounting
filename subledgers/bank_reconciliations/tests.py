# -*- coding: utf-8 -*-
# import warnings
# import unittest
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase  # , Client
# from django.contrib.auth.models import User

from ledgers.models import Account, Transaction
from ledgers.bank_accounts.models import BankAccount
from .models import BankTransaction


class TestBankTransactionQueryset(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.a1 = Account(element='01', number='0101',
                          name='Test Bank Account 1')
        self.a1.save()
        self.a2 = Account(element='15', number='0501',
                          name='Test Expenses Account 1')
        self.a2.save()
        self.ba = BankAccount(account=self.a1, bank='CBA')
        self.ba.save()

        # banktransacion created, transaction matched
        t1_value = Decimal(10)
        lines = (self.a1, self.a2, t1_value)
        self.t1 = Transaction(date=date(2017, 6, 16), value=0, user=self.user,
                              source="{}".format(BankAccount.__module__))
        self.t1.save(lines=lines)

        self.b1 = BankTransaction(transaction=self.t1,
                                  date=date(2017, 6, 16), value=t1_value,
                                  bank_account=self.ba,
                                  line_dump='Test Transaction 1',
                                  description='Test Transaction 1')
        self.b1.save()

        # banktransacion created only
        self.b2 = BankTransaction(date=date(2017, 6, 16), value=Decimal(20),
                                  bank_account=self.ba,
                                  line_dump='Test Transaction 2',
                                  description='Test Transaction 2')
        self.b2.save()
        self.b3 = BankTransaction(date=date(2017, 6, 16), value=Decimal(30),
                                  bank_account=self.ba,
                                  line_dump='Test Transaction 3',
                                  description='Test Transaction 3')
        self.b3.save()

    def test_banktransaction_queryset_reconcilied_passes(self):
        reconciled_obj_list = BankTransaction.objects.reconciled()
        self.assertEqual(reconciled_obj_list.count(), 1)
        self.assertIn(self.b1, reconciled_obj_list)
        self.assertNotIn(self.b2, reconciled_obj_list)
        self.assertNotIn(self.b3, reconciled_obj_list)

    def test_banktransaction_queryset_unreconcilied_passes(self):
        unreconciled_obj_list = BankTransaction.objects.unreconciled()
        self.assertEqual(unreconciled_obj_list.count(), 2)
        self.assertNotIn(self.b1, unreconciled_obj_list)
        self.assertIn(self.b2, unreconciled_obj_list)
        self.assertIn(self.b3, unreconciled_obj_list)
