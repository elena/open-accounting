# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class AccountQuerySet(models.query.QuerySet):

    def special(self):
        return self.exclude(special_account=None)

    def regular(self):
        return self.filter(special_account=None)

    def by_code(self, code):
        element, number = code.split("-")
        return self.filter(element=element, number=number).first()