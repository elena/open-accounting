# -*- coding: utf-8 -*-
from approx_dates.models import ApproxDate

from django.conf import settings
from django.db import models


class AccountQuerySet(models.query.QuerySet):

    def special(self):
        return self.exclude(special_account=None)

    def regular(self):
        return self.filter(special_account=None)

    def by_code(self, code):
        element, number = code.split("-")
        return self.filter(element=element, number=number).first()


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

    def fyear(self, fyear=settings.CURRENT_FYEAR):
        return self.filter(transaction__date__range=(
            settings.FINANCIAL_YEARS[fyear]))
