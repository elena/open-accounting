# -*- coding: utf-8 -*-
import dateparser
from django.contrib.auth.models import User
from django.test import TestCase  # , Client

from subledgers import utils
from subledgers.creditors.models import CreditorInvoice
from entities.models import Entity
from ledgers.models import Account, Transaction, Line
from subledgers import settings
from subledgers.creditors.models import Creditor


class TestUtilsCreateObject(TestCase):

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

    def test_create_object_single_passes(self):

        # create based upon dump
        test_input = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA
        test_create_object = utils.create_objects(
            utils.dump_to_kwargs(test_input,
                                 user=self.user,
                                 object_name='CreditorInvoice'))

        # try to get objects that look exactly correct
        test_transaction = Transaction.objects.get(
            value=utils.make_decimal('$485.27'),
            date=dateparser.parse('02-Jun-2017'),
            source='subledgers.creditors.CreditorInvoice',
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

    def test_create_object_single_rubbish_list_failure(self):

        test_kwargs_list = ['asfd']
        self.assertRaises(Exception, utils.create_objects, test_kwargs_list)

    def test_create_object_single_incomplete_kwarg_failure(self):

        test_kwargs_list = [{'relation': self.creditor0,
                             # 'object': 'CreditorInvoice', # no object failure
                             'date': dateparser.parse('02-Jun-2017'),
                             'gst_total': utils.make_decimal('$0.65'),
                             'invoice_number': 'I38731476',
                             'order_number': 'guild house',
                             'reference': 'O37696095',
                             'source': 'subledgers.creditors.CreditorInvoice',
                             'value': utils.make_decimal('$485.27'),
                             'user': self.user,
                             'lines': [
                                 (self.a1, utils.set_DR('478.12')),
                                 (self.a2, utils.set_DR('6.5')),
                                 (self.account_creditors, utils.set_CR('485.27')),  # noqa
                                 (self.account_GST, utils.set_DR('0.65')),
                             ]}, ]
        self.assertRaises(Exception, utils.create_objects, test_kwargs_list)


class TestUtilsImportDump(TestCase):

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
        test_result = [{'relation': self.creditor0,
                        'creditor': 'BIDVES',
                        'object_name': 'CreditorInvoice',
                        'date': dateparser.parse('02-Jun-2017'),
                        'gst_total': utils.make_decimal('$0.65'),
                        'invoice_number': 'I38731476',
                        'order_number': 'guild house',
                        'reference': 'O37696095',
                        'source': 'subledgers.creditors.CreditorInvoice',
                        'user': self.user,
                        'value': utils.make_decimal('$485.27')},
                       {'relation': self.creditor1,
                        'creditor': 'EFG456',
                        'object_name': 'CreditorInvoice',
                        'date': dateparser.parse('02-Jun-2017'),
                        'gst_total': utils.make_decimal('$0.29'),
                        'invoice_number': 'I38728128',
                        'order_number': 'guild house',
                        'reference': 'O37688231',
                        'source': 'subledgers.creditors.CreditorInvoice',
                        'user': self.user,
                        'value': utils.make_decimal('$217.86')},
                       ]

        results = utils.dump_to_kwargs(
            test_input, self.user, 'CreditorInvoice')
        for i, x in enumerate(test_result):
            results[i].pop('lines')
            self.assertDictEqual(x, results[i])

    def test_dump_to_kwargs_invoice_double_passes(self):
        test_input = "creditor\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t\r\nEFG456\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house\t2.92\t214.65\t\t\t"
        test_result = [{'relation': self.creditor0,
                        # @@ TODO could clean up this relic. not important.
                        'creditor': 'BIDVES',
                        'object_name': 'CreditorInvoice',
                        'date': dateparser.parse('02-Jun-2017'),
                        'gst_total': utils.make_decimal('$0.65'),
                        'invoice_number': 'I38731476',
                        'order_number': 'guild house',
                        'reference': 'O37696095',
                        'source': 'subledgers.creditors.CreditorInvoice',
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
                        'object_name': 'CreditorInvoice',
                        'date': dateparser.parse('02-Jun-2017'),
                        'gst_total': utils.make_decimal('$0.29'),
                        'invoice_number': 'I38728128',
                        'order_number': 'guild house',
                        'reference': 'O37688231',
                        'source': 'subledgers.creditors.CreditorInvoice',
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
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertSequenceEqual
        results = utils.dump_to_kwargs(
            test_input, user=self.user, object_name='CreditorInvoice')
        for x in results:
            # for k, v in x.items():
            #     print("{}: {}".format(k, v))
            x['lines'] = set(x['lines'])
            if x['invoice_number'] == 'I38731476':
                compare = test_result[0]
            else:
                compare = test_result[1]
            compare['lines'] = set(compare['lines'])
            self.assertDictEqual(x, compare)


class TestUtilsGetRelation(TestCase):

    def setUp(self):
        self.entity0 = Entity.objects.create(name="abc")
        self.entity1 = Entity.objects.create(name="abc123")
        self.entity2 = Entity.objects.create(name="efg4")

        self.creditor1 = Creditor.objects.create(
            entity=self.entity1)

    def test_get_relation_failure(self):
        self.assertRaises(TypeError, utils.get_relation, 'nothing')

    def test_get_relation_no_entity_failure(self):
        self.assertRaises(Exception, utils.get_relation,
                          'nothing', 'CreditorInvoice')

    def test_get_relation_valid_entity_passes(self):
        creditor0 = Creditor.objects.create(entity=self.entity0)
        self.assertEqual(utils.get_relation(
            self.entity0.code, 'CreditorInvoice'), creditor0)

    def test_get_relation_valid_creditor_passes(self):
        self.assertEqual(utils.get_relation(
            self.entity1.code, 'CreditorInvoice'), self.creditor1)

    def test_get_relation_valid_entity_not_creditor_failure(self):
        self.assertNotEqual(utils.get_relation(
            self.entity0.code, 'CreditorInvoice'), self.creditor1)


class TestUtilsCheckRequired(TestCase):

    def test_check_required_simple_transaction_passes(self):
        test_input = {'date': '02-Jun-2017',
                      'value': '$485.27'}
        self.assertTrue(utils.check_required(
            test_input, object_name='BankTransaction'))

    def test_check_required_normal_transaction_passes(self):
        test_input = {'[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'date': '02-Jun-2017',
                      'value': '$485.27'}
        self.assertTrue(utils.check_required(
            test_input, object_name='BankTransaction'))

    def test_check_required_single_transaction_failure(self):
        test_input = {'[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'value': '$485.27'}
        self.assertRaises(Exception, utils.check_required,
                          test_input, 'journals')

    def test_check_required_multiple_transaction_failure(self):
        test_input = {'[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5'}
        self.assertRaises(Exception, utils.check_required,
                          test_input, 'journals')

    def test_check_required_normal_invoice_passes(self):
        test_input = {'creditor': 'BIDVES',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertTrue(utils.check_required(test_input, 'CreditorInvoice'))

    def test_check_required_single_invoice_failure(self):
        test_input = {"'creditor__entity__code": 'BIDVES',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'gst_total': '$0.65',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertRaises(Exception, utils.check_required,
                          test_input, 'CreditorInvoice')

    def test_check_required_multiple_invoice_failure(self):
        test_input = {'creditor': 'BIDVES',
                      '[15-0151]': '478.12',
                      '[15-0155]': '',
                      '[15-0301]': '',
                      '[15-0305]': '',
                      '[15-0608]': '6.5',
                      'invoice_number': 'I38731476',
                      'order_number': 'guild house',
                      'reference': 'O37696095',
                      'value': '$485.27'}
        self.assertRaises(Exception, utils.check_required,
                          test_input, 'CreditorInvoice')

    def test_check_required_simple_invoice_passes(self):
        test_input = {'creditor': 'BIDVES',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'invoice_number': 'I38731476',
                      'value': '$485.27'}

        self.assertTrue(utils.check_required(test_input, 'CreditorInvoice'))

    def test_check_required_simple_entity_invoice_passes(self):
        test_input = {'entity': 'BIDVES',
                      'date': '02-Jun-2017',
                      'gst_total': '$0.65',
                      'invoice_number': 'I38731476',
                      'value': '$485.27'}

        self.assertTrue(utils.check_required(test_input, 'CreditorInvoice'))


class TestUtilsTsvToDict(TestCase):

    def test_tsv_to_dict_failure(self):
        test_input = "asdfsad"
        self.assertRaises(Exception, utils.tsv_to_dict(test_input))

    def test_tsv_to_dict_single_passes(self):
        test_input = "'creditor__entity__code\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t"  # NOQA
        test_result = [{"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '478.12',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '6.5',
                        'date': '02-Jun-2017',
                        'gst_total': '$0.65',
                        'invoice_number': 'I38731476',
                        'order_number': 'guild house',
                        'reference': 'O37696095',
                        'value': '$485.27'},
                       ]
        self.assertEqual(utils.tsv_to_dict(test_input), test_result)

    def test_tsv_to_dict_double_passes(self):
        test_input = "'creditor__entity__code\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t\r\nBIDVES\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house\t2.92\t214.65\t\t\t"  # NOQA
        test_result = [{"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '478.12',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '6.5',
                        'date': '02-Jun-2017',
                        'gst_total': '$0.65',
                        'invoice_number': 'I38731476',
                        'order_number': 'guild house',
                        'reference': 'O37696095',
                        'value': '$485.27'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '214.65',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '2.92',
                        'date': '02-Jun-2017',
                        'gst_total': '$0.29',
                        'invoice_number': 'I38728128',
                        'order_number': 'guild house',
                        'reference': 'O37688231',
                        'value': '$217.86'},
                       ]
        self.assertEqual(utils.tsv_to_dict(test_input), test_result)

    def test_tsv_to_dict_normal_passes(self):
        # @@ TODO make this less unweildly
        # as unlikely as it seems this was the easiest test to write today (the one I had handy)

        test_input = "'creditor__entity__code\tdate\tinvoice_number\treference\tvalue\tgst_total\torder_number\t[15-0608]\t[15-0151]\t[15-0155]\t[15-0301]\t[15-0305]\r\nBIDVES\t02-Jun-2017\tI38731476\tO37696095\t$485.27\t$0.65\tguild house\t6.5\t478.12\t\t\t\r\nBIDVES\t02-Jun-2017\tI38728128\tO37688231\t$217.86\t$0.29\tguild house\t2.92\t214.65\t\t\t\r\nBIDVES\t01-Jun-2017\tI38712244\tO37673162\t$415.92\t$2.50\tguild house\t5.55\t407.87\t\t\t\r\nBIDVES\t29-May-2017\tI38675121\tO37635503\t$1,250.80\t$19.31\tguild house\t16.52\t1214.97\t\t\t\r\nBIDVES\t26-May-2017\tI38662854\tO37628074\t$380.67\t$0.51\tguild house\t5.1\t375.06\t\t\t\r\nBIDVES\t23-May-2017\tI38618750\tO37582526\t$352.85\t$2.41\tguild house\t4.7\t345.74\t\t\t\r\nBIDVES\t19-May-2017\tI38593473\tO37560909\t$373.32\t$3.75\tguild house\t4.96\t364.61\t\t\t\r\nBIDVES\t19-May-2017\tI38590107\tO37552929\t$340.23\t$0.46\tguild house\t4.56\t296.19\t39.02\t\t\r\nBIDVES\t18-May-2017\tI38573973\tO37538304\t$180.01\t$0.24\tguild house\t2.41\t177.36\t\t\t\r\nBIDVES\t17-May-2017\tI38561177\tO37526323\t$290.69\t$2.33\tGuild house\t3.87\t284.49\t\t\t\r\nBIDVES\t16-May-2017\tI38548235\tO37514613\t$574.63\t$0.77\tGuild house\t7.7\t566.16\t\t\t\r\nBIDVES\t15-May-2017\tI38535465\tO37500532\t$146.69\t$2.13\tguild house\t1.94\t142.62\t\t\t\r\nBIDVES\t12-May-2017\tI38523300\tO37492513\t$406.79\t$0.55\tGuild house\t5.45\t400.79\t\t\t\r\nBIDVES\t11-May-2017\tI38503207\tO37469025\t$276.93\t$2.31\tGuild house\t3.68\t270.94\t\t\t\r\nBIDVES\t10-May-2017\tI38489831\tO37456505\t$353.49\t$0.47\tGuild house\t4.74\t348.28\t\t\t\r\nBIDVES\t08-May-2017\tI38463891\tO37430285\t$283.19\t$2.35\tguild house\t3.77\t237.65\t39.42\t\t"  # NOQA
        test_result = [{"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '478.12',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '6.5',
                        'date': '02-Jun-2017',
                        'gst_total': '$0.65',
                        'invoice_number': 'I38731476',
                        'order_number': 'guild house',
                        'reference': 'O37696095',
                        'value': '$485.27'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '214.65',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '2.92',
                        'date': '02-Jun-2017',
                        'gst_total': '$0.29',
                        'invoice_number': 'I38728128',
                        'order_number': 'guild house',
                        'reference': 'O37688231',
                        'value': '$217.86'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '407.87',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '5.55',
                        'date': '01-Jun-2017',
                        'gst_total': '$2.50',
                        'invoice_number': 'I38712244',
                        'order_number': 'guild house',
                        'reference': 'O37673162',
                        'value': '$415.92'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '1214.97',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '16.52',
                        'date': '29-May-2017',
                        'gst_total': '$19.31',
                        'invoice_number': 'I38675121',
                        'order_number': 'guild house',
                        'reference': 'O37635503',
                        'value': '$1,250.80'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '375.06',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '5.1',
                        'date': '26-May-2017',
                        'gst_total': '$0.51',
                        'invoice_number': 'I38662854',
                        'order_number': 'guild house',
                        'reference': 'O37628074',
                        'value': '$380.67'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '345.74',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '4.7',
                        'date': '23-May-2017',
                        'gst_total': '$2.41',
                        'invoice_number': 'I38618750',
                        'order_number': 'guild house',
                        'reference': 'O37582526',
                        'value': '$352.85'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '364.61',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '4.96',
                        'date': '19-May-2017',
                        'gst_total': '$3.75',
                        'invoice_number': 'I38593473',
                        'order_number': 'guild house',
                        'reference': 'O37560909',
                        'value': '$373.32'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '296.19',
                        '[15-0155]': '39.02',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '4.56',
                        'date': '19-May-2017',
                        'gst_total': '$0.46',
                        'invoice_number': 'I38590107',
                        'order_number': 'guild house',
                        'reference': 'O37552929',
                        'value': '$340.23'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '177.36',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '2.41',
                        'date': '18-May-2017',
                        'gst_total': '$0.24',
                        'invoice_number': 'I38573973',
                        'order_number': 'guild house',
                        'reference': 'O37538304',
                        'value': '$180.01'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '284.49',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '3.87',
                        'date': '17-May-2017',
                        'gst_total': '$2.33',
                        'invoice_number': 'I38561177',
                        'order_number': 'Guild house',
                        'reference': 'O37526323',
                        'value': '$290.69'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '566.16',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '7.7',
                        'date': '16-May-2017',
                        'gst_total': '$0.77',
                        'invoice_number': 'I38548235',
                        'order_number': 'Guild house',
                        'reference': 'O37514613',
                        'value': '$574.63'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '142.62',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '1.94',
                        'date': '15-May-2017',
                        'gst_total': '$2.13',
                        'invoice_number': 'I38535465',
                        'order_number': 'guild house',
                        'reference': 'O37500532',
                        'value': '$146.69'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '400.79',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '5.45',
                        'date': '12-May-2017',
                        'gst_total': '$0.55',
                        'invoice_number': 'I38523300',
                        'order_number': 'Guild house',
                        'reference': 'O37492513',
                        'value': '$406.79'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '270.94',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '3.68',
                        'date': '11-May-2017',
                        'gst_total': '$2.31',
                        'invoice_number': 'I38503207',
                        'order_number': 'Guild house',
                        'reference': 'O37469025',
                        'value': '$276.93'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '348.28',
                        '[15-0155]': '',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '4.74',
                        'date': '10-May-2017',
                        'gst_total': '$0.47',
                        'invoice_number': 'I38489831',
                        'order_number': 'Guild house',
                        'reference': 'O37456505',
                        'value': '$353.49'},
                       {"'creditor__entity__code": 'BIDVES',
                        '[15-0151]': '237.65',
                        '[15-0155]': '39.42',
                        '[15-0301]': '',
                        '[15-0305]': '',
                        '[15-0608]': '3.77',
                        'date': '08-May-2017',
                        'gst_total': '$2.35',
                        'invoice_number': 'I38463891',
                        'order_number': 'guild house',
                        'reference': 'O37430285',
                        'value': '$283.19'},
                       ]

        self.assertEqual(utils.tsv_to_dict(test_input), test_result)
