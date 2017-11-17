
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class InvoiceQuerySet(models.query.QuerySet):

    def open(self, relation=None):
        if relation:
            return self.filter(relation=relation)
        return self.filter(unpaid__gt=0)


class RelationQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(is_active=True)
