# -*- coding: utf-8 -*-
from ..models import Entry


class Expense(Entry):
    """ `Entry` is just a `Transaction`. Generalised in case more fields are
    necessary for subjedgers.
    """
    pass
