# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from ledgers.models import Account, Transaction, Line


class TestLineQueryset(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test_staff_user', 'test@example.com', '1234')
        self.user.is_staff = True
        self.user.save()

        self.a1 = Account.objects.create(
            element='01', number='0101', name='Test Bank Account 1')
        self.a2 = Account.objects.create(
            element='15', number='0501', name='Test Expenses Account 1')

        self.v1, self.v2, self.v3 = Decimal(10), Decimal(-15), Decimal(5)
        self.year = settings.FINANCIAL_YEARS['F16']

        # this year
        self.d1 = date(2016, 6, 16)
        self.t1 = Transaction(date=self.d1, value=0, user=self.user)
        l = [(self.a1, self.v1),
             (self.a1, self.v2),
             (self.a2, self.v3), ]
        self.t1.save(lines=l)
        self.l1 = Line.objects.get(
            transaction=self.t1, account=self.a1, value=self.v1)
        self.l2 = Line.objects.get(
            transaction=self.t1, account=self.a1, value=self.v2)
        self.l3 = Line.objects.get(
            transaction=self.t1, account=self.a2, value=self.v3)

        # last year
        self.d2 = date(2015, 6, 16)
        self.tl1 = Transaction(date=date(2015, 6, 16), value=0, user=self.user)
        l = [(self.a1, self.v1),
             (self.a1, self.v2),
             (self.a2, self.v3), ]
        self.tl1.save(lines=l)
        self.ll1 = Line.objects.get(
            transaction=self.tl1, account=self.a1, value=self.v1)
        self.ll2 = Line.objects.get(
            transaction=self.tl1, account=self.a1, value=self.v2)
        self.ll3 = Line.objects.get(
            transaction=self.tl1, account=self.a2, value=self.v3)

        # next year
        self.tn1 = Transaction(date=date(2017, 6, 16), value=0, user=self.user)
        l = [(self.a1, self.v1),
             (self.a1, self.v2),
             (self.a2, self.v3), ]
        self.tn1.save(lines=l)
        self.ln1 = Line.objects.get(
            transaction=self.tn1, account=self.a1, value=self.v1)
        self.ln2 = Line.objects.get(
            transaction=self.tn1, account=self.a1, value=self.v2)
        self.ln3 = Line.objects.get(
            transaction=self.tn1, account=self.a2, value=self.v3)

    def test_line_queryset_day1_passes(self):

        obj_list = Line.objects.day(self.d1)

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_month_passes(self):

        obj_list = Line.objects.month('2016-06')

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_month_none_passes(self):

        obj_list = Line.objects.month('2016-05')

        self.assertEqual(obj_list.count(), 0)
        self.assertNotIn(self.l1, obj_list)
        self.assertNotIn(self.l2, obj_list)
        self.assertNotIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_fyear_last_range_passes(self):

        obj_list = Line.objects.fyear('F15')

        self.assertEqual(obj_list.count(), 3)
        self.assertNotIn(self.l1, obj_list)
        self.assertNotIn(self.l2, obj_list)
        self.assertNotIn(self.l3, obj_list)
        self.assertIn(self.ll1, obj_list)
        self.assertIn(self.ll2, obj_list)
        self.assertIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_fyear_next_range_passes(self):

        obj_list = Line.objects.fyear('F17')

        self.assertEqual(obj_list.count(), 3)
        self.assertNotIn(self.l1, obj_list)
        self.assertNotIn(self.l2, obj_list)
        self.assertNotIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertIn(self.ln1, obj_list)
        self.assertIn(self.ln2, obj_list)
        self.assertIn(self.ln3, obj_list)

    def test_line_queryset_date_range1_passes(self):

        obj_list = Line.objects.range(
            date(2016, 6, 15),
            date(2016, 6, 17)
        )

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_date_range2_passes(self):

        obj_list = Line.objects.range(
            date(2016, 6, 15),
            date(2016, 6, 16)
        )

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_date_range3_passes(self):

        obj_list = Line.objects.range(
            date(2016, 6, 16),
            date(2016, 6, 17)
        )

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)

    def test_line_queryset_date_range4_passes(self):

        obj_list = Line.objects.range(
            date(2016, 6, 16),
            date(2016, 6, 16)
        )

        self.assertEqual(obj_list.count(), 3)
        self.assertIn(self.l1, obj_list)
        self.assertIn(self.l2, obj_list)
        self.assertIn(self.l3, obj_list)
        self.assertNotIn(self.ll1, obj_list)
        self.assertNotIn(self.ll2, obj_list)
        self.assertNotIn(self.ll3, obj_list)
        self.assertNotIn(self.ln1, obj_list)
        self.assertNotIn(self.ln2, obj_list)
        self.assertNotIn(self.ln3, obj_list)
