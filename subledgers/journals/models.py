# -*- coding: utf-8 -*-
from ..models import Entry


class JournalEntry(Entry):

    class Meta:
        verbose_name_plural = "journal entries"
