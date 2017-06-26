from django.test import TestCase

from .models import CurrentFinancialYear


class TestCurrrentFinancialYear(TestCase):

    def setUp(self):
        self.fy1 = 'F15'
        self.fy2 = 'F16'

    def test_new_current_fy_single_passes(self):
        CurrentFinancialYear.objects.create(current_financial_year=self.fy1)
        self.assertEqual(CurrentFinancialYear.objects.count(), 1)
        self.assertEqual(CurrentFinancialYear.objects.get(
        ).current_financial_year, self.fy1)

    def test_new_current_fy_multiple_passes(self):
        CurrentFinancialYear.objects.create(current_financial_year=self.fy1)
        CurrentFinancialYear.objects.create(current_financial_year=self.fy2)
        self.assertEqual(CurrentFinancialYear.objects.count(), 1)
        self.assertEqual(CurrentFinancialYear.objects.get(
        ).current_financial_year, self.fy2)

    def test_new_current_fy_multiple2_passes(self):
        CurrentFinancialYear.objects.create(current_financial_year=self.fy1)
        CurrentFinancialYear.objects.create(current_financial_year=self.fy2)
        CurrentFinancialYear.objects.create(current_financial_year=self.fy1)
        self.assertEqual(CurrentFinancialYear.objects.count(), 1)
        self.assertEqual(CurrentFinancialYear.objects.get(
        ).current_financial_year, self.fy1)
