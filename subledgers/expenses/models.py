# -*- coding: utf-8 -*-
from django.db import models
from ..models import Entry


class Expense(Entry):

    relation = models.ForeignKey(
        'entities.Entity', models.PROTECT, default='', blank=True, null=True)
