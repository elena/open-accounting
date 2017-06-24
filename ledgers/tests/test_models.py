# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase  # , Client

from ledgers.models import Account, Transaction


class TestTransactionSave(TestCase):

    def setUp(self):
        self.date = date(2017, 6, 16)
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()
        self.a1 = Account(element='01', number='0101', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0102', name='Test Account 2')
        self.a2.save()

        # t1_value = Decimal(10)
        # lines = (self.a1, self.a2, t1_value)
        # self.t1 = Transaction(date=self.date, value=0, user=self.user)
        # self.t1.save(lines=lines)

    def test_transaction_new_object_save_no_lines_fails(self):
        new_transaction = Transaction(date=self.date, value=0, user=self.user)
        self.assertRaises(Exception, new_transaction.save)

    def test_transaction_new_object_simple_all_fields_correct(self):
        """ Testing custom save() behaves as expected."""

        test_input = ("01-0101", "01-0102", 5)
        new_obj = Transaction(user=self.user, date=self.date, value=0)
        new_obj.save(test_input)
        self.assertEqual(new_obj.date, self.date)
        self.assertEqual(new_obj.value, Decimal(5))
        self.assertEqual(new_obj.note, "")
        self.assertEqual(new_obj.source, "")
        self.assertEqual(new_obj.user, self.user)
        self.assertEqual(new_obj.is_balanced, True)
        self.assertEqual(new_obj.lines.count(), 2)
        self.assertEqual(new_obj.lines.first().account, self.a1)
        self.assertEqual(new_obj.lines.first().value, 5)
        self.assertEqual(new_obj.lines.first().note, "")
        self.assertEqual(new_obj.lines.last().account, self.a2)
        self.assertEqual(new_obj.lines.last().value, -5)
        self.assertEqual(new_obj.lines.last().note, "")

    def test_transaction_new_object_multi2_all_fields_correct(self):
        """ Testing custom save() behaves as expected."""

        test_input = [
            ("01-0101", 5),
            ("01-0102", -5)
        ]
        new_obj = Transaction(user=self.user, date=self.date, value=0)
        new_obj.save(test_input)
        self.assertEqual(new_obj.date, self.date)
        self.assertEqual(new_obj.value, Decimal(5))
        self.assertEqual(new_obj.note, "")
        self.assertEqual(new_obj.source, "")
        self.assertEqual(new_obj.user, self.user)
        self.assertEqual(new_obj.is_balanced, True)
        self.assertEqual(new_obj.lines.count(), 2)
        self.assertEqual(new_obj.lines.first().account, self.a1)
        self.assertEqual(new_obj.lines.first().value, 5)
        self.assertEqual(new_obj.lines.first().note, "")
        self.assertEqual(new_obj.lines.last().account, self.a2)
        self.assertEqual(new_obj.lines.last().value, -5)
        self.assertEqual(new_obj.lines.last().note, "")

    def test_transaction_new_object_multi3_all_fields_correct(self):
        """ Testing custom save() behaves as expected."""

        test_input = [
            ("01-0101", -5),
            ("01-0102", -5),
            ("01-0101", 10),
        ]
        new_obj = Transaction(user=self.user, date=self.date, value=0)
        new_obj.save(test_input)
        self.assertEqual(new_obj.date, self.date)
        self.assertEqual(new_obj.value, Decimal(10))
        self.assertEqual(new_obj.note, "")
        self.assertEqual(new_obj.source, "")
        self.assertEqual(new_obj.user, self.user)
        self.assertEqual(new_obj.is_balanced, True)
        self.assertEqual(new_obj.lines.count(), 3)
        self.assertEqual(new_obj.lines.first().account, self.a1)
        self.assertEqual(new_obj.lines.first().value, -5)
        self.assertEqual(new_obj.lines.first().note, "")
        self.assertEqual(new_obj.lines.last().account, self.a1)
        self.assertEqual(new_obj.lines.last().value, 10)
        self.assertEqual(new_obj.lines.last().note, "")


class TestTransactionCheckIsBalanced(TestCase):

    """ Test a bunch of random object types and formats for outcomes. """

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()
        self.a1 = Account(element='01', number='0101', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0102', name='Test Account 2')
        self.a2.save()

        t1_value = Decimal(10)
        lines = (self.a1, self.a2, t1_value)
        self.t1 = Transaction(date=date(2017, 6, 16), value=0, user=self.user)
        self.t1.save(lines=lines)

    def test_transaction_check_is_balanced_fails(self):
        broken_line = self.t1.lines.first()
        broken_line.value = 10000
        broken_line.save()
        self.assertEqual(self.t1.is_balanced, False)


class TestTransactionLineValidationMultilineFailures(TestCase):

    """ Test a bunch of random object types and formats for outcomes. """

    def setUp(self):
        self.a1 = Account(element='01', number='0101', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0102', name='Test Account 2')
        self.a2.save()
        self.a3 = Account(element='01', number='0103', name='Test Account 3')
        self.a3.save()

    def test_transaction_line_validation_multi_zero_list_fails(self):
        # Nothing
        test_input = [
            ()
        ]
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_multi_zero_tuple_fails(self):
        # Nothing
        test_input = (
            (),
        )
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_multi_single_fails(self):
        # Nothing
        test_input = [
            ("01-0101", 5)
        ]
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_multi_no_bal2_fails(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", 5)
        ]
        self.assertRaises(Exception, Transaction.line_validation, test_input)
        # self.assertEqual(Transaction.line_validation(test_input), None)

    def test_transaction_line_validation_multi_no_bal3_fails(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", 5),
            ("01-0102", -5)
        ]
        self.assertRaises(Exception, Transaction.line_validation, test_input)
        # self.assertEqual(Transaction.line_validation(test_input), None)

    def test_transaction_line_validation_multi_account_fails(self):
        test_input = [
            ("01-0000", 5),
            ("01-0102", 5)
        ]
        self.assertRaises(Exception, Transaction.line_validation, test_input)
        # self.assertEqual(Transaction.line_validation(test_input), None)


class TestTransactionLineValidationMultilinePasses(TestCase):

    """ Test successful cases."""

    def setUp(self):
        self.a1 = Account(element='01', number='0101', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0102', name='Test Account 2')
        self.a2.save()
        self.a3 = Account(element='01', number='0103', name='Test Account 3')
        self.a3.save()

    def test_transaction_line_validation_multi_simple_passes(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", -5)
        ]
        test_result = [Decimal(5),
                       [{'account': self.a1, 'value': Decimal(5)},
                        {'account': self.a2, 'value': Decimal(-5)}
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_note1_passes(self):
        test_input = [
            ("01-0101", 5, "A notation"),
            ("01-0102", -5)
        ]
        test_result = [Decimal(5),
                       [{'account': self.a1, 'value': Decimal(5), 'note': 'A notation'},
                        {'account': self.a2, 'value': Decimal(-5)}
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_note2_passes(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", -5, "A notation")
        ]
        test_result = [Decimal(5),
                       [{'account': self.a1, 'value': Decimal(5)},
                        {'account': self.a2,
                         'value': Decimal(-5), 'note': 'A notation'},
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_note_both_passes(self):
        test_input = [
            ("01-0101", 5, "A notation"),
            ("01-0102", -5, "Another notation")
        ]
        test_result = [Decimal(5),
                       [{'account': self.a1, 'value': Decimal(5), 'note': 'A notation'},
                        {'account': self.a2,
                         'value': Decimal(-5), 'note': 'Another notation'},
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_same_passes(self):
        # have repeated same account is allowed in multi situation
        test_input = [
            ("01-0101", -5),
            ("01-0101", -5),
            ("01-0101", 10)
        ]
        test_result = [Decimal(10),
                       [{'account': self.a1, 'value': Decimal(-5)},
                        {'account': self.a1, 'value': Decimal(-5)},
                        {'account': self.a1, 'value': Decimal(10)}
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_list_passes(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", 5),
            ("01-0103", -10)
        ]
        test_result = [Decimal(10),
                       [{'account': self.a1, 'value': Decimal(5)},
                        {'account': self.a2, 'value': Decimal(5)},
                        {'account': self.a3, 'value': Decimal(-10)},
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_tuple_passes(self):
        test_input = (
            ("01-0101", 5),
            ("01-0102", 5),
            ("01-0103", -10)
        )
        test_result = [Decimal(10),
                       [{'account': self.a1, 'value': Decimal(5)},
                        {'account': self.a2, 'value': Decimal(5)},
                        {'account': self.a3, 'value': Decimal(-10)},
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_multi_none_passes(self):
        test_input = [
            ("01-0101", 5),
            ("01-0102", 5),
            ("01-0103", -10),
            ("01-0101", -5),
            ("01-0102", -5),
            ("01-0103", 10)
        ]
        test_result = [Decimal(20),
                       [{'account': self.a1, 'value': Decimal(5)},
                        {'account': self.a2, 'value': Decimal(5)},
                        {'account': self.a3, 'value': Decimal(-10)},
                        {'account': self.a1, 'value': Decimal(-5)},
                        {'account': self.a2, 'value': Decimal(-5)},
                        {'account': self.a3, 'value': Decimal(10)},
                        ]]
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)


class TestTransactionLineValidationSimpleFailures(TestCase):

    """ Test a bunch of random object types and formats for outcomes. """

    def setUp(self):
        self.a1 = Account(element='01', number='0100', name='Test Account 1')
        self.a1.save()
        self.a2 = Account(element='01', number='0101', name='Test Account 2')
        self.a2.save()

    def test_transaction_line_validation_simple_none_fails(self):
        # Nothing
        test_input = None
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_empty_fails(self):
        # Pretty much nothing
        test_input = ()
        self.assertRaises(Exception, Transaction.line_validation, test_input)

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
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_layout_nan_fails(self):
        # Correct layout incorrect obj types
        test_input = (self.a1, self.a2, "")
        self.assertRaises(Exception, Transaction.line_validation, test_input)

    def test_transaction_line_validation_simple_dup_fails(self):
        # Correct layout incorrect obj types
        test_input = (self.a1, self.a1, 5)
        self.assertRaises(Exception, Transaction.line_validation, test_input)


class TestTransactionLineValidationSimplePasses(TestCase):
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
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_sox_input_passes(self):
        test_input = (self.a1, "01-0101", 5)
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_osx_input_passes(self):
        test_input = ("01-0100", self.a2, 5)
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_oox_input_passes(self):
        test_input = (self.a1, self.a2, Decimal('5'))
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    # Check `value` variations

    def test_transaction_line_validation_simple_xxs_input_passes(self):
        test_input = ("01-0100", "01-0101", '5')
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_xxd_input_passes(self):
        test_input = ("01-0100", "01-0101", Decimal(5))
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)

    def test_transaction_line_validation_simple_xxi_input_passes(self):
        test_input = ("01-0100", "01-0101", int(5))
        test_result = (5, [{'account': self.a1, 'value': 5},
                           {'account': self.a2, 'value': -5}])
        self.assertEqual(Transaction.line_validation(test_input),
                         test_result)
