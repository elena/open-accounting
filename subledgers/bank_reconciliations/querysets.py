
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class QuerySet(models.query.QuerySet):

    def reconciled(self):
        return self.exclude(transaction__id=None)

    def unreconciled(self):
        return self.filter(transaction__id=None)
