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

        self.a1 = Account.objects.create(
            element='01', number='0450', name='Account 1')
        self.a2 = Account.objects.create(
            element='01', number='0709', name='Account 2')

        self.kwargs = {
            'date': '5-May-2020',
            'user': self.user,
            'account_DR': self.a1,
            'account_CR': self.a2,
            'value': 1.00,
        }

    def test_journalentry_save_transaction_passes(self):
        self.kwargs['source'] = utils.get_source(JournalEntry)
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
        self.kwargs['source'] = utils.get_source(CreditorInvoice)
        new_creditorinvoice = CreditorInvoice(
            invoice_number='abc123',
            relation=self.creditor
        )
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


class TestEntryMakeLines(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.code = "ABC"
        self.entity = Entity.objects.create(name=self.code.lower())
        self.creditor = Creditor.objects.create(entity=self.entity)

        self.a = Account.objects.create(
            element='03', number='0300', name='ACP')
        self.b = Account.objects.create(
            element='01', number='0100', name='Bank 1')

        self.a1 = Account.objects.create(
            element='01', number='0450', name='Account 1')
        self.a2 = Account.objects.create(
            element='01', number='0709', name='Account 2')

        self.kwargs = {
            'date': '5-May-2020',
            'user': self.user,
        }

    def test_get_lines_balance(self):
        lines = [('01-0700', 1.00),
                 ('01-0450', 1.00)]

        self.assertEqual(
            CreditorInvoice().get_lines_balance(lines), 2.00)

    def test_input_accounts_fails(self):
        kwargs = {
            'accounts': [('01-0700', 1.00),
                         ('01-0450', 1.00)]
        }
        k = {**kwargs, **self.kwargs}
        self.assertRaises(Exception, CreditorInvoice().save_transaction, k)

    def test_input_account_by_number(self):
        kwargs = {
            'account': '01-0450',
            'value': 1.00,
        }

        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_accounts_by_number(self):
        kwargs = {
            'accounts': [('01-0450', 1.00),
                         ('01-0709', 1.00),
                         ('01-0450', 1.00)]
        }
        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_account_DR_CR_by_number(self):
        kwargs = {
            'account_DR': '01-0450',
            'account_CR': self.a2,
            'value': 1.00,
        }
        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_account(self):
        kwargs = {
            'account': self.a1,
            'value': 1.00,
        }

        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_accounts(self):
        kwargs = {
            'accounts': [(self.a1, 1.00),
                         (self.a1, 1.00),
                         (self.a2, 1.00)]
        }
        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_account_DR_CR(self):
        kwargs = {
            'account_DR': self.a1,
            'account_CR': self.a2,
            'value': 1.00,
        }
        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)

    def test_input_account_creditorpayment(self):
        kwargs = {
            'account': self.b,
            'value': 5.00,
        }
        k = {**kwargs, **self.kwargs}
        CreditorInvoice().save_transaction(k)
        self.assertEqual(1, 1)


class TestModelEntryCreateObjectJournal(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.ac = Account.objects.create(
            element='03', number='0450', name='Clearing - Payroll')
        self.ap = Account.objects.create(
            element='03', number='0709', name='PAYG Withholding')
        self.ab = Account.objects.create(
            element='15', number='1905', name='Bar')
        self.af = Account.objects.create(
            element='15', number='1903', name='FOH')
        self.ag = Account.objects.create(
            element='15', number='1910', name='Games')
        self.ak = Account.objects.create(
            element='15', number='1901', name='Kitchen')
        self.ast = Account.objects.create(
            element='15', number='1900', name='Staff')
        self.asl = Account.objects.create(
            element='03', number='0600', name='Superannuation Liability')
        self.asu = Account.objects.create(
            element='15', number='1950', name='Superannuation')

    def test_create_object_single_journalentry_passes(self):

        test_dump = 'value\tdate\ttype\t[03-0450]\t[03-0709]\t[15-1905]\t[15-1903]\t[15-1910]\t[15-1901]\t[15-1900]\t[03-0600]\t[15-1950]\r\n23,017.03\tJan. 31, 2016\tJournalEntry\t-17,817.96\t-3,447.00\t2,385.02\t6,991.98\t730.77\t8,255.34\t2,901.85\t-1,752.07\t1,752.07'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='JournalEntry')

        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('23017.03'),
            date=dateparser.parse('31-Jan-2016'),
            source='subledgers.journals.models.JournalEntry',
            user=self.user)
        test_lines = [
            Line.objects.get(transaction=test_transaction,
                             account=self.ac,
                             value=utils.make_decimal(-17817.96)),
            Line.objects.get(transaction=test_transaction,
                             account=self.ap,
                             value=utils.make_decimal(-3447)),
            Line.objects.get(transaction=test_transaction,
                             account=self.ab,
                             value=utils.make_decimal(2385.02)),
            Line.objects.get(transaction=test_transaction,
                             account=self.af,
                             value=utils.make_decimal(6991.98)),
            Line.objects.get(transaction=test_transaction,
                             account=self.ag,
                             value=utils.make_decimal(730.77)),
            Line.objects.get(transaction=test_transaction,
                             account=self.ak,
                             value=utils.make_decimal(8255.34)),
            Line.objects.get(transaction=test_transaction,
                             account=self.ast,
                             value=utils.make_decimal(2901.85)),
            Line.objects.get(transaction=test_transaction,
                             account=self.asl,
                             value=utils.make_decimal(-1752.07)),
            Line.objects.get(transaction=test_transaction,
                             account=self.asu,
                             value=utils.make_decimal(1752.07)),
        ]
        test_result = [JournalEntry.objects.get(transaction=test_transaction,)]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))


class TestModelEntryGetCls(TestCase):

    # Successes!

    def test_get_cls_valid_model_CreditorInvoice_passes(self):
        self.assertEqual(Entry.get_cls(CreditorInvoice), CreditorInvoice)

    def test_get_cls_valid_model_str_passes(self):
        self.assertEqual(Entry.get_cls('CreditorInvoice'), CreditorInvoice)

    def test_get_cls_valid_model_source_passes(self):
        source = utils.get_source(CreditorInvoice)
        self.assertEqual(Entry.get_cls(source), CreditorInvoice)

    # Failures!

    def test_get_cls_not_valid_model_Account_failure(self):
        self.assertRaises(Exception, Entry.get_cls, Account)

    def test_get_cls_not_valid_model_Creditor_failure(self):
        self.assertRaises(Exception, Entry.get_cls, Creditor)

    def test_get_cls_valid_random_str_failure(self):
        self.assertRaises(Exception, Entry.get_cls, 'asdf')

    def test_get_cls_valid_model_str_failure(self):
        self.assertRaises(Exception, Entry.get_cls, 'Creditor')

    def test_get_cls_valid_model_source_failure(self):
        source = utils.get_source(Creditor)
        self.assertRaises(Exception, Entry.get_cls, source)


class TestModelRelationGetRelation(TestCase):

    def setUp(self):
        self.new_entity_code = "new"
        self.new_entity_name = "new entity"

        self.code0 = "ABC"
        self.code1 = "ABC123"
        self.code2 = "EFG456"

        self.entity0 = Entity.objects.create(name=self.code0.lower())
        self.entity1 = Entity.objects.create(name=self.code1.lower())
        self.entity2 = Entity.objects.create(name=self.code2.lower())

        self.creditor0 = Creditor.objects.create(entity=self.entity0)
        self.creditor1 = Creditor.objects.create(entity=self.entity1)

    # passes

    def test_get_relation_valid_creditor_passes(self):
        self.assertEqual(Creditor().get_relation(self.code1), self.creditor1)

    def test_get_relation_valid_creditor_name_passes(self):
        self.assertEqual(Relation.get_relation(
            self.code1, relation_class="subledgers.creditors.models.Creditor"),
            self.creditor1)

    def test_get_relation_entity_exists_new_creditor_passes(self):
        test_input = Relation.get_relation(
            self.code2, relation_class="subledgers.creditors.models.Creditor")
        # get newly created Creditor
        test_result = Creditor.objects.get(entity=self.entity2)
        self.assertEqual(test_input, test_result)

    def test_get_relation_valid_entity_name_passes(self):
        self.assertEqual(Relation.get_relation(
            self.code1, relation_class="entities.models.Entity"),
            self.entity1)

    def test_get_entry_relation_valid_creditor_passes(self):
        self.assertEqual(Relation.get_relation_by_entry(
            self.code1, 'CreditorInvoice'), self.creditor1)

    # failures

    def test_get_relation_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL')

    def test_get_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL',
                          'subledgers.creditors.models.Creditor')

    def test_get_entry_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor.get_relation_by_entry, 'XFAIL',
                          'subledgers.creditors.models.Creditor')  # note: no `self`/Creditor() # noqa


class TestModelEntryCreateObjectFailure(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.entity0 = Entity.objects.create(name="Bidvest")
        self.creditor0 = Creditor.objects.create(
            entity=self.entity0)
        self.entity1 = Entity.objects.create(name="efg456")
        self.creditor1 = Creditor.objects.create(
            entity=self.entity1)

        ACCOUNTS_PAYABLE_ACCOUNT = Account.objects.create(
            element='03', number='0300', name='ACP')
        settings.GST_CR_ACCOUNT = Account.objects.create(
            element='03', number='0733', name='GST account')
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='03', number='0713', name='GST account')
        self.account_CR_GST = settings.GST_CR_ACCOUNT
        self.account_DR_GST = settings.GST_DR_ACCOUNT
        self.account_creditors = ACCOUNTS_PAYABLE_ACCOUNT
        self.account_GST = settings.GST_CR_ACCOUNT
        self.a1 = Account.objects.create(
            element='15', number='0151', name='Test Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0608', name='Test Account 2')

    def test_create_object_single_rubbish_list_failure(self):

        test_kwargs_list = ['asfd']
        self.assertRaises(Exception, Entry.create_object, test_kwargs_list)

    def test_create_object_single_incomplete_kwarg_failure(self):

        test_kwargs = {
            'relation': self.creditor0,
             # 'object': 'CreditorInvoice', # no object failure
                             'date': dateparser.parse('02-Jun-2017'),
             'gst_total': utils.make_decimal('$0.65'),
             'invoice_number': 'I38731476',
             'order_number': 'guild house',
             'reference': 'O37696095',
             'source': 'subledgers.creditors.models.CreditorInvoice',
             'value': utils.make_decimal('$485.27'),
             'user': self.user,
             'lines': [
                 (self.a1, utils.set_DR('478.12')),
                 (self.a2, utils.set_DR('6.5')),
                 (self.account_creditors, utils.set_CR('485.27')),  # noqa
                 (self.account_GST, utils.set_DR('0.65')),
             ]}
        self.assertRaises(Exception, Entry.create_object, test_kwargs)


# These are the End-to-End tests (dump >> objects)
# These are the only tests that really matter.

class TestModelEntryCreateObjectSale(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.SALES_CLEARING_ACCOUNT = Account.objects.create(
            element='03', number='0410', name='Sales Clearing')
        settings.GST_CR_ACCOUNT = Account.objects.create(
            element='03', number='0733', name='GST account')
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='03', number='0713', name='GST account')
        self.account_CR_GST = settings.GST_CR_ACCOUNT
        self.account_DR_GST = settings.GST_DR_ACCOUNT
        self.a1 = Account.objects.create(
            element='10', number='0100', name='Sales')

    def test_create_object_single_sale_passes(self):

        test_dump = 'value\tdate\ttype\tgst_total\t[10-0100]\r\n3054.6\tJan. 23, 2016\tSale\t277.69\t2776.91'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Sale')

        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('3054.6'),
            date=dateparser.parse('23-Jan-2016'),
            source='subledgers.sales.models.Sale',
            user=self.user)
        test_lines = [
            Line.objects.get(transaction=test_transaction,
                             account=self.SALES_CLEARING_ACCOUNT,
                             value=utils.set_DR('3054.6')),
            Line.objects.get(transaction=test_transaction,
                             account=self.a1,
                             value=utils.set_CR('2776.91')),
            Line.objects.get(transaction=test_transaction,
                             account=self.account_DR_GST,
                             value=utils.set_CR('277.69')),
        ]
        test_result = [Sale.objects.get(transaction=test_transaction,)]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_double_sale_passes(self):

        test_dump = 'value\tdate\ttype\tgst_total\t[10-0100]\r\n3054.6\tJan. 23, 2016\tSale\t277.69\t2776.91\r\n3877.7\tJan. 24, 2016\tSale\t352.52\t3525.18'  # noqa

        test_create_objects = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Sale')

        test_transaction1 = Transaction.objects.get(
            value=utils.make_decimal('3054.6'),
            date=dateparser.parse('23-Jan-2016'),
            source='subledgers.sales.models.Sale',
            user=self.user)
        test_transaction2 = Transaction.objects.get(
            value=utils.make_decimal('3877.7'),
            date=dateparser.parse('24-Jan-2016'),
            source='subledgers.sales.models.Sale',
            user=self.user)
        test_lines = [
            Line.objects.get(transaction=test_transaction1,
                             account=self.SALES_CLEARING_ACCOUNT,
                             value=utils.set_DR('3054.6')),
            Line.objects.get(transaction=test_transaction1,
                             account=self.a1,
                             value=utils.set_CR('2776.91')),
            Line.objects.get(transaction=test_transaction1,
                             account=self.account_DR_GST,
                             value=utils.set_CR('277.69')),
        ]
        test_result = [
            Sale.objects.get(transaction=test_transaction1),
            Sale.objects.get(transaction=test_transaction2)
        ]

        self.assertEqual(test_create_objects, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))


class TestModelEntryCreateObjectExpense(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.entity0 = Entity.objects.create(name="7Eleven")
        self.creditor0 = Creditor.objects.create(
            entity=self.entity0)
        self.entity1 = Entity.objects.create(name="efg456")
        self.creditor1 = Creditor.objects.create(
            entity=self.entity1)

        self.EXPENSE_CLEARING_ACCOUNT = Account.objects.create(
            element='03', number='0430', name='Expense Clearing')
        settings.GST_CR_ACCOUNT = Account.objects.create(
            element='03', number='0733', name='GST account')
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='03', number='0713', name='GST account')
        self.account_CR_GST = settings.GST_CR_ACCOUNT
        self.account_DR_GST = settings.GST_DR_ACCOUNT

        self.a1 = Account.objects.create(
            element='15', number='0150', name='Test Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0608', name='Test Account 2')

    def test_create_object_single_expense_no_entity_passes(self):

        test_dump = 'value\tdate\tnote\ttype\trelation\tgst_total\t[15-1420]\t[15-0715]\t[15-0605]\t[15-0150]\t[15-0500]\t[15-0650]\t[15-0705]\t[15-0710]\t[15-1010]\t[15-1400]\t[15-1430]\t[15-0620]\t[15-1470]\r\n53.47\t11-Dec-2015\t7-ELEVEN 2296 ERINDALE CENT\tExpense\t\t4.86\t\t\t\t48.61\t\t\t\t\t\t\t\t\t'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Expense')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('53.47'),
            date=dateparser.parse('11-Dec-2015'),
            source='subledgers.expenses.models.Expense',
            note='7-ELEVEN 2296 ERINDALE CENT',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('48.61')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.EXPENSE_CLEARING_ACCOUNT,
                                       value=utils.set_CR('53.47')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('4.86')), ]
        test_result = [Expense.objects.get(
            transaction=test_transaction,
        )]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_single_expense_using_entity_passes(self):

        test_dump = 'value\tdate\tnote\ttype\trelation\tgst_total\t[15-1420]\t[15-0715]\t[15-0605]\t[15-0150]\t[15-0500]\t[15-0650]\t[15-0705]\t[15-0710]\t[15-1010]\t[15-1400]\t[15-1430]\t[15-0620]\t[15-1470]\r\n53.47\t11-Dec-2015\t7-ELEVEN 2296 ERINDALE CENT\tExpense\t7ELEVE\t4.86\t\t\t\t48.61\t\t\t\t\t\t\t\t\t'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Expense')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('53.47'),
            date=dateparser.parse('11-Dec-2015'),
            source='subledgers.expenses.models.Expense',
            note='7-ELEVEN 2296 ERINDALE CENT',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('48.61')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.EXPENSE_CLEARING_ACCOUNT,
                                       value=utils.set_CR('53.47')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('4.86')), ]
        test_result = [Expense.objects.get(
            transaction=test_transaction,
            relation=self.entity0,
        )]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_single_expense_using_entity_GST_variation_passes(self):  # noqa

        # GST allocated, not using `gst_total` field.
        test_dump = 'value\tdate\tnote\ttype\trelation\t[03-0733]\t[15-1420]\t[15-0715]\t[15-0605]\t[15-0150]\t[15-0500]\t[15-0650]\t[15-0705]\t[15-0710]\t[15-1010]\t[15-1400]\t[15-1430]\t[15-0620]\t[15-1470]\r\n53.47\t11-Dec-2015\t7-ELEVEN 2296 ERINDALE CENT\tExpense\t7ELEVE\t4.86\t\t\t\t48.61\t\t\t\t\t\t\t\t\t'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Expense')

        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('53.47'),
            date=dateparser.parse('11-Dec-2015'),
            source='subledgers.expenses.models.Expense',
            note='7-ELEVEN 2296 ERINDALE CENT',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('48.61')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.EXPENSE_CLEARING_ACCOUNT,
                                       value=utils.set_CR('53.47')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('4.86')), ]
        test_result = [Expense.objects.get(
            transaction=test_transaction,
            relation=self.entity0,
        )]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_single_expense_in_credit_passes(self):  # noqa

        # Is a credit (ie negative value expense)
        test_dump = 'value\tdate\tnote\ttype\trelation\t[03-0733]\t[15-1420]\t[15-0715]\t[15-0605]\t[15-0150]\t[15-0500]\t[15-0650]\t[15-0705]\t[15-0710]\t[15-1010]\t[15-1400]\t[15-1430]\t[15-0620]\t[15-1470]\r\n53.47\t11-Dec-2015\t7-ELEVEN 2296 ERINDALE CENT\tExpense\t7ELEVE\t-4.86\t\t\t\t-48.61\t\t\t\t\t\t\t\t\t'  # noqa

        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='Expense')

        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('53.47'),
            date=dateparser.parse('11-Dec-2015'),
            source='subledgers.expenses.models.Expense',
            note='7-ELEVEN 2296 ERINDALE CENT',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_CR('48.61')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.EXPENSE_CLEARING_ACCOUNT,
                                       value=utils.set_DR('53.47')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_CR('4.86')), ]
        test_result = [Expense.objects.get(
            transaction=test_transaction,
            relation=self.entity0,
        )]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))


class TestModelEntryCreateObjectTransactionDelete(TransactionTestCase):

    """ This setUp is to test that superfluous `Transaction` objects are not
    created if there is a validation problem with the `Entry`, as `Transaction`
    must be created before `Entry`.

    This is important for system integrity, until there is some generic
    relation from `Transaction` that we can ensure exists.

    # @@ TODO: This important integrity check needs to be done better.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

    def test_create_object_failure_transaction_object_delete(self):  # noqa

        # has blank entity, should fail to create CreditorInvoice
        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\n\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA

        self.assertRaises(Exception, Entry.dump_to_objects,
                          test_dump, user=self.user,
                          object_name='CreditorInvoice')

        test_transaction_kwargs = {
            'value': utils.make_decimal('$485.27'),
            'date': dateparser.parse('02-Jun-2017'),
            'source': 'subledgers.creditors.models.CreditorInvoice',
            'user': self.user}

        self.assertRaises(ObjectDoesNotExist, Transaction.objects.get,
                          **test_transaction_kwargs)

        # This test saved me one time, when Entry was finding a way to be
        # created anyway, because wasn't validating `value` = bal.

        test_transaction_kwargs = {
            'source': 'subledgers.creditors.models.CreditorInvoice',
            'user': self.user}

        self.assertEqual(Transaction.objects.filter(
            **test_transaction_kwargs).count(), 0)

class TestModelEntryCreateObjectCreditorInvoice(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.entity0 = Entity.objects.create(name="Bidvest")
        self.creditor0 = Creditor.objects.create(
            entity=self.entity0)
        self.entity1 = Entity.objects.create(name="efg456")
        self.creditor1 = Creditor.objects.create(
            entity=self.entity1)

        ACCOUNTS_PAYABLE_ACCOUNT = Account.objects.create(
            element='03', number='0300', name='ACP')
        settings.GST_CR_ACCOUNT = Account.objects.create(
            element='03', number='0733', name='GST account')
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='03', number='0713', name='GST account')
        self.account_CR_GST = settings.GST_CR_ACCOUNT
        self.account_DR_GST = settings.GST_DR_ACCOUNT
        self.account_creditors = ACCOUNTS_PAYABLE_ACCOUNT
        self.a1 = Account.objects.create(
            element='15', number='0151', name='Test Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0608', name='Test Account 2')

    def test_create_object_single_creditor_invoice_using_entity_passes(self):

        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA
        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='CreditorInvoice')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('$485.27'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.models.CreditorInvoice',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('478.12')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.a2,
                                       value=utils.set_DR('6.5')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_creditors,
                                       value=utils.set_CR('485.27')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('0.65')), ]
        test_result = [CreditorInvoice.objects.get(
            transaction=test_transaction,
            relation=self.creditor0,
            gst_total=utils.make_decimal('$0.65'),
            invoice_number='I38731476',
            order_number='guild house',
            reference='O37696095',)]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_single_creditor_invoice_passes(self):

        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$1485.27\t$0.65\tguild house\t6.5\t$1,478.12\t\t\t"  # NOQA
        test_create_object = Entry.dump_to_objects(
            test_dump, user=self.user, object_name='CreditorInvoice')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('$1485.27'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.models.CreditorInvoice',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('1478.12')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.a2,
                                       value=utils.set_DR('6.5')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_creditors,
                                       value=utils.set_CR('1485.27')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('0.65')), ]
        test_result = [CreditorInvoice.objects.get(
            transaction=test_transaction,
            relation=self.creditor0,
            gst_total=utils.make_decimal('$0.65'),
            invoice_number='I38731476',
            order_number='guild house',
            reference='O37696095',)]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_single_creditor_invoice_using_creditor_invoice(self):  # noqa

        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA
        test_create_object = CreditorInvoice.dump_to_objects(
            test_dump, user=self.user, object_name='CreditorInvoice')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('$485.27'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.models.CreditorInvoice',
            user=self.user)
        test_lines = [Line.objects.get(transaction=test_transaction,
                                       account=self.a1,
                                       value=utils.set_DR('478.12')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.a2,
                                       value=utils.set_DR('6.5')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_creditors,
                                       value=utils.set_CR('485.27')),
                      Line.objects.get(transaction=test_transaction,
                                       account=self.account_CR_GST,
                                       value=utils.set_DR('0.65')), ]
        test_result = [CreditorInvoice.objects.get(
            transaction=test_transaction,
            relation=self.creditor0,
            gst_total=utils.make_decimal('$0.65'),
            invoice_number='I38731476',
            order_number='guild house',
            reference='O37696095',)]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines))

    def test_create_object_double_creditor_invoice_using_creditor_invoice(self):  # noqa

        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t\r\nEFG456\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house\t2.92\t214.65\t\t\t"  # noqa
        test_create_object = CreditorInvoice.dump_to_objects(
            test_dump, user=self.user, object_name='CreditorInvoice')

        # `.get(..` MUST BE BELOW `test_create_object`
        # get the objects that look exactly correct
        test_transaction0 = Transaction.objects.get(
            value=utils.make_decimal('$485.27'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.models.CreditorInvoice',
            user=self.user)
        test_transaction1 = Transaction.objects.get(
            value=utils.make_decimal('$217.86'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.models.CreditorInvoice',
            user=self.user)
        test_lines0 = [Line.objects.get(transaction=test_transaction0,
                                        account=self.a1,
                                        value=utils.set_DR('478.12')),
                       Line.objects.get(transaction=test_transaction0,
                                        account=self.a2,
                                        value=utils.set_DR('6.5')),
                       Line.objects.get(transaction=test_transaction0,
                                        account=self.account_creditors,
                                        value=utils.set_CR('485.27')),
                       Line.objects.get(transaction=test_transaction0,
                                        account=self.account_CR_GST,
                                        value=utils.set_DR('0.65')), ]
        test_lines1 = [Line.objects.get(transaction=test_transaction1,
                                        account=self.a1,
                                        value=utils.set_DR('214.65')),
                       Line.objects.get(transaction=test_transaction1,
                                        account=self.a2,
                                        value=utils.set_DR('2.92')),
                       Line.objects.get(transaction=test_transaction1,
                                        account=self.account_creditors,
                                        value=utils.set_CR('217.86')),
                       Line.objects.get(transaction=test_transaction1,
                                        account=self.account_CR_GST,
                                        value=utils.set_DR('0.29')), ]
        test_result = [
            CreditorInvoice.objects.get(
                transaction=test_transaction0,
                relation=self.creditor0,
                gst_total=utils.make_decimal('$0.65'),
                invoice_number='I38731476',
                order_number='guild house',
                reference='O37696095',),
            CreditorInvoice.objects.get(
                transaction=test_transaction1,
                relation=self.creditor1,
                gst_total=utils.make_decimal('$0.29'),
                invoice_number='I38728128',
                order_number='guild house',
                reference='O37688231',),
        ]

        self.assertEqual(test_create_object, test_result)
        self.assertEqual(set(list(test_result[0].transaction.lines.all())),
                         set(test_lines0))
        self.assertEqual(set(list(test_result[1].transaction.lines.all())),
                         set(test_lines1))






class TestModelEntryCheckRequired(TestCase):

    def test_check_required_simple_transaction_passes(self):
        test_input = {'date': '02-Jun-2017',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      'lines': [1],
                      'user': 1,
                      'cls': CreditorInvoice,
                      'relation': 1,
                      'bank_transaction_id': 1,
                      'object_name': 'BankEntry',
                      'value': '$485.27'}
        self.assertTrue(Entry.check_required(test_input))

    def test_check_required_normal_transaction_passes(self):
        test_input = {'[15-0151]': '478.12',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'object_name': 'BankEntry',
                      'lines': [1],
                      'user': 1,
                      'relation': 1,
                      'bank_transaction_id': 1,
                      'cls': CreditorInvoice,
                      'date': '02-Jun-2017',
                      'value': '$485.27'}
        self.assertTrue(Entry.check_required(test_input))

    def test_check_required_single_transaction_failure(self):
        test_input = {'[15-0151]': '478.12',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'lines': [1],
                      'user': 1,
                      'value': '$485.27'}
        self.assertRaises(Exception, Entry.check_required,
                          test_input, 'JournalEntry')

    def test_check_required_multiple_transaction_failure(self):
        test_input = {'[15-0151]': '478.12',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5'}
        self.assertRaises(Exception, Entry.check_required,
                          test_input, 'JournalEntry')

    def test_check_required_normal_invoice_passes(self):
        test_input = {'creditor': 'BIDVES',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'lines': [1],
                      'user': 1,
                      'cls': CreditorInvoice,
                      'object_name': 'CreditorInvoice',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertTrue(Entry.check_required(test_input))

    def test_check_required_single_invoice_failure(self):
        test_input = {'creditor': 'BIDVES',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'gst_total': '$0.65',
                      'object_name': 'CreditorInvoice',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertRaises(Exception, Entry.check_required, test_input)

    def test_check_required_multiple_invoice_failure(self):
        test_input = {'creditor': 'BIDVES',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'object_name': 'CreditorInvoice',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertRaises(Exception, Entry.check_required, test_input)

    def test_check_required_simple_invoice_passes(self):
        test_input = {'creditor': 'BIDVES',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'lines': [1],
                      'user': 1,
                      'cls': CreditorInvoice,
                      'object_name': 'CreditorInvoice',
                      'invoice_number': 'I38731476',
                      'value': '$485.27'}

        self.assertTrue(Entry.check_required(test_input))

    def test_check_required_simple_entity_invoice_passes(self):
        test_input = {'entity': 'BIDVES',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'lines': [1],
                      'user': 1,
                      'cls': CreditorInvoice,
                      'object_name': 'CreditorInvoice',
                      'invoice_number': 'I38731476',
                      'value': '$485.27'}

        self.assertTrue(Entry.check_required(test_input))
