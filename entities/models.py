# -*- coding: utf-8 -*-
""" This app is an "Address Book" of sorts.

This app should contain all "relationship" records with other companies so that
they can be referred to all in one place, regardless of how many inter-
connections there are in the relationship.

Pattern is that `Entity` is extended in each necessary app or subledger to have
additional parameters or details attached, such as debtors/creditors requiring
terms.
"""

from django.db import models

from . import utils


# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #

# Entities
#
# See detailed discussion:
# http://admin-accounting.blogspot.com.au/2017/06/subledger-generalisation-and-specifics.html

# @@TODO: Additional Entity details taiga#51

# ~~~~~~~ ======= ######################################### ======== ~~~~~~~ #


class Entity(models.Model):
    """
    ~~~ CONCRETE CLASS ~~~

    Can be used for :Organisation:-like classes.

    @@TODO Needs to have additional fields attached. taiga#51
    """
    code = models.CharField(max_length=6,
                            unique=True,
                            help_text="Unique lookup code.")

    name = models.CharField(max_length=128, blank=True, default="")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'entities'

    def __str__(self):
        return "[{code}] {name}".format(
            code=self.code,
            name=self.name)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = utils.generate_code(code=self.name)
        return super(Entity, self).save(*args, **kwargs)

    def create_related(self, relation):
        """
        Example usage:

        entity = Entity.objects.get(code="abc")
        entity.create_related(Creditor)
        """

        return relation.objects.get_or_create(entity=self)[0]
