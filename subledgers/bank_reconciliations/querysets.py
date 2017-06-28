
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class QuerySet(models.query.QuerySet):

    def reconciled(self):
        return self.filter(bankentry__id__gt=0)

    def unreconciled(self):
        return self.exclude(bankentry__id__gt=0)
