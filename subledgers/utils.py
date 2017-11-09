# -*- coding: utf-8 -*-
from django.utils.module_loading import import_string

from ledgers import utils
from ledgers.models import Account


def convert_import_to_objects(dump, user, object_name=None, live=True):
    """
    ** End-to-End **

    Main function for bringing together the elements of constructing
    the list of kwargs for transactions / invoices based upon whatever is
    required for the object.

    Defining Object type by "object_name":
     Either: batch of same Object Class(using * arg `object_name`)
             or: by calling method from Object Class(eg. CreditorInvoice)
         or: column header `object_name` defining on a row-by-row basis.

     There is the choice of either preselecting what object_name of
     objects are being defined such as "CreditorInvoice" objects or
    "JournalEntry" objects.

     Alternatively each `row` should define a `object_name`.

    `user` will be added here as the individual creating this list is
    the one who should be tied to the objects.
    """

    # ** Part 1. convert dump to `list` of `dict` objects
    table = utils.tsv_to_dict(dump)

    obj_list, valid_kwargs = [], []

    for row_dict in table:

        # Copy kwargs for safety to ensure valid set/uniform keys
        kwargs = {k.lower(): v for k, v in row_dict.items()}

        kwargs['user'] = user

        """ There are a couple of different ways to provide `cls`.

        (a) `type` column provided for row in csv
        (b) `object_name` arg provided

        Alternatively done at the single object level not in scope of this
        function. Entry "make/create" methods employed below are used instead.
        """
        # `type` is particular to import as easy nomenclature for csv
        # 1. prioritise type provided for individual line
        if kwargs.get('type'):
            cls = utils.get_cls(kwargs['type'])
        # 2. fall back on `object_name` arg provided
        elif object_name:
            cls = utils.get_cls(object_name)
        else:
            raise Exception(
                "No `type` column specified for {}, unable to create objects.".format(kwargs))  # noqa
        cls = import_string(utils.get_source(cls))

        # If errors Blow up whole lot instead of processing few then blowing up
        cls().make_dicts(kwargs)

        # If doesn't blow up add to valid list
        valid_kwargs.append((cls, kwargs))

    # If whole set has been validated:
    for cls, kwargs in valid_kwargs:
        new_object = cls().save_transaction(kwargs, live=live)
        obj_list.append(new_object)

    # Returns list of generated objects/messages (depending if live or not).
    return obj_list
