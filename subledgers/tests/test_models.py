# -*- coding: utf-8 -*-
import dateparser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase  # , Client

from entities.models import Entity
from ledgers import utils
from ledgers.models import Account, Transaction, Line
from subledgers import settings
from subledgers.models import Entry, Relation
from subledgers.creditors.models import Creditor, CreditorInvoice
from subledgers.expenses.models import Expense
from subledgers.sales.models import Sale
from subledgers.journals.models import JournalEntry


class TestModelEntrySaveTransaction(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.code = "ABC"
        self.entity = Entity.objects.create(name=self.code.lower())
        self.creditor = Creditor.objects.create(entity=self.entity)

        self.c = Account.objects.create(
            element='03', number='0300', name='ACP')

        self.a1 = Account.objects.create(
            element='01', number='0450', name='Account 1')
        self.a2 = Account.objects.create(
            element='01', number='0709', name='Account 2')

        self.kwargs = {
            'date': '5-May-2020',
            'user': self.user,
            'account_DR': '01-0450',
            'account_CR': '01-0709',
            'value': 1.00,
        }

        # 'account_DR': self.a1,
        # 'account_CR': self.a2,

    def test_journalentry_save_transaction_account_code_passes(self):

        new_journalentry = JournalEntry()
        new_journalentry.save_transaction(self.kwargs)

        test_kwargs = {
            'transaction__date': utils.make_date('5-May-2020'),
            'transaction__user': self.user,
            'transaction__value': 1.00,
            'transaction__source': utils.get_source(JournalEntry)
        }
        test_object = JournalEntry.objects.get(**test_kwargs)
        self.assertEqual(new_journalentry, test_object)

    def test_journalentry_save_transaction_account_obj_passes(self):

        self.kwargs = {
            'date': '5-May-2020',
            'user': self.user,
            'account_DR': self.a1,
            'account_CR': self.a2,
            'value': 1.00,
        }

        new_journalentry = JournalEntry()
        new_journalentry.save_transaction(self.kwargs)

        test_kwargs = {
            'transaction__date': utils.make_date('5-May-2020'),
            'transaction__user': self.user,
            'transaction__value': 1.00,
            'transaction__source': utils.get_source(JournalEntry)
        }
        test_object = JournalEntry.objects.get(**test_kwargs)
        self.assertEqual(new_journalentry, test_object)

    def test_creditorinvoice_save_transaction_passes(self):

        self.kwargs = {
            'date': '5-May-2020',
            'user': self.user,
            'account': self.a1,
            'value': 1.00,
        }
        self.kwargs['invoice_number'] = 'abc123'
        self.kwargs['relation'] = self.creditor
        self.kwargs['gst_total'] = 0
        new_creditorinvoice = CreditorInvoice()
        new_creditorinvoice.save_transaction(self.kwargs)
        test_kwargs = {
            'transaction__date': utils.make_date('5-May-2020'),
            'transaction__user': self.user,
            'transaction__value': 1.00,
            'transaction__source': utils.get_source(CreditorInvoice)
        }
        test_object = CreditorInvoice.objects.get(**test_kwargs)
        self.assertEqual(new_creditorinvoice, test_object)


class TestModelEntryDRCR(TestCase):

    def test_crdr_journalentry(self):
        a = JournalEntry().is_cr_or_dr_in_tb()
        self.assertEqual(a, None)

    def test_crdr_creditorinvoice(self):
        a = CreditorInvoice().is_cr_or_dr_in_tb()
        self.assertEqual(a, 'CR')

    def test_crdr_creditorinvoice_credit(self):
        a = CreditorInvoice(is_credit=True).is_cr_or_dr_in_tb()
        self.assertEqual(a, 'DR')


class TestModelEntryGetRelation(TestCase):

    def setUp(self):
        self.code = "ABC"
        self.entity = Entity.objects.create(name=self.code.lower())
        self.creditor = Creditor.objects.create(entity=self.entity)

    def test_relation_code_Entity(self):
        test_rel = JournalEntry().get_relation(self.entity.code)
        self.assertEqual(self.entity, test_rel)

    def test_relation_obj_Entity(self):
        test_rel = JournalEntry().get_relation(self.entity)
        self.assertEqual(self.entity, test_rel)

    def test_relation_code_Creditor(self):
        test_rel = CreditorInvoice().get_relation(self.creditor.entity.code)
        self.assertEqual(self.creditor, test_rel)

    def test_relation_obj_Creditor(self):
        test_rel = CreditorInvoice().get_relation(self.creditor)
        self.assertEqual(self.creditor, test_rel)




# These are the End-to-End tests (dump >> objects)
# These are the only tests that really matter.

