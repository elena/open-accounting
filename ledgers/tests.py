# -*- coding: utf-8 -*-
import warnings
import unittest
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, Client

from .models import Account, Transaction, Line


class TestTransactionLineValidationFailures(TestCase):

    def setUp(self):
        self.a1 = Account(element='01', number='0100', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0101', name='Test Account 2')
        self.a2.save()

    def test_transaction_line_validation_simple_none_fails(self):
        # Nothing
        test_input = None
        self.assertEqual(Transaction.line_validation(test_input), None)

    def test_transaction_line_validation_simple_empty_fails(self):
        # Pretty much nothing
        test_input = ()
        self.assertEqual(Transaction.line_validation(test_input), None)

    def test_transaction_line_validation_simple_layout_fails(self):
        # Correct layout incorrect obj types
        test_input = ("", "", "")
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_layout_type_fails(self):
        # Correct layout incorrect obj types
        test_input = (Transaction, "", 0)
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_layout_obj_fails(self):
        # Correct layout incorrect obj types
        test_input = (Account, "", 0)
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_layout_incomplete_fails(self):
        # Correct layout incorrect obj types
        test_input = (self.a1, "", 0)
        self.assertEqual(Transaction.line_validation(test_input), None)

    def test_transaction_line_validation_simple_layout_nan_fails(self):
        # Correct layout incorrect obj types
        test_input = (self.a1, self.a2, "")
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_dup_fails(self):
        # Correct layout incorrect obj types
        test_input = (self.a1, self.a1, 5)
        self.assertEqual(Transaction.line_validation(test_input), None)


class TestTransactionLineValidationPasses(TestCase):
    """ All correct permuations:
    (s, s, x) -- test `Account` str/obj input perms
    (s, o, x)
    (o, s, x)
    (o, o, x)

    (x, x, s) -- test `value` str/obj/Decimal input perms
    (x, x, d)
    (x, x, i)
    """

    def setUp(self):
        self.a1 = Account(element='01', number='0100', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0101', name='Test Account 2')
        self.a2.save()

    # check `Account`variations

    def test_transaction_line_validation_simple_ssx_input_passes(self):
        test_input = ("01-0100", "01-0101", 5)
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_sox_input_passes(self):
        test_input = (self.a1, "01-0101", 5)
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_osx_input_passes(self):
        test_input = ("01-0100", self.a2, 5)
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_oox_input_passes(self):
        test_input = (self.a1, self.a2, Decimal('5'))
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    # Check `value` variations

    def test_transaction_line_validation_simple_xxs_input_passes(self):
        test_input = ("01-0100", "01-0101", '5')
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_xxd_input_passes(self):
        test_input = ("01-0100", "01-0101", Decimal(5))
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_xxi_input_passes(self):
        test_input = ("01-0100", "01-0101", int(5))
        test_result = (5, {'account': self.a1, 'value': 5},
                          {'account': self.a2, 'value': -5})
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)
