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

    def test_get_specific_relation_valid_creditor_passes(self):
        self.assertEqual(Relation.get_specific_relation(
            self.code1, 'CreditorInvoice'), self.creditor1)

    # failures

    def test_get_relation_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL')

    def test_get_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL',
                          'subledgers.creditors.models.Creditor')

    def test_get_specific_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor.get_specific_relation, 'XFAIL',
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
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='13', number='0700', name='GST account')
        self.account_creditors = ACCOUNTS_PAYABLE_ACCOUNT
        self.account_GST = settings.GST_DR_ACCOUNT
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
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='03', number='0733', name='GST account')
        self.account_GST = settings.GST_DR_ACCOUNT
        self.a1 = Account.objects.create(
            element='15', number='0150', name='Test Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0608', name='Test Account 2')

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
                                       account=self.account_GST,
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
                                       account=self.account_GST,
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
                                       account=self.account_GST,
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
        settings.GST_DR_ACCOUNT = Account.objects.create(
            element='13', number='0700', name='GST account')
        self.account_creditors = ACCOUNTS_PAYABLE_ACCOUNT
        self.account_GST = settings.GST_DR_ACCOUNT
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
                                       account=self.account_GST,
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
                                       account=self.account_GST,
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
                                       account=self.account_GST,
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
                                        account=self.account_GST,
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
                                        account=self.account_GST,
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
