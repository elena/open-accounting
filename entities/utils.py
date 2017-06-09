# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist


def generate_unique_code(queryset,
                         code=None,
                         code_field='code', # field code is kept in
                         length=6, # same as field length
                         iteration=0):

    if not code and not codify_text:
        raise NameError('Either Code or Text to Codify must be specified.')

    code = code.upper()[:length]

    if iteration > 0:
        code = '{0}{1}'.format(code[:length-1], iteration)

    try:
        queryset.get(**{code_field: code})
    except ObjectDoesNotExist:
        return code
    else:
        iteration += 1
        return generate_unique_code(queryset=queryset,
                                    code=code,
                                    code_field=code_field,
                                    length=6,
                                    iteration=iteration)
