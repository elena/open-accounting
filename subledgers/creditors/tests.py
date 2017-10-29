# -*- coding: utf-8 -*-
import dateparser
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from ledgers.utils import get_source


from entities.models import Entity
from ledgers.bank_accounts.models import BankAccount
from ledgers.models import Account, Transaction
from subledgers import settings
from subledgers.bank_reconciliations.models import BankLine, BankEntry
from subledgers.creditors.models import (Creditor, CreditorInvoice,
                                         CreditorPayment,
                                         CreditorPaymentInvoice)


class TestCreditorInvoiceMethods(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        # create accounts
        self.a1 = Account.objects.create(
            element='01', number='0150', name='a1')
        self.a2 = Account.objects.create(
            element='01', number='0100', name='a2')

        # create creditors objects
        entity = Entity.objects.create(code='a', name='a')
        self.creditor = Creditor.objects.create(entity=entity)

        # create bank_reconciliation objects
        self.ba = BankAccount(account=self.a1, bank='CBA')
        self.ba.save()

        trans_kwargs = {
            'user': self.user,
            'date': date(2017,5,2),
            'account_DR': self.a1,
            'account_CR': self.a2,
        }

        # banktransacion created, transaction matched
        # Payment 1
        trans_kwargs['value'] = Decimal(350)
        trans_kwargs['source'] = get_source(BankLine)
        self.b1 = BankLine(date=date(2017, 6, 16), value=trans_kwargs['value'],
            bank_account=self.ba, line_dump='1', description='1')
        self.b1.save()
        self.e1 = BankEntry(bank_line=self.b1)
        self.e1.save_transaction(trans_kwargs)
        self.p1 = CreditorPayment(relation = self.creditor,
            bank_entry = self.e1, user = self.user)
        self.p1.save()

        # Payment 2
        trans_kwargs['value'] = Decimal(20)
        trans_kwargs['account_DR'] = self.a1
        trans_kwargs['account_CR'] = self.a2
        self.b2 = BankLine(date=date(2017, 6, 16), value=trans_kwargs['value'],
            bank_account=self.ba, line_dump='2', description='2')
        self.b2.save()
        self.e2 = BankEntry(bank_line=self.b2)
        self.e2.save_transaction(trans_kwargs)
        self.p2 = CreditorPayment(relation = self.creditor,
            bank_entry = self.e2, user = self.user)
        self.p2.save()

        for x in range(1,6):
            trans_kwargs['value'] = 100.00
            trans_kwargs['source'] = get_source(CreditorInvoice)
            trans_kwargs['date'] = date(2017,5,2)-timedelta(days=x*30)
            trans_kwargs['account_DR'] = self.a1
            trans_kwargs['account_CR'] = self.a2
            new_invoice = CreditorInvoice(
                relation=self.creditor, invoice_number=x)
            new_invoice.save_transaction(trans_kwargs)

        # Intentionally leaving this here to see what's going on.
        # for x in self.p1.match_invoices():
        #     print(x)

    def test_outstanding_balance1(self):
        i1 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='1')
        self.assertEqual(i1.outstanding_balance(), Decimal('100.00'))

    def test_outstanding_balance2(self):
        self.p1.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.outstanding_balance(), Decimal('50.00'))

    def test_outstanding_balance3(self):
        self.p1.match_invoices()
        i3 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='3')
        self.assertEqual(i3.outstanding_balance(), Decimal('0.00'))

    def test_outstanding_balance4(self):
        self.p1.match_invoices()
        i4 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='4')
        self.assertEqual(i4.outstanding_balance(), Decimal('0.00'))

    def test_outstanding_balance5(self):
        self.p1.match_invoices()
        i5 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='5')
        self.assertEqual(i5.outstanding_balance(), Decimal('0.00'))

    def test_outstanding_balance_2nd_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.outstanding_balance(), Decimal('30.00'))

    def test_outstanding_balance_dup_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.outstanding_balance(), Decimal('30.00'))
        
    def test_is_settled1(self):
        i1 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='1')
        self.assertEqual(i1.is_settled(), False)

    def test_is_settled2(self):
        self.p1.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.is_settled(), False)

    def test_is_settled3(self):
        self.p1.match_invoices()
        i3 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='3')
        self.assertEqual(i3.is_settled(), True)

    def test_is_settled4(self):
        self.p1.match_invoices()
        i4 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='4')
        self.assertEqual(i4.is_settled(), True)

    def test_is_settled5(self):
        self.p1.match_invoices()
        i5 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='5')
        self.assertEqual(i5.is_settled(), True)

    def test_is_settled_2nd_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.is_settled(), False)

    def test_is_settled_dup_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.is_settled(), False)
        

class TestCreditorPaymentMatchInvoiceMethod(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        # create accounts
        self.a1 = Account.objects.create(
            element='01', number='0150', name='a1')
        self.a2 = Account.objects.create(
            element='01', number='0100', name='a2')

        # create creditors objects
        entity = Entity.objects.create(code='a', name='a')
        self.creditor = Creditor.objects.create(entity=entity)

        # create bank_reconciliation objects
        self.ba = BankAccount(account=self.a1, bank='CBA')
        self.ba.save()

        # banktransacion created, transaction matched
        # Payment 1
        t1_value = Decimal(350)
        lines = (self.a1, self.a2, t1_value)
        self.t1 = Transaction(date=date(2017, 6, 16), value=0, user=self.user,
                              source="{}".format(BankAccount.__module__))
        self.t1.save(lines=lines)
        self.b1 = BankLine(date=date(2017, 6, 16), value=t1_value,
                                  bank_account=self.ba,
                                  line_dump='Test Transaction 1',
                                  description='Test Transaction 1')
        self.b1.save()
        self.e1 = BankEntry.objects.create(transaction=self.t1,
                                           bank_line=self.b1)

        self.p1 = CreditorPayment(relation = self.creditor,
            bank_entry = self.e1, user = self.user)
        self.p1.save()

        # Payment 2
        t2_value = Decimal(20)
        lines = (self.a1, self.a2, t2_value)
        self.t2 = Transaction(date=date(2017, 6, 16), value=0, user=self.user,
                              source="{}".format(BankAccount.__module__))
        self.t2.save(lines=lines)
        self.b2 = BankLine(date=date(2017, 6, 16), value=t2_value,
                                  bank_account=self.ba,
                                  line_dump='Test Transaction 2',
                                  description='Test Transaction 2')
        self.b2.save()
        self.e2 = BankEntry.objects.create(transaction=self.t2,
                                           bank_line=self.b2)
        self.p2 = CreditorPayment(relation = self.creditor,
            bank_entry = self.e2, user = self.user)
        self.p2.save()

        for x in range(1,6):
            new_transaction = Transaction(
                user=self.user,
                date=date(2017,5,2)-timedelta(days=x*30),
                source=get_source(CreditorInvoice))
            new_transaction.save(lines=(self.a1, self.a2, 100.00))
            new_invoice = CreditorInvoice(
                relation=self.creditor,
                transaction=new_transaction,
                invoice_number=x)
            new_invoice.save()

    def test_match_invoices_simple_case1(self):
        self.p1.match_invoices()
        i1 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='1')
        self.assertEqual(i1.unpaid, Decimal('100.00'))

    def test_match_invoices_simple_case2(self):
        self.p1.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.unpaid, Decimal('50.00'))

    def test_match_invoices_simple_case3(self):
        self.p1.match_invoices()
        i3 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='3')
        self.assertEqual(i3.unpaid, Decimal('0.00'))

    def test_match_invoices_simple_case4(self):
        self.p1.match_invoices()
        i4 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='4')
        self.assertEqual(i4.unpaid, Decimal('0.00'))

    def test_match_invoices_simple_case5(self):
        self.p1.match_invoices()
        i5 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='5')
        self.assertEqual(i5.unpaid, Decimal('0.00'))

    def test_match_invoices_2nd_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.unpaid, Decimal('30.00'))

    def test_match_invoices_dup_payment_case(self):
        """ Second payment on the same invoice """
        self.p1.match_invoices()
        self.p2.match_invoices()
        self.p2.match_invoices()
        i2 = CreditorInvoice.objects.get(
            relation=self.creditor, invoice_number='2')
        self.assertEqual(i2.unpaid, Decimal('30.00'))
