# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class AccountQuerySet(models.query.QuerySet):

    def special(self):
        return self.exclude(special_account=None)

    def regular(self):
        return self.filter(special_account=None)
