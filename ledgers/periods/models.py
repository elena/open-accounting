from django.db import models

from .settings import FINANCIAL_YEARS_CHOICES


class CurrentFinancialYear(models.Model):
    current_financial_year = models.CharField(
        max_length=3, choices=FINANCIAL_YEARS_CHOICES)

    def __str__(self):
        return self.current_financial_year

    def save(self, *args, **kwargs):

        # Only one current Financial Year can ever be selected.
        # (delete whatever exists)
        CurrentFinancialYear.objects.all().delete()
        super(CurrentFinancialYear, self).save(*args, **kwargs)
