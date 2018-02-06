# -*- coding: utf-8 -*-
from django.db import models
from ..models import Entry


class JournalEntry(Entry):

    relation = models.ForeignKey(
        'entities.Entity', models.PROTECT, default="", blank=True, null=True)

    class Meta:
        verbose_name_plural = "journal entries"
