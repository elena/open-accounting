# -*- coding: utf-8 -*-
from approx_dates.models import ApproxDate

from django.db import models
from django.db.models import Sum
from ledgers.periods import settings
from ledgers.periods.models import CurrentFinancialYear


class AccountQuerySet(models.query.QuerySet):

    def special(self):
        return self.exclude(special_account=None)

    def regular(self):
        return self.filter(special_account=None)

    def by_code(self, code):
        try:
            element, number = code.split("-")
            return self.filter(element=element, number=number).first()
        except ValueError:
            return self.none()

    # @@ TODO add tests for remainder of Account qs

    def range(self, start=None, end=None):
        return self.filter(lines__transaction__date__range=(start, end))

    def day(self, day):
        return self.filter(lines__transaction__date=day)

    def month(self, month):
        approx_date = ApproxDate.from_iso8601(month)
        return self.filter(lines__transaction__date__range=(
            approx_date.earliest_date,
            approx_date.latest_date))

    def fyear(self, fyear=None):
        if not fyear:
            fyear = CurrentFinancialYear.objects.get()
        return self.filter(lines__transaction__date__range=(
            settings.FINANCIAL_YEARS[fyear]))

    def total(self):
        return self.annotate(total=Sum('lines__value'))


class LineQuerySet(models.query.QuerySet):
    def range(self, start=None, end=None):
        return self.filter(transaction__date__range=(start, end))

    def day(self, day):
        return self.filter(transaction__date=day)

    def month(self, month):
        approx_date = ApproxDate.from_iso8601(month)
        return self.filter(transaction__date__range=(
            approx_date.earliest_date,
            approx_date.latest_date))

    def fyear(self, fyear=None):
        if not fyear:
            fyear = CurrentFinancialYear.objects.get()
        return self.filter(transaction__date__range=(
            settings.FINANCIAL_YEARS[fyear]))
