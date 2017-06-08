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

    Can be used for :Organisation:-like classes.
    """
    code = models.CharField(max_length=6,
                            unique=True,
                            help_text="easy lookup unique code"
    )

    name = models.CharField(max_length=128, blank=True, default="")

    def __str__(self):
        return self.code
