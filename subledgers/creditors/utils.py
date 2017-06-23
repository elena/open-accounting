# -*- coding: utf-8 -*-
from .models import Creditor  # , CreditorInvoice



def bulk_add_creditors(s, live_run=False, tracer=False):

    obj_lines = s.split("\r\n")[1:]

    if tracer:
        print(obj_lines)

    new_objs = []

    for line in obj_lines:

        new = Creditor()

        items = [x for x in line.split("\t")]
        if tracer:
            print(items)

        new.reference, new.name, new.terms = items

        if live_run is True:
            new.save()

        new_objs.append(new)

        if tracer:
            print(new_objs)

            return new_objs


