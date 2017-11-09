# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
from decimal import Decimal

from django.test import TestCase  # , Client

from ledgers.models import Account
from ledgers import utils


class TestUtilsMakeDate(TestCase, unittest.TestCase):

    def test_make_date_not_date_failure(self):
        test_input = "asdf"
        # @@ bit inconsistent .. could be better.
        self.assertEqual(utils.make_date(test_input), None)

    def test_make_date_iso8601_failure(self):
        test_input = "2017-05-02"
        self.assertRaises(Exception, utils.make_date, test_input)

    def test_make_date_usa_failure(self):
        test_input = "2017-02-05"
        self.assertRaises(Exception, utils.make_date, test_input)

    # # @@ TODO limit range to this era
    # def test_make_date_close_invalid_failure(self):
    #     test_input = "2017-May-50"
    #     self.assertRaises(Exception, utils.make_date, test_input)

    def test_make_date_normal_passes(self):
        test_input = "2-May-2017"
        test_result = datetime(2017, 5, 2, 0, 0)
        self.assertEqual(utils.make_date(test_input), test_result)

    def test_make_date_nearly_normal_passes(self):
        test_input = "2017-May-2"
        test_result = datetime(2017, 5, 2, 0, 0)
        self.assertEqual(utils.make_date(test_input), test_result)

    def test_make_date_nearly_normal2_passes(self):
        test_input = "Thursday, 2nd May 2017"
        test_result = datetime(2017, 5, 2, 0, 0)
        self.assertEqual(utils.make_date(test_input), test_result)


class TestUtilsGetSource(TestCase, unittest.TestCase):

    def test_get_source_Obj_passes(self):
        test_input = Account
        test_result = "ledgers.models.Account"
        self.assertEqual(utils.get_source(test_input), test_result)

    def test_get_source_Obj_instance_passes(self):
        test_input = Account()
        test_result = "ledgers.models.Account"
        self.assertEqual(utils.get_source(test_input), test_result)

    def test_get_source_Obj_object_passes(self):
        Account.objects.create(element="01", number="0001")
        test_input = Account.objects.first()
        test_result = "ledgers.models.Account"
        self.assertEqual(utils.get_source(test_input), test_result)

    def test_get_source_str_passes(self):
        test_input = 'ledgers.models.Account'
        test_result = "ledgers.models.Account"
        self.assertEqual(utils.get_source(test_input), test_result)

    def test_get_source_failure(self):
        test_input = "Account"
        self.assertRaises(ImportError, utils.get_source, test_input)


class TestUtilsMakeDecimal(TestCase, unittest.TestCase):

    def test_make_decimal_str_num_passes(self):
        test_input = "5"
        test_result = Decimal('5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_int_passes(self):
        test_input = int(5)
        test_result = Decimal('5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_Decimal_passes(self):
        test_input = Decimal(5)
        test_result = Decimal('5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_neg_passes(self):
        test_input = -5
        test_result = Decimal('-5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_neg_Dec_passes(self):
        test_input = Decimal(-5)
        test_result = Decimal('-5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_neg_str_passes(self):
        test_input = '-5'
        test_result = Decimal('-5.00')
        self.assertEqual(utils.make_decimal(test_input), test_result)

    def test_make_decimal_str_alpha_failure(self):
        test_input = "asdf"
        self.assertRaises(Exception, utils.make_decimal, test_input)


class TestUtilsTsvToDict(TestCase):

    def test_tsv_to_dict_rubbish_input_failure(self):
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
