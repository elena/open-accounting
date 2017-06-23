# -*- coding: utf-8 -*-
from django.db import models


class JournalEntry(models.Model):

    transaction = models.OneToOneField('ledgers.Transaction')

    def save(self, *args, **kwargs):
        return super(JournalEntry, self).save(*args, **kwargs)
