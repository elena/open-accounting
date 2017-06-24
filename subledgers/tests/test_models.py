# -*- coding: utf-8 -*-
import dateparser
from django.contrib.auth.models import User
from django.test import TestCase  # , Client

from entities.models import Entity
from ledgers import utils
from ledgers.models import Account, Transaction, Line
from subledgers import settings
from subledgers.models import Entry
from subledgers.creditors.models import Creditor, CreditorInvoice


class TestModelRelationGetRelation(TestCase):

    def setUp(self):
        self.new_entity_code = "new"
        self.new_entity_name = "new entity"

        self.entity0 = Entity.objects.create(name="abc")
        self.entity1 = Entity.objects.create(name="abc123")
        self.entity2 = Entity.objects.create(name="efg4")

        self.creditor1 = Creditor.objects.create(
            entity=self.entity1)

    def test_get_relation_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL')

    def test_get_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor().get_relation, 'XFAIL',
                          'CreditorInvoice')

    def test_get_specific_relation_no_entity_failure(self):
        self.assertRaises(Exception, Creditor.get_specific_relation, 'XFAIL',
                          'CreditorInvoice')  # note: no `self`/Creditor()

    def test_get_or_create_relation_and_entity_add_name_passes(self):
        creditor0 = Creditor().get_or_create_relation_and_entity(
            self.new_entity_code, name=self.new_entity_name)
        self.assertEqual(Creditor().get_or_create_relation_and_entity(
            self.new_entity_code, name=self.new_entity_name), creditor0)

    def test_get_or_create_relation_and_entity_no_name_failure(self):
        self.assertRaises(Exception,
                          Creditor().get_or_create_relation_and_entity,
                          self.new_entity_code)

    def test_get_relation_valid_entity_passes(self):
        creditor0 = Creditor.objects.create(entity=self.entity0)
        self.assertEqual(Creditor().get_relation(
            self.entity0.code), creditor0)

    def test_get_relation_valid_creditor_passes(self):
        self.assertEqual(Creditor().get_relation(
            self.entity1.code), self.creditor1)

    def test_get_relation_valid_entity_not_creditor_passes(self):
        self.assertEqual(Creditor().get_relation(
            self.entity1.code), self.creditor1)

    def test_get_specific_relation_valid_creditor_passes(self):
        self.assertEqual(Creditor.get_specific_relation(  # note: no `self`/Creditor() # noqa
            self.entity1.code, 'CreditorInvoice'), self.creditor1)


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
        self.assertRaises(Exception, Entry.create_objects, test_kwargs_list)

    def test_create_object_single_incomplete_kwarg_failure(self):

        test_kwargs_list = [
            {'relation': self.creditor0,
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
             ]}, ]
        self.assertRaises(Exception, Entry.create_objects, test_kwargs_list)


# These are the only tests that really matter.

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
        test_kwargs_list = Entry.dump_to_kwargs(
            test_dump, user=self.user, object_name='CreditorInvoice')
        test_create_object = Entry.create_objects(test_kwargs_list)

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

    def test_create_object_single_creditor_invoice_using_creditor_invoice(self):  # noqa

        test_dump = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA
        test_kwargs_list = CreditorInvoice.dump_to_kwargs(
            test_dump, user=self.user, object_name='CreditorInvoice')
        test_create_object = CreditorInvoice.create_objects(test_kwargs_list)

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
        test_kwargs_list = CreditorInvoice.dump_to_kwargs(
            test_dump, user=self.user, object_name='CreditorInvoice')
        test_create_object = CreditorInvoice.create_objects(test_kwargs_list)

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


class TestModelEntryDumpToKwargs(TestCase):

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

        # needed for result display
        self.account_creditors = settings.ACCOUNTS_PAYABLE_ACCOUNT
        self.account_GST = settings.GST_DR_ACCOUNT
        self.a1 = Account.objects.create(
            element='15', number='0151', name='Test Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0608', name='Test Account 2')

    def test_dump_to_kwargs_no_accounts_invoice_double_passes(self):
        test_input = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\r\nEFG456\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house"  # NOQA
        test_result = [
            {'relation': self.creditor0,
             'cls': CreditorInvoice,
             'creditor': 'BIDVES',
             'object_name': 'CreditorInvoice',
             'date': dateparser.parse('02-Jun-2017'),
             'gst_total': utils.make_decimal('$0.65'),
             'invoice_number': 'I38731476',
             'order_number': 'guild house',
             'reference': 'O37696095',
             'source': 'subledgers.creditors.models.CreditorInvoice',
             'user': self.user,
             'value': utils.make_decimal('$485.27')},
            {'cls': CreditorInvoice,
             'relation': self.creditor1,
             'creditor': 'EFG456',
             'object_name': 'CreditorInvoice',
             'date': dateparser.parse('02-Jun-2017'),
             'gst_total': utils.make_decimal('$0.29'),
             'invoice_number': 'I38728128',
             'order_number': 'guild house',
             'reference': 'O37688231',
             'source': 'subledgers.creditors.models.CreditorInvoice',
             'user': self.user,
             'value': utils.make_decimal('$217.86')},
        ]

        results = Entry.dump_to_kwargs(
            test_input, user=self.user, object_name='CreditorInvoice')
        for i, x in enumerate(test_result):
            results[i].pop('lines')
            self.assertDictEqual(x, results[i])

    # This ugly test kind of doesn't matter.
    # It's the next one: create_objects (from the kwargs) that matters and is waaaay
    # easier to test.

    def test_dump_to_kwargs_invoice_double_passes(self):
        test_input = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t\r\nEFG456\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house\t2.92\t214.65\t\t\t"  # noqa
        test_result = [
            {'relation': self.creditor0,
             # @@ TODO could clean up this relic. not important.
             'creditor': 'BIDVES',
             'cls': CreditorInvoice,
             'object_name': 'CreditorInvoice',
             'date': dateparser.parse('02-Jun-2017'),
             'gst_total': utils.make_decimal('$0.65'),
             'invoice_number': 'I38731476',
             'order_number': 'guild house',
             'reference': 'O37696095',
             'source': 'subledgers.creditors.models.CreditorInvoice',
             'value': utils.make_decimal('$485.27'),
             'user': self.user,
             '[15-0151]': '478.12',
             '[15-0155]': '',
             '[15-0301]': '',
             '[15-0305]': '',
             '[15-0608]': '6.5',
             'lines': [
                 (self.a1, utils.set_DR('478.12')),
                 (self.a2, utils.set_DR('6.5')),
                 (self.account_creditors, utils.set_CR('485.27')),
                 (self.account_GST, utils.set_DR('0.65')),
             ]},
            {'relation': self.creditor1,
             'creditor': 'EFG456',
             'cls': CreditorInvoice,
             'object_name': 'CreditorInvoice',
             'date': dateparser.parse('02-Jun-2017'),
             'gst_total': utils.make_decimal('$0.29'),
             'invoice_number': 'I38728128',
             'order_number': 'guild house',
             'reference': 'O37688231',
             'source': 'subledgers.creditors.models.CreditorInvoice',
             'value': utils.make_decimal('$217.86'),
             'user': self.user,
             '[15-0151]': '214.65',
             '[15-0155]': '',
             '[15-0301]': '',
             '[15-0305]': '',
             '[15-0608]': '2.92',
             'lines': [
                 (self.a1, utils.set_DR('214.65')),
                 (self.a2, utils.set_DR('2.92')),
                 (self.account_creditors, utils.set_CR('217.86')),
                 (self.account_GST, utils.set_DR('0.29')),
             ],
             },
        ]

        # work around dict mutability when generating line list.
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertSequenceEqual # noqa
        results = Entry.dump_to_kwargs(
            test_input, user=self.user, object_name='CreditorInvoice')
        for x in results:
            x['lines'] = set(x['lines'])
            if x['invoice_number'] == 'I38731476':
                compare = test_result[0]
            else:
                compare = test_result[1]
            compare['lines'] = set(compare['lines'])
            self.assertDictEqual(x, compare)


class TestModelEntryCheckRequired(TestCase):

    def test_check_required_simple_transaction_passes(self):
        test_input = {'date': '02-Jun-2017',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      'lines': [1],
                      'user': 1,
                      'cls': CreditorInvoice,
                      'relation': 1,
                      'object_name': 'BankTransaction',
                      'value': '$485.27'}
        self.assertTrue(Entry.check_required(test_input))

    def test_check_required_normal_transaction_passes(self):
        test_input = {'[15-0151]': '478.12',
                      'source': 'subledgers.creditors.models.CreditorInvoice',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'object_name': 'BankTransaction',
                      'lines': [1],
                      'user': 1,
                      'relation': 1,
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
